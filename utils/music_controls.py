
import discord
from discord.ui import Button, View
from typing import Optional
import asyncio

class MusicControlView(View):
    """Vista con botones de control de música"""
    
    def __init__(self, music_cog, guild_id: int, timeout: float = 900):  # 15 minutos
        super().__init__(timeout=timeout)
        self.music_cog = music_cog
        self.guild_id = guild_id
        self.message: Optional[discord.Message] = None
    
    @discord.ui.button(label="Anterior", style=discord.ButtonStyle.secondary, emoji="⏮️")
    async def previous_button(self, interaction: discord.Interaction, button: Button):
        """Botón para volver a la canción anterior"""
        player = self.music_cog.get_player(self.guild_id)
        queue = self.music_cog.get_queue(self.guild_id)
        
        if not player.is_connected():
            await interaction.response.send_message("❌ No estoy en un canal de voz!", ephemeral=True)
            return
        
        # Guardar canal de texto
        self.music_cog.text_channels[self.guild_id] = interaction.channel
        
        previous_song = queue.get_previous()
        
        if not previous_song:
            await interaction.response.send_message("❌ No hay canción anterior!", ephemeral=True)
            return
        
        # Detener canción actual y reproducir anterior
        player.stop()
        await interaction.response.send_message("⏮️ Volviendo a la canción anterior...", ephemeral=True)
    
    @discord.ui.button(label="Pausa/Resume", style=discord.ButtonStyle.primary, emoji="⏸️")
    async def pause_resume_button(self, interaction: discord.Interaction, button: Button):
        """Botón para pausar/reanudar"""
        player = self.music_cog.get_player(self.guild_id)
        
        if not player.is_connected():
            await interaction.response.send_message("❌ No estoy en un canal de voz!", ephemeral=True)
            return
        
        if player.is_playing():
            player.pause()
            await interaction.response.send_message("⏸️ Música pausada", ephemeral=True)
        elif player.is_paused():
            player.resume()
            await interaction.response.send_message("▶️ Música reanudada", ephemeral=True)
        else:
            await interaction.response.send_message("❌ No hay nada reproduciéndose!", ephemeral=True)
    
    @discord.ui.button(label="Siguiente", style=discord.ButtonStyle.secondary, emoji="⏭️")
    async def skip_button(self, interaction: discord.Interaction, button: Button):
        """Botón para saltar canción"""
        player = self.music_cog.get_player(self.guild_id)
        
        if not player.is_playing():
            await interaction.response.send_message("❌ No hay nada reproduciéndose!", ephemeral=True)
            return
        
        # Guardar canal de texto - ESTO ES LO MÁS IMPORTANTE
        self.music_cog.text_channels[self.guild_id] = interaction.channel
        
        # Solo detener para que autoplay funcione
        player.stop()
        await interaction.response.send_message("⏭️ Saltando canción...", ephemeral=True)
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️")
    async def stop_button(self, interaction: discord.Interaction, button: Button):
        """Botón para detener reproducción"""
        player = self.music_cog.get_player(self.guild_id)
        queue = self.music_cog.get_queue(self.guild_id)
        
        player.stop()
        queue.clear()
        await interaction.response.send_message("⏹️ Reproducción detenida", ephemeral=True)
    
    async def on_timeout(self):
        """Cuando los botones expiran"""
        if self.message:
            try:
                # Deshabilitar botones
                for item in self.children:
                    item.disabled = True
                await self.message.edit(view=self)
            except:
                pass