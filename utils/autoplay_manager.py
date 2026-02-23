
import yt_dlp
import asyncio
import random
from typing import Optional, Dict
from config import Config

class AutoplayManager:
    """Gestiona la reproducción automática de música relacionada"""
    
    def __init__(self):
        self.enabled_guilds = set()  # Servidores con autoplay activo
    
    def toggle_autoplay(self, guild_id: int) -> bool:
        """
        Activa/desactiva autoplay para un servidor
        Retorna: True si está activo, False si está desactivado
        """
        if guild_id in self.enabled_guilds:
            self.enabled_guilds.remove(guild_id)
            return False
        else:
            self.enabled_guilds.add(guild_id)
            return True
    
    def is_enabled(self, guild_id: int) -> bool:
        """Verifica si autoplay está activo en un servidor"""
        return guild_id in self.enabled_guilds
    
    async def get_related_song(self, current_url: str, current_title: str) -> Optional[Dict]:
        """
        Obtiene una canción relacionada usando múltiples métodos
        
        Método 1: yt-dlp related videos (YouTube)
        Método 2: Búsqueda por artista/género
        
        Retorna: Dict con info de la canción o None
        """
        
        # Método 1: Intentar obtener videos relacionados con yt-dlp
        related_song = await self._get_yt_related(current_url)
        if related_song:
            print(f"✅ Autoplay: Encontrado video relacionado de YouTube")
            return related_song
        
        # Método 2: Búsqueda por artista (fallback)
        related_song = await self._search_by_artist(current_title)
        if related_song:
            print(f"✅ Autoplay: Encontrado por búsqueda de artista")
            return related_song
        
        print("⚠️  Autoplay: No se pudo encontrar canción relacionada")
        return None
    
    async def _get_yt_related(self, video_url: str) -> Optional[Dict]:
        """
        Obtiene un video relacionado desde YouTube usando yt-dlp
        """
        try:
            loop = asyncio.get_event_loop()
            
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,  # No descargar, solo extraer info
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extraer información incluyendo videos relacionados
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(video_url, download=False)
                )
                
                # Buscar videos relacionados
                # Nota: YouTube ha limitado esto, puede no siempre estar disponible
                if info and 'entries' in info:
                    # Si hay resultados, tomar el primero
                    related = info['entries'][0]
                    return {
                        'url': f"https://www.youtube.com/watch?v={related['id']}",
                        'title': related.get('title', 'Título desconocido'),
                        'duration': related.get('duration', 0),
                        'thumbnail': related.get('thumbnail')
                    }
                
                # Método alternativo: buscar en la descripción o tags
                if info:
                    # Extraer artista del título
                    artist = self._extract_artist(info.get('title', ''))
                    if artist:
                        return await self._search_by_artist(info.get('title', ''))
                
        except Exception as e:
            print(f"Error en _get_yt_related: {e}")
        
        return None
    
    async def _search_by_artist(self, title: str) -> Optional[Dict]:
        """
        Busca una canción del mismo artista o similar
        """
        try:
            # Extraer artista del título
            artist = self._extract_artist(title)
            
            if not artist:
                # Si no hay artista, buscar términos genéricos
                search_terms = self._extract_genre_terms(title)
                if search_terms:
                    artist = search_terms
                else:
                    return None
            
            # Buscar en YouTube
            search_query = f"{artist} music"
            
            loop = asyncio.get_event_loop()
            
            with yt_dlp.YoutubeDL(Config.YT_DLP_OPTIONS) as ydl:
                info = await loop.run_in_executor(
                    None,
                    lambda: ydl.extract_info(f"ytsearch5:{search_query}", download=False)
                )
                
                if info and 'entries' in info and len(info['entries']) > 0:
                    # Tomar un resultado aleatorio de los primeros 5
                    entries = [e for e in info['entries'] if e]  # Filtrar None
                    if entries:
                        selected = random.choice(entries[:min(5, len(entries))])
                        return {
                            'url': selected.get('webpage_url', f"https://www.youtube.com/watch?v={selected['id']}"),
                            'title': selected.get('title', 'Título desconocido'),
                            'duration': selected.get('duration', 0),
                            'thumbnail': selected.get('thumbnail')
                        }
        
        except Exception as e:
            print(f"Error en _search_by_artist: {e}")
        
        return None
    
    def _extract_artist(self, title: str) -> Optional[str]:
        """
        Extrae el artista del título de la canción
        Formato común: "Artista - Canción" o "Canción by Artista"
        """
        if not title:
            return None
        
        # Intentar formato "Artista - Canción"
        if ' - ' in title:
            return title.split(' - ')[0].strip()
        
        # Intentar formato "Canción by Artista"
        if ' by ' in title.lower():
            parts = title.lower().split(' by ')
            if len(parts) > 1:
                return parts[1].strip()
        
        # Intentar formato "Artista: Canción"
        if ': ' in title:
            return title.split(': ')[0].strip()
        
        # Si no hay separador claro, tomar las primeras 2-3 palabras
        words = title.split()
        if len(words) >= 2:
            return ' '.join(words[:2])
        
        return None
    
    def _extract_genre_terms(self, title: str) -> Optional[str]:
        """
        Extrae términos de género o tipo de música del título
        """
        genre_keywords = [
            'rock', 'metal', 'pop', 'jazz', 'blues', 'electronic',
            'hip hop', 'rap', 'classical', 'country', 'reggae',
            'indie', 'folk', 'punk', 'soul', 'r&b', 'edm'
        ]
        
        title_lower = title.lower()
        for genre in genre_keywords:
            if genre in title_lower:
                return genre
        
        return None