# ============================================
# Sistema de gestión de lista de canciones
# ============================================

import discord
from collections import deque
from typing import Optional, List

class Song:
    """Representa una canción en la lista"""
    
    def __init__(self, url: str, title: str, duration: int, requester: discord.Member, thumbnail: str = None):
        self.url = url
        self.title = title
        self.duration = duration
        self.requester = requester
        self.thumbnail = thumbnail
    
    def __str__(self):
        return f"{self.title} - solicitada por {self.requester.name}"


class QueueManager:
    """Gestiona la lista de reproducción de un servidor"""
    
    def __init__(self):
        self.queue = deque()
        self.current = None
        self.loop = False
        self.loop_queue = False
        self.history = deque(maxlen=10)
    
    def add(self, song: Song):
        """Agrega una canción a la lista"""
        self.queue.append(song)
    
    def add_next(self, song: Song):
        """Agrega una canción al principio de la lista (playnow)"""
        self.queue.appendleft(song)
    
    def get_next(self) -> Optional[Song]:
        """Obtiene la siguiente canción de la lista"""
        if self.loop and self.current:
            return self.current
        
        if not self.queue:
            return None
        
        song = self.queue.popleft()
        
        # Si loop_queue está activo, agregar al final
        if self.loop_queue:
            self.queue.append(song)
        
        self.current = song
        return song
    
    def skip(self):
        """Salta la canción actual (NO LIMPIAR current para que autoplay funcione)"""
        # NO hacer self.current = None
        # El método play_next manejará esto correctamente
        pass
    
    def clear(self):
        """Limpia toda la lista"""
        self.queue.clear()
        self.current = None
    
    def remove(self, index: int) -> Optional[Song]:
        """Elimina una canción específica por índice"""
        if 0 <= index < len(self.queue):
            song = self.queue[index]
            del self.queue[index]
            return song
        return None
    
    def get_queue(self) -> List[Song]:
        """Retorna la lista de canciones en lista"""
        return list(self.queue)
    
    def is_empty(self) -> bool:
        """Verifica si la lista está vacía"""
        return len(self.queue) == 0
    
    def size(self) -> int:
        """Retorna el tamaño de la lista"""
        return len(self.queue)
    
    def get_next(self) -> Optional[Song]:
        """Obtiene la siguiente canción de la cola"""
        if self.loop and self.current:
            return self.current

        if not self.queue:
            return None

        song = self.queue.popleft()

        # Guardar canción actual en historial antes de cambiar
        if self.current:
            self.history.append(self.current)

        # Si loop_queue está activo, agregar al final
        if self.loop_queue:
            self.queue.append(song)

        self.current = song
        return song
    
    def get_previous(self) -> Optional[Song]:
        """Obtiene la canción anterior del historial"""

        if not self.history:
            return None

        # Sacar del historial
        previous_song = self.history.pop()

        # Agregar canción actual al inicio de la cola
        if self.current:
            self.queue.appendleft(self.current)

        self.current = previous_song
        return previous_song
    