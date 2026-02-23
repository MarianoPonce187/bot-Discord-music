# ============================================
# Comandos de música
# ============================================

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from utils.music_player import MusicPlayer
from utils.queue_manager import QueueManager, Song
from utils.autoplay_manager import AutoplayManager
from utils.music_controls import MusicControlView
from config import Config
import asyncio

class Music(commands.Cog):
    """Comandos de reproducción de música"""
    
    def __init__(self, bot):
        self.bot = bot
        self.autoplay = AutoplayManager()
        self.players = {}  # {guild_id: MusicPlayer}
        self.queues = {}   # {guild_id: QueueManager}
        self.autoplay = AutoplayManager()
        self.text_channels = {}
    
    def get_player(self, guild_id: int) -> MusicPlayer:
        """Obtiene o crea un reproductor para el servidor"""
        if guild_id not in self.players:
            self.players[guild_id] = MusicPlayer(None)
        return self.players[guild_id]
    
    def get_queue(self, guild_id: int) -> QueueManager:
        """Obtiene o crea una cola para el servidor"""
        if guild_id not in self.queues:
            self.queues[guild_id] = QueueManager()
            # Activar autoplay por defecto
            self.autoplay.enabled_guilds.add(guild_id)
        return self.queues[guild_id]
    
    async def play_next(self, guild_id: int):
        """Reproduce la siguiente canción en la cola"""
        
        queue = self.get_queue(guild_id)
        player = self.get_player(guild_id)
        
        last_song = player.last_played
        
        next_song = queue.get_next()
        
        autoplay_activated = False
        
        # Si no hay siguiente canción y autoplay está activo
        if not next_song and self.autoplay.is_enabled(guild_id):
            
            if last_song:
                print(f"🎵 Autoplay: Buscando canción relacionada a '{last_song.title}'...")
                related_info = await self.autoplay.get_related_song(
                    last_song.url,
                    last_song.title
                )
                
                if related_info:
                    next_song = Song(
                        url=related_info['url'],
                        title=related_info['title'],
                        duration=related_info['duration'],
                        requester=self.bot.user,
                        thumbnail=related_info.get('thumbnail')
                    )
                    autoplay_activated = True
                    print(f"✅ Autoplay: Agregando '{next_song.title}'")
                else:
                    print(f"❌ No se encontró canción relacionada")
            else:
                print(f"❌ No hay last_played para buscar relacionada")
        
        if next_song:
            
            if last_song:  # Usar last_song en vez de player.current_song
                queue.history.append(last_song)
            
            def after_playing(error):
                if error:
                    print(f"Error en reproducción: {error}")
                
                asyncio.run_coroutine_threadsafe(
                    self.play_next(guild_id),
                    self.bot.loop
                )
            
            await player.play(next_song, after_callback=after_playing)
            
            text_channel = self.text_channels.get(guild_id)
    
            if text_channel:
                try:
                    # Cambiar título según si es autoplay o no
                    if autoplay_activated:
                        title = "🔄 Autoplay - Reproduciendo ahora"
                        footer_text = "Encontrada automáticamente por Pentakill 🎸"
                    else:
                        title = "▶️ Reproduciendo ahora"
                        footer_text = f"Solicitada por {next_song.requester.name}"

                    embed = discord.Embed(
                        title=title,
                        description=f"**{next_song.title}**",
                        color=Config.COLOR_PRIMARY
                    )
                    embed.add_field(
                        name="⏱️ Duración", 
                        value=self._format_duration(next_song.duration), 
                        inline=True
                    )
                    embed.set_footer(text=footer_text)
                    if next_song.thumbnail:
                        embed.set_thumbnail(url=next_song.thumbnail)

                    # Agregar botones
                    view = MusicControlView(self, guild_id)
                    message = await text_channel.send(embed=embed, view=view)
                    view.message = message
                except Exception as e:
                    print(f"❌ Error al enviar mensaje: {e}")
            else:
                print(f"❌ No hay text_channel guardado")
        else:
            print(f"📭 Cola vacía en servidor {guild_id}, no hay canción para reproducir")
    
    @app_commands.command(name="join", description="🎸 Pentakill se une a tu canal de voz")
    async def join(self, interaction: discord.Interaction):
        """Comando para unirse al canal de voz"""
        
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Debes estar en un canal de voz para usar este comando!",
                ephemeral=True
            )
            return
        
        # GUARDAR CANAL DE TEXTO
        self.text_channels[interaction.guild.id] = interaction.channel
        
        channel = interaction.user.voice.channel
        player = self.get_player(interaction.guild.id)
        
        success = await player.connect(channel)
        
        if success:
            embed = discord.Embed(
                title="🎸 Pentakill ha entrado al escenario!",
                description=f"Conectado a **{channel.name}**",
                color=Config.COLOR_SUCCESS
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                "❌ No pude conectarme al canal de voz",
                ephemeral=True
            )
    
    @app_commands.command(name="leave", description="👋 Pentakill abandona el canal de voz")
    async def leave(self, interaction: discord.Interaction):
        """Comando para salir del canal de voz"""
        
        player = self.get_player(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        
        if not player.is_connected():
            await interaction.response.send_message(
                "❌ No estoy en ningún canal de voz!",
                ephemeral=True
            )
            return
        
        player.stop()
        queue.clear()
        await player.disconnect()
        
        embed = discord.Embed(
            title="👋 Pentakill ha dejado el escenario",
            description="Gracias por el concierto!",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="play", description="▶️ Reproduce una canción")
    @app_commands.describe(song="URL de YouTube o nombre de la canción")
    async def play(self, interaction: discord.Interaction, song: str):
        """Comando para reproducir música"""
        
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Debes estar en un canal de voz!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # GUARDAR CANAL DE TEXTO
        self.text_channels[interaction.guild.id] = interaction.channel
        
        channel = interaction.user.voice.channel
        player = self.get_player(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        
        if not player.is_connected():
            await player.connect(channel)
        
        info = await player.extract_info(song)
        
        if not info:
            await interaction.followup.send("❌ No pude encontrar esa canción")
            return
        
        song_obj = Song(
            url=info.get('webpage_url', song),
            title=info.get('title', 'Título desconocido'),
            duration=info.get('duration', 0),
            requester=interaction.user,
            thumbnail=info.get('thumbnail')
        )
        
        queue.add(song_obj)
        
        if not player.is_playing() and not player.is_paused():
            await self.play_next(interaction.guild.id)
            
            embed = discord.Embed(
                title="▶️ Reproduciendo ahora",
                description=f"**{song_obj.title}**",
                color=Config.COLOR_PRIMARY
            )
            embed.add_field(name="⏱️ Duración", value=self._format_duration(song_obj.duration), inline=True)
            embed.set_footer(text=f"Solicitada por {song_obj.requester.name}")
            if song_obj.thumbnail:
                embed.set_thumbnail(url=song_obj.thumbnail)
            
            view = MusicControlView(self, interaction.guild.id)
            message = await interaction.followup.send(embed=embed, view=view)
            view.message = message
        else:
            embed = discord.Embed(
                title="➕ Agregada a la cola",
                description=f"**{song_obj.title}**",
                color=Config.COLOR_INFO
            )
            embed.add_field(name="Posición", value=f"#{queue.size()}")
            embed.set_footer(text=f"Solicitada por {song_obj.requester.name}")
            
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="pause", description="⏸️ Pausa la reproducción")
    async def pause(self, interaction: discord.Interaction):
        """Pausa la música"""
        
        player = self.get_player(interaction.guild.id)
        
        if not player.is_playing():
            await interaction.response.send_message(
                "❌ No hay nada reproduciéndose!",
                ephemeral=True
            )
            return
        
        player.pause()
        
        embed = discord.Embed(
            title="⏸️ Música pausada",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="resume", description="▶️ Reanuda la reproducción")
    async def resume(self, interaction: discord.Interaction):
        """Reanuda la música"""
        
        player = self.get_player(interaction.guild.id)
        
        if not player.is_paused():
            await interaction.response.send_message(
                "❌ La música no está pausada!",
                ephemeral=True
            )
            return
        
        player.resume()
        
        embed = discord.Embed(
            title="▶️ Música reanudada",
            color=Config.COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="skip", description="⏭️ Salta a la siguiente canción")
    async def skip(self, interaction: discord.Interaction):
        """Salta la canción actual"""
        
        player = self.get_player(interaction.guild.id)
        
        if not player.is_playing():
            await interaction.response.send_message(
                "❌ No hay nada reproduciéndose!",
                ephemeral=True
            )
            return
        
        # GUARDAR CANAL DE TEXTO
        self.text_channels[interaction.guild.id] = interaction.channel
        
        # Solo detener, NO llamar queue.skip() para que autoplay funcione
        player.stop()
        
        embed = discord.Embed(
            title="⏭️ Canción saltada",
            description="Reproduciendo siguiente...",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="previous", description="⏮️ Vuelve a la canción anterior")
    async def previous(self, interaction: discord.Interaction):
        """Vuelve a reproducir la canción anterior"""
        
        player = self.get_player(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        
        if not player.is_connected():
            await interaction.response.send_message(
                "❌ No estoy en ningún canal de voz!",
                ephemeral=True
            )
            return
        
        previous_song = queue.get_previous()
        
        if not previous_song:
            await interaction.response.send_message(
                "❌ No hay canción anterior en el historial!",
                ephemeral=True
            )
            return
        
        # Detener la actual y reproducir anterior
        player.stop()
        
        embed = discord.Embed(
            title="⏮️ Volviendo a canción anterior",
            description=f"**{previous_song.title}**",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stop", description="⏹️ Detiene la música y limpia la lista")
    async def stop(self, interaction: discord.Interaction):
        """Detiene toda la reproducción"""
        
        player = self.get_player(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        
        player.stop()
        queue.clear()
        
        embed = discord.Embed(
            title="⏹️ Reproducción detenida",
            description="lista limpiada",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="lista", description="📋 Muestra la lista de reproducción")
    async def queue(self, interaction: discord.Interaction, page: int = 1):
        """Muestra la lista de reproducción con paginación"""
        
        queue = self.get_queue(interaction.guild.id)
        player = self.get_player(interaction.guild.id)
        
        if queue.is_empty() and not player.current_song:
            await interaction.response.send_message(
                "❌ No hay canciones en la lista!",
                ephemeral=True
            )
            return
        
        # Configurar paginación
        songs_per_page = 10
        queue_list = queue.get_queue()
        total_pages = max(1, (len(queue_list) + songs_per_page - 1) // songs_per_page)
        
        if page < 1 or page > total_pages:
            page = 1
        
        start_idx = (page - 1) * songs_per_page
        end_idx = start_idx + songs_per_page
        
        # Crear embed
        embed = discord.Embed(
            title="🎵 lista de Reproducción",
            color=Config.COLOR_PRIMARY
        )
        
        # Canción actual
        if player.current_song:
            current = player.current_song
            embed.add_field(
                name="▶️ Reproduciendo ahora",
                value=f"**{current.title}**\nSolicitada por {current.requester.mention}",
                inline=False
            )
        
        # lista
        if queue_list:
            queue_text = ""
            for i, song in enumerate(queue_list[start_idx:end_idx], start=start_idx + 1):
                duration = self._format_duration(song.duration)
                queue_text += f"`{i}.` **{song.title}** [{duration}]\n   Solicitada por {song.requester.mention}\n\n"
            
            embed.add_field(
                name=f"📋 Próximas canciones ({len(queue_list)} en lista)",
                value=queue_text or "lista vacía",
                inline=False
            )
            
            # Footer con paginación
            embed.set_footer(text=f"Página {page}/{total_pages} • {len(queue_list)} canciones restantes")
        else:
            embed.add_field(
                name="📋 Próximas canciones",
                value="lista vacía",
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="nowplaying", description="🎵 Muestra la canción actual")
    async def nowplaying(self, interaction: discord.Interaction):
        """Muestra información de la canción que se está reproduciendo"""
        
        player = self.get_player(interaction.guild.id)
        
        if not player.current_song:
            await interaction.response.send_message(
                "❌ No hay nada reproduciéndose!",
                ephemeral=True
            )
            return
        
        song = player.current_song
        duration = self._format_duration(song.duration)
        queue = self.get_queue(interaction.guild.id)
        
        embed = discord.Embed(
            title="🎵 Reproduciendo ahora",
            description=f"**{song.title}**",
            color=Config.COLOR_PRIMARY,
            url=song.url  # Hace el título clickeable
        )
        
        embed.add_field(name="⏱️ Duración", value=duration, inline=True)
        embed.add_field(name="🔊 Volumen", value=f"{int(player.volume * 100)}%", inline=True)
        
        # Status del modo loop
        queue = self.get_queue(interaction.guild.id)
        if queue.loop:
            embed.add_field(name="🔁 Loop", value="Canción", inline=True)
        elif queue.loop_queue:
            embed.add_field(name="🔁 Loop", value="lista", inline=True)
        else:
            embed.add_field(name="🔁 Loop", value="Desactivado", inline=True)
        
        embed.add_field(name="👤 Solicitada por", value=song.requester.mention, inline=False)
        
        if song.thumbnail:
            embed.set_image(url=song.thumbnail)  # Imagen más grande
        
        # Mostrar autoplay status
        if self.autoplay.is_enabled(interaction.guild.id):
            embed.set_footer(text="🔄 Autoplay: Activado")
            
        # AGREGAR BOTONES
        view = MusicControlView(self, interaction.guild.id)
        message = await interaction.response.send_message(embed=embed, view=view)
        view.message = await message.original_response()
    
    @app_commands.command(name="clear", description="🗑️ Limpia toda la lista de reproducción")
    async def clear(self, interaction: discord.Interaction):
        """Limpia la lista pero mantiene la canción actual"""
        
        queue = self.get_queue(interaction.guild.id)
        
        if queue.is_empty():
            await interaction.response.send_message(
                "❌ La lista ya está vacía!",
                ephemeral=True
            )
            return
        
        songs_removed = queue.size()
        queue.clear()
        
        embed = discord.Embed(
            title="🗑️ lista limpiada",
            description=f"Se eliminaron **{songs_removed}** canciones de la lista",
            color=Config.COLOR_INFO
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="remove", description="❌ Elimina una canción de la lista")
    @app_commands.describe(position="Posición de la canción en la lista (usa /queue para ver)")
    async def remove(self, interaction: discord.Interaction, position: int):
        """Elimina una canción específica de la lista"""
        
        queue = self.get_queue(interaction.guild.id)
        
        if queue.is_empty():
            await interaction.response.send_message(
                "❌ La lista está vacía!",
                ephemeral=True
            )
            return
        
        # Ajustar índice (usuario ve 1-indexed, internamente es 0-indexed)
        song = queue.remove(position - 1)
        
        if song:
            embed = discord.Embed(
                title="❌ Canción eliminada",
                description=f"**{song.title}** fue eliminada de la lista",
                color=Config.COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ Posición inválida! La lista tiene {queue.size()} canciones",
                ephemeral=True
            )
    
    @app_commands.command(name="playnow", description="⚡ Reproduce una canción inmediatamente")
    @app_commands.describe(song="URL de YouTube o nombre de la canción")
    async def playnow(self, interaction: discord.Interaction, song: str):
        """Reproduce una canción saltando la cola actual"""
        
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Debes estar en un canal de voz!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # GUARDAR CANAL DE TEXTO
        self.text_channels[interaction.guild.id] = interaction.channel
        
        channel = interaction.user.voice.channel
        player = self.get_player(interaction.guild.id)
        queue = self.get_queue(interaction.guild.id)
        
        if not player.is_connected():
            await player.connect(channel)
        
        info = await player.extract_info(song)
        
        if not info:
            await interaction.followup.send("❌ No pude encontrar esa canción")
            return
        
        song_obj = Song(
            url=info.get('webpage_url', song),
            title=info.get('title', 'Título desconocido'),
            duration=info.get('duration', 0),
            requester=interaction.user,
            thumbnail=info.get('thumbnail')
        )
        
        if player.is_playing():
            player.stop()
            queue.add_next(song_obj)
            
            embed = discord.Embed(
                title="⚡ Reproduciendo ahora",
                description=f"**{song_obj.title}**\nLa canción anterior fue agregada al principio de la cola",
                color=Config.COLOR_PRIMARY
            )
        else:
            queue.add_next(song_obj)
            await self.play_next(interaction.guild.id)
            
            embed = discord.Embed(
                title="⚡ Reproduciendo ahora",
                description=f"**{song_obj.title}**",
                color=Config.COLOR_PRIMARY
            )
        
        embed.set_footer(text=f"Solicitada por {song_obj.requester.name}")
        if song_obj.thumbnail:
            embed.set_thumbnail(url=song_obj.thumbnail)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="shuffle", description="🔀 Mezcla la lista aleatoriamente")
    async def shuffle(self, interaction: discord.Interaction):
        """Mezcla el orden de las canciones en la lista"""
        
        import random
        
        queue = self.get_queue(interaction.guild.id)
        
        if queue.is_empty():
            await interaction.response.send_message(
                "❌ La lista está vacía!",
                ephemeral=True
            )
            return
        
        if queue.size() < 2:
            await interaction.response.send_message(
                "❌ Necesitas al menos 2 canciones en la lista para mezclar!",
                ephemeral=True
            )
            return
        
        # Mezclar la lista
        queue_list = list(queue.queue)
        random.shuffle(queue_list)
        queue.queue = type(queue.queue)(queue_list)
        
        embed = discord.Embed(
            title="🔀 lista mezclada",
            description=f"**{queue.size()}** canciones fueron mezcladas aleatoriamente",
            color=Config.COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="loop", description="🔁 Activa/desactiva la repetición de la canción actual")
    async def loop(self, interaction: discord.Interaction):
        """Alterna el modo de repetición de la canción actual"""
        
        queue = self.get_queue(interaction.guild.id)
        queue.loop = not queue.loop
        
        if queue.loop:
            embed = discord.Embed(
                title="🔁 Repetición activada",
                description="La canción actual se repetirá",
                color=Config.COLOR_SUCCESS
            )
        else:
            embed = discord.Embed(
                title="🔁 Repetición desactivada",
                description="Reproducción normal",
                color=Config.COLOR_INFO
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="looplista", description="🔁 Activa/desactiva la repetición de toda la lista")
    async def loopqueue(self, interaction: discord.Interaction):
        """Alterna el modo de repetición de toda la lista"""
        
        queue = self.get_queue(interaction.guild.id)
        queue.loop_queue = not queue.loop_queue
        
        if queue.loop_queue:
            embed = discord.Embed(
                title="🔁 Repetición de lista activada",
                description="Toda la lista se repetirá infinitamente",
                color=Config.COLOR_SUCCESS
            )
        else:
            embed = discord.Embed(
                title="🔁 Repetición de lista desactivada",
                description="Reproducción normal",
                color=Config.COLOR_INFO
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="volume", description="🔊 Ajusta el volumen del bot")
    @app_commands.describe(level="Nivel de volumen (0-100)")
    async def volume(self, interaction: discord.Interaction, level: int):
        """Ajusta el volumen de reproducción"""
        
        player = self.get_player(interaction.guild.id)
        
        if not player.is_connected():
            await interaction.response.send_message(
                "❌ No estoy conectado a un canal de voz!",
                ephemeral=True
            )
            return
        
        if level < 0 or level > 100:
            await interaction.response.send_message(
                "❌ El volumen debe estar entre 0 y 100!",
                ephemeral=True
            )
            return
        
        player.set_volume(level / 100.0)
        
        # Emoji según el nivel
        if level == 0:
            emoji = "🔇"
        elif level < 30:
            emoji = "🔉"
        elif level < 70:
            emoji = "🔊"
        else:
            emoji = "📢"
        
        embed = discord.Embed(
            title=f"{emoji} Volumen ajustado",
            description=f"Volumen establecido a **{level}%**",
            color=Config.COLOR_SUCCESS
        )
        await interaction.response.send_message(embed=embed)
    
    # Función helper para formatear duración
    def _format_duration(self, seconds: int) -> str:
        """Formatea segundos a MM:SS o HH:MM:SS"""
        if seconds == 0:
            return "En vivo"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes}:{secs:02d}"
        
    @app_commands.command(name="autoplay", description="🔄 Activa/desactiva la reproducción automática")
    async def autoplay_toggle(self, interaction: discord.Interaction):
        """Activa o desactiva el modo autoplay"""
        
        is_enabled = self.autoplay.toggle_autoplay(interaction.guild.id)
        
        if is_enabled:
            embed = discord.Embed(
                title="🔄 Autoplay activado",
                description=(
                    "Cuando la lista esté vacía, Pentakill buscará automáticamente "
                    "música relacionada para seguir rockeando! 🎸\n\n"
                    "**Cómo funciona:**\n"
                    "• Busca videos relacionados en YouTube\n"
                    "• Si no encuentra, busca del mismo artista\n"
                    "• Mantiene la música sonando sin parar!"
                ),
                color=Config.COLOR_SUCCESS
            )
            embed.set_footer(text="Usa /autoplay nuevamente para desactivar")
        else:
            embed = discord.Embed(
                title="🔄 Autoplay desactivado",
                description="La reproducción automática ha sido desactivada",
                color=Config.COLOR_INFO
            )
        
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="help", description="❓ Muestra todos los comandos disponibles")
    async def help_command(self, interaction: discord.Interaction):
        """Muestra la lista completa de comandos"""
        
        embed = discord.Embed(
            title="🎸 Pentakill - Comandos",
            description="Bot de música para Discord",
            color=Config.COLOR_PRIMARY
        )
        
        # Comandos básicos
        embed.add_field(
            name="🎵 Reproducción Básica",
            value=(
                "`/join` - Une el bot al canal de voz\n"
                "`/leave` - Desconecta el bot\n"
                "`/play [canción]` - Reproduce una canción\n"
                "`/playnow [canción]` - Reproduce inmediatamente\n"
                "`/pause` - Pausa la reproducción\n"
                "`/resume` - Reanuda la reproducción\n"
                "`/skip` - Salta a la siguiente canción\n"
                "`/stop` - Detiene y limpia la lista"
            ),
            inline=False
        )
        
        # Control de lista
        embed.add_field(
            name="📋 Control de lista",
            value=(
                "`/lista [página]` - Muestra la lista actual\n"
                "`/nowplaying` - Info de la canción actual\n"
                "`/clear` - Limpia la lista\n"
                "`/remove [pos]` - Quita canción de la lista\n"
                "`/shuffle` - Mezcla la lista\n"
                "`/loop` - Repite la canción actual\n"
                "`/looplista` - Repite toda la lista"
            ),
            inline=False
        )
        
        # Playlists
        embed.add_field(
            name="📁 Playlists Guardadas",
            value=(
                "`/createlist [nombre]` - Crea una playlist\n"
                "`/mylists` - Muestra tus playlists\n"
                "`/showlist [nombre]` - Ver canciones\n"
                "`/addtolist [nombre] [canción]` - Agrega canción\n"
                "`/removefromlist [nombre] [pos]` - Quita canción\n"
                "`/playplaylist [nombre]` - Reproduce playlist\n"
                "`/renamelist [viejo] [nuevo]` - Renombra\n"
                "`/deletelist [nombre]` - Elimina playlist\n"
                "`/clearlist [nombre]` - Limpia playlist"
            ),
            inline=False
        )
        
        # Extras
        embed.add_field(
            name="⚙️ Configuración",
            value=(
                "`/volume [0-100]` - Ajusta el volumen\n"
                "`/autoplay` - Reproducción automática\n"
                "`/help` - Muestra este mensaje"
            ),
            inline=False
        )
        
        embed.set_footer(text="🎸 Pentakill | Hecho con ❤️ para rockear")
        embed.set_thumbnail(url=self.bot.user.avatar.url if self.bot.user.avatar else None)
        
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Music(bot))