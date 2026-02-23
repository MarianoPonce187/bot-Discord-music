
# ============================================
# Lógica de reproducción de música
# ============================================

import discord
import yt_dlp
import asyncio
from typing import Optional
from config import Config

class MusicPlayer:
    """Maneja la reproducción de música en un servidor"""
    
    def __init__(self, ctx):
        self.ctx = ctx
        self.voice_client: Optional[discord.VoiceClient] = None
        self.current_song = None
        self.last_played = None
        self.volume = 0.25
    
    async def connect(self, channel: discord.VoiceChannel) -> bool:
        """Conecta el bot al canal de voz"""
        try:
            if self.voice_client and self.voice_client.is_connected():
                if self.voice_client.channel != channel:
                    await self.voice_client.move_to(channel)
            else:
                self.voice_client = await channel.connect()
            return True
        except Exception as e:
            print(f"Error al conectar: {e}")
            return False
    
    async def disconnect(self):
        """Desconecta el bot del canal de voz"""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
    
    def is_connected(self) -> bool:
        """Verifica si el bot está conectado a un canal de voz"""
        return self.voice_client is not None and self.voice_client.is_connected()
    
    def is_playing(self) -> bool:
        """Verifica si hay música reproduciéndose"""
        return self.voice_client and self.voice_client.is_playing()
    
    def is_paused(self) -> bool:
        """Verifica si la música está en pausa"""
        return self.voice_client and self.voice_client.is_paused()
    
    async def extract_info(self, query: str) -> Optional[dict]:
        """Extrae información de la URL o búsqueda usando yt-dlp"""
        try:
            loop = asyncio.get_event_loop()
            
            with yt_dlp.YoutubeDL(Config.YT_DLP_OPTIONS) as ydl:
                # Si no es URL, buscar en YouTube
                if not query.startswith('http'):
                    query = f"ytsearch:{query}"
                
                info = await loop.run_in_executor(
                    None, 
                    lambda: ydl.extract_info(query, download=False)
                )
                
                # Si es una búsqueda, tomar el primer resultado
                if 'entries' in info:
                    info = info['entries'][0]
                
                return info
        except Exception as e:
            print(f"Error al extraer info: {e}")
            return None
    
    async def play(self, song, after_callback=None):
        """Reproduce una canción"""
        if not self.voice_client:
            return False
        
        try:
            # Guardar la canción anterior antes de cambiar
            if self.current_song:
                self.last_played = self.current_song
            
            self.current_song = song
            
            # Extraer información actualizada (URLs expiran)
            info = await self.extract_info(song.url)
            if not info:
                return False
            
            audio_url = info['url']
            
            # Crear fuente de audio
            source = discord.FFmpegPCMAudio(audio_url, **Config.FFMPEG_OPTIONS)
            source = discord.PCMVolumeTransformer(source, volume=self.volume)
            
            # Reproducir
            self.voice_client.play(source, after=after_callback)
            
            return True
        except Exception as e:
            print(f"Error al reproducir: {e}")
            return False
    
    def pause(self):
        """Pausa la reproducción"""
        if self.voice_client and self.voice_client.is_playing():
            self.voice_client.pause()
    
    def resume(self):
        """Reanuda la reproducción"""
        if self.voice_client and self.voice_client.is_paused():
            self.voice_client.resume()
    
    def stop(self):
        """Detiene la reproducción"""
        if self.voice_client:
            # Guardar current_song como last_played antes de borrarla
            if self.current_song:
                self.last_played = self.current_song
            
            self.voice_client.stop()
            self.current_song = None
    
    def set_volume(self, volume: float):
        """Ajusta el volumen (0.0 a 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        if self.voice_client and self.voice_client.source:
            self.voice_client.source.volume = self.volume
