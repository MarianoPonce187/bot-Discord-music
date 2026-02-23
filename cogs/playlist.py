# ============================================
# ARCHIVO: cogs/playlist.py
# Comandos para gestión de playlists
# ============================================

import discord
from discord import app_commands
from discord.ext import commands
from database.db_manager import DatabaseManager
from utils.queue_manager import Song
from config import Config

class Playlist(commands.Cog):
    """Comandos para gestión de playlists guardadas"""
    
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager(Config.DB_PATH)
    
    @app_commands.command(name="createlist", description="📝 Crea una nueva playlist")
    @app_commands.describe(name="Nombre de la playlist")
    async def createlist(self, interaction: discord.Interaction, name: str):
        """Crea una nueva playlist"""
        
        # Validar nombre
        if len(name) > 50:
            await interaction.response.send_message(
                "❌ El nombre de la playlist no puede tener más de 50 caracteres!",
                ephemeral=True
            )
            return
        
        if len(name) < 2:
            await interaction.response.send_message(
                "❌ El nombre de la playlist debe tener al menos 2 caracteres!",
                ephemeral=True
            )
            return
        
        # Crear playlist
        playlist_id = self.db.create_playlist(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if playlist_id:
            embed = discord.Embed(
                title="📝 Playlist creada",
                description=f"**{name}** fue creada exitosamente!",
                color=Config.COLOR_SUCCESS
            )
            embed.set_footer(text=f"ID: {playlist_id}")
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ Ya tienes una playlist llamada **{name}**!",
                ephemeral=True
            )
    
    @app_commands.command(name="deletelist", description="🗑️ Elimina una playlist")
    @app_commands.describe(name="Nombre de la playlist a eliminar")
    async def deletelist(self, interaction: discord.Interaction, name: str):
        """Elimina una playlist"""
        
        success = self.db.delete_playlist(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title="🗑️ Playlist eliminada",
                description=f"**{name}** fue eliminada permanentemente",
                color=Config.COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
    
    @app_commands.command(name="mylists", description="📚 Muestra todas tus playlists")
    async def mylists(self, interaction: discord.Interaction):
        """Muestra todas las playlists del usuario"""
        
        playlists = self.db.get_user_playlists(
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlists:
            await interaction.response.send_message(
                "❌ No tienes ninguna playlist aún! Crea una con `/createlist`",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title=f"📚 Playlists de {interaction.user.name}",
            description=f"Total: {len(playlists)} playlist(s)",
            color=Config.COLOR_PRIMARY
        )
        
        for name, song_count, created_at in playlists:
            # Formatear fecha
            date_str = created_at.split()[0] if ' ' in created_at else created_at
            
            embed.add_field(
                name=f"🎵 {name}",
                value=f"📊 {song_count} canción(es)\n📅 Creada: {date_str}",
                inline=True
            )
        
        embed.set_footer(text="Usa /showlist [nombre] para ver las canciones")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="showlist", description="👁️ Muestra las canciones de una playlist")
    @app_commands.describe(
        name="Nombre de la playlist",
        page="Número de página (10 canciones por página)"
    )
    async def showlist(self, interaction: discord.Interaction, name: str, page: int = 1):
        """Muestra las canciones de una playlist con paginación"""
        
        # Obtener ID de la playlist
        playlist_id = self.db.get_playlist_id(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlist_id:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
            return
        
        # Obtener canciones
        songs = self.db.get_playlist_songs(playlist_id)
        
        if not songs:
            embed = discord.Embed(
                title=f"🎵 {name}",
                description="Esta playlist está vacía. Usa `/addtolist` para agregar canciones!",
                color=Config.COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Configurar paginación
        songs_per_page = 10
        total_pages = max(1, (len(songs) + songs_per_page - 1) // songs_per_page)
        
        if page < 1 or page > total_pages:
            page = 1
        
        start_idx = (page - 1) * songs_per_page
        end_idx = start_idx + songs_per_page
        
        # Crear embed
        embed = discord.Embed(
            title=f"🎵 {name}",
            description=f"Total: {len(songs)} canción(es)",
            color=Config.COLOR_PRIMARY
        )
        
        songs_text = ""
        for url, title, duration, thumbnail, position in songs[start_idx:end_idx]:
            duration_str = self._format_duration(duration)
            songs_text += f"`{position}.` **{title}** [{duration_str}]\n"
        
        embed.add_field(
            name="📋 Canciones",
            value=songs_text,
            inline=False
        )
        
        embed.set_footer(text=f"Página {page}/{total_pages} • Usa /playlist {name} para reproducir")
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="addtolist", description="➕ Agrega una canción a una playlist")
    @app_commands.describe(
        name="Nombre de la playlist",
        query="URL de YouTube o nombre de la canción"
    )
    async def addtolist(self, interaction: discord.Interaction, name: str, query: str):
        """Agrega una canción a una playlist"""
        
        # Obtener ID de la playlist
        playlist_id = self.db.get_playlist_id(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlist_id:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Importar MusicPlayer para extraer info
        from utils.music_player import MusicPlayer
        player = MusicPlayer(None)
        
        # Extraer información de la canción
        info = await player.extract_info(query)
        
        if not info:
            await interaction.followup.send("❌ No pude encontrar esa canción")
            return
        
        # Agregar a la base de datos
        success = self.db.add_song_to_playlist(
            playlist_id=playlist_id,
            url=info.get('webpage_url', query),
            title=info.get('title', 'Título desconocido'),
            duration=info.get('duration', 0),
            thumbnail=info.get('thumbnail')
        )
        
        if success:
            embed = discord.Embed(
                title="➕ Canción agregada",
                description=f"**{info.get('title')}** fue agregada a **{name}**",
                color=Config.COLOR_SUCCESS
            )
            if info.get('thumbnail'):
                embed.set_thumbnail(url=info.get('thumbnail'))
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Error al agregar la canción a la playlist")
    
    @app_commands.command(name="removefromlist", description="➖ Quita una canción de una playlist")
    @app_commands.describe(
        name="Nombre de la playlist",
        position="Posición de la canción (usa /showlist para ver)"
    )
    async def removefromlist(self, interaction: discord.Interaction, name: str, position: int):
        """Elimina una canción de una playlist"""
        
        # Obtener ID de la playlist
        playlist_id = self.db.get_playlist_id(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlist_id:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
            return
        
        # Eliminar canción
        success = self.db.remove_song_from_playlist(playlist_id, position)
        
        if success:
            embed = discord.Embed(
                title="➖ Canción eliminada",
                description=f"La canción en la posición **{position}** fue eliminada de **{name}**",
                color=Config.COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ No hay ninguna canción en la posición **{position}**!",
                ephemeral=True
            )
    
    @app_commands.command(name="clearlist", description="🗑️ Elimina todas las canciones de una playlist")
    @app_commands.describe(name="Nombre de la playlist")
    async def clearlist(self, interaction: discord.Interaction, name: str):
        """Limpia todas las canciones de una playlist"""
        
        # Obtener ID de la playlist
        playlist_id = self.db.get_playlist_id(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlist_id:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
            return
        
        success = self.db.clear_playlist(playlist_id)
        
        if success:
            embed = discord.Embed(
                title="🗑️ Playlist limpiada",
                description=f"Todas las canciones de **{name}** fueron eliminadas",
                color=Config.COLOR_INFO
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Error al limpiar la playlist", ephemeral=True)
    
    @app_commands.command(name="playplaylist", description="▶️ Reproduce una playlist completa")
    @app_commands.describe(name="Nombre de la playlist")
    async def playplaylist(self, interaction: discord.Interaction, name: str):
        """Carga y reproduce una playlist completa"""
        
        # Verificar que el usuario esté en un canal de voz
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ Debes estar en un canal de voz!",
                ephemeral=True
            )
            return
        
        # Obtener ID de la playlist
        playlist_id = self.db.get_playlist_id(
            name=name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if not playlist_id:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{name}**!",
                ephemeral=True
            )
            return
        
        # Obtener canciones
        songs = self.db.get_playlist_songs(playlist_id)
        
        if not songs:
            await interaction.response.send_message(
                f"❌ La playlist **{name}** está vacía!",
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        
        # Obtener player y queue del cog de música
        music_cog = self.bot.get_cog('Music')
        if not music_cog:
            await interaction.followup.send("❌ Error: Sistema de música no disponible")
            return
        
        player = music_cog.get_player(interaction.guild.id)
        queue = music_cog.get_queue(interaction.guild.id)
        
        # Conectar al canal de voz
        channel = interaction.user.voice.channel
        if not player.is_connected():
            await player.connect(channel)
        
        # Agregar todas las canciones a la lista
        songs_added = 0
        for url, title, duration, thumbnail, position in songs:
            song = Song(
                url=url,
                title=title,
                duration=duration,
                requester=interaction.user,
                thumbnail=thumbnail
            )
            queue.add(song)
            songs_added += 1
        
        # Iniciar reproducción si no está reproduciendo
        if not player.is_playing() and not player.is_paused():
            await music_cog.play_next(interaction.guild.id)
        
        embed = discord.Embed(
            title=f"▶️ Reproduciendo playlist: {name}",
            description=f"Se agregaron **{songs_added}** canciones a la lista",
            color=Config.COLOR_SUCCESS
        )
        embed.set_footer(text=f"Solicitada por {interaction.user.name}")
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="renamelist", description="✏️ Renombra una playlist")
    @app_commands.describe(
        old_name="Nombre actual de la playlist",
        new_name="Nuevo nombre para la playlist"
    )
    async def renamelist(self, interaction: discord.Interaction, old_name: str, new_name: str):
        """Renombra una playlist"""
        
        # Validar nuevo nombre
        if len(new_name) > 50:
            await interaction.response.send_message(
                "❌ El nuevo nombre no puede tener más de 50 caracteres!",
                ephemeral=True
            )
            return
        
        if len(new_name) < 2:
            await interaction.response.send_message(
                "❌ El nuevo nombre debe tener al menos 2 caracteres!",
                ephemeral=True
            )
            return
        
        success = self.db.rename_playlist(
            old_name=old_name,
            new_name=new_name,
            guild_id=interaction.guild.id,
            user_id=interaction.user.id
        )
        
        if success:
            embed = discord.Embed(
                title="✏️ Playlist renombrada",
                description=f"**{old_name}** ahora se llama **{new_name}**",
                color=Config.COLOR_SUCCESS
            )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(
                f"❌ No tienes ninguna playlist llamada **{old_name}** o **{new_name}** ya existe!",
                ephemeral=True
            )
    
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


async def setup(bot):
    await bot.add_cog(Playlist(bot))