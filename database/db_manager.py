
# Sistema de gestión de base de datos SQLite
# ============================================

import sqlite3
import os
from typing import List, Optional, Tuple
from datetime import datetime

class DatabaseManager:
    """Gestiona todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = 'database/music_bot.db'):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
    
    def _ensure_db_directory(self):
        """Crea el directorio de base de datos si no existe"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self):
        """Crea las tablas necesarias si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de playlists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playlists (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, guild_id, user_id)
                )
            ''')
            
            # Tabla de canciones en playlists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS playlist_songs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    playlist_id INTEGER NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT NOT NULL,
                    duration INTEGER DEFAULT 0,
                    thumbnail TEXT,
                    position INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE
                )
            ''')
            
            # Índices para mejorar rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_playlists_guild_user 
                ON playlists(guild_id, user_id)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_playlist_songs_playlist 
                ON playlist_songs(playlist_id, position)
            ''')
            
            conn.commit()
            print("✅ Base de datos inicializada correctamente")
    
    # ==================== OPERACIONES DE PLAYLISTS ====================
    
    def create_playlist(self, name: str, guild_id: int, user_id: int) -> Optional[int]:
        """
        Crea una nueva playlist
        Retorna: ID de la playlist creada o None si ya existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO playlists (name, guild_id, user_id)
                    VALUES (?, ?, ?)
                ''', (name, guild_id, user_id))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # Ya existe una playlist con ese nombre para ese usuario
            return None
        except Exception as e:
            print(f"Error al crear playlist: {e}")
            return None
    
    def delete_playlist(self, name: str, guild_id: int, user_id: int) -> bool:
        """
        Elimina una playlist
        Retorna: True si se eliminó, False si no existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM playlists 
                    WHERE name = ? AND guild_id = ? AND user_id = ?
                ''', (name, guild_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar playlist: {e}")
            return False
    
    def get_playlist_id(self, name: str, guild_id: int, user_id: int) -> Optional[int]:
        """
        Obtiene el ID de una playlist
        Retorna: ID de la playlist o None si no existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id FROM playlists 
                    WHERE name = ? AND guild_id = ? AND user_id = ?
                ''', (name, guild_id, user_id))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            print(f"Error al obtener playlist ID: {e}")
            return None
    
    def get_user_playlists(self, guild_id: int, user_id: int) -> List[Tuple[str, int, str]]:
        """
        Obtiene todas las playlists de un usuario en un servidor
        Retorna: Lista de tuplas (nombre, cantidad_canciones, fecha_creacion)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        p.name,
                        COUNT(ps.id) as song_count,
                        p.created_at
                    FROM playlists p
                    LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
                    WHERE p.guild_id = ? AND p.user_id = ?
                    GROUP BY p.id
                    ORDER BY p.created_at DESC
                ''', (guild_id, user_id))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener playlists del usuario: {e}")
            return []
    
    def rename_playlist(self, old_name: str, new_name: str, guild_id: int, user_id: int) -> bool:
        """
        Renombra una playlist
        Retorna: True si se renombró, False si no existe o el nuevo nombre ya existe
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE playlists 
                    SET name = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ? AND guild_id = ? AND user_id = ?
                ''', (new_name, old_name, guild_id, user_id))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            # Ya existe una playlist con el nuevo nombre
            return False
        except Exception as e:
            print(f"Error al renombrar playlist: {e}")
            return False
    
    # ==================== OPERACIONES DE CANCIONES ====================
    
    def add_song_to_playlist(self, playlist_id: int, url: str, title: str, 
                            duration: int = 0, thumbnail: str = None) -> bool:
        """
        Agrega una canción a una playlist
        Retorna: True si se agregó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener la siguiente posición
                cursor.execute('''
                    SELECT COALESCE(MAX(position), 0) + 1 
                    FROM playlist_songs 
                    WHERE playlist_id = ?
                ''', (playlist_id,))
                next_position = cursor.fetchone()[0]
                
                # Insertar la canción
                cursor.execute('''
                    INSERT INTO playlist_songs 
                    (playlist_id, url, title, duration, thumbnail, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (playlist_id, url, title, duration, thumbnail, next_position))
                
                # Actualizar timestamp de la playlist
                cursor.execute('''
                    UPDATE playlists 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (playlist_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error al agregar canción: {e}")
            return False
    
    def remove_song_from_playlist(self, playlist_id: int, position: int) -> bool:
        """
        Elimina una canción de una playlist por su posición
        Retorna: True si se eliminó correctamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Eliminar la canción
                cursor.execute('''
                    DELETE FROM playlist_songs 
                    WHERE playlist_id = ? AND position = ?
                ''', (playlist_id, position))
                
                if cursor.rowcount == 0:
                    return False
                
                # Reordenar posiciones
                cursor.execute('''
                    UPDATE playlist_songs 
                    SET position = position - 1 
                    WHERE playlist_id = ? AND position > ?
                ''', (playlist_id, position))
                
                # Actualizar timestamp de la playlist
                cursor.execute('''
                    UPDATE playlists 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (playlist_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error al eliminar canción: {e}")
            return False
    
    def get_playlist_songs(self, playlist_id: int) -> List[Tuple[str, str, int, str, int]]:
        """
        Obtiene todas las canciones de una playlist
        Retorna: Lista de tuplas (url, title, duration, thumbnail, position)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT url, title, duration, thumbnail, position
                    FROM playlist_songs
                    WHERE playlist_id = ?
                    ORDER BY position ASC
                ''', (playlist_id,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener canciones de playlist: {e}")
            return []
    
    def clear_playlist(self, playlist_id: int) -> bool:
        """
        Elimina todas las canciones de una playlist
        Retorna: True si se limpiaron las canciones
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM playlist_songs 
                    WHERE playlist_id = ?
                ''', (playlist_id,))
                
                # Actualizar timestamp de la playlist
                cursor.execute('''
                    UPDATE playlists 
                    SET updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (playlist_id,))
                
                conn.commit()
                return True
        except Exception as e:
            print(f"Error al limpiar playlist: {e}")
            return False
    
    def get_playlist_info(self, playlist_id: int) -> Optional[Tuple[str, int, int, str]]:
        """
        Obtiene información de una playlist
        Retorna: Tupla (nombre, guild_id, user_id, fecha_creacion) o None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, guild_id, user_id, created_at
                    FROM playlists
                    WHERE id = ?
                ''', (playlist_id,))
                return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener info de playlist: {e}")
            return None
    
    # ==================== UTILIDADES ====================
    
    def get_stats(self) -> dict:
        """Obtiene estadísticas generales de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total de playlists
                cursor.execute('SELECT COUNT(*) FROM playlists')
                total_playlists = cursor.fetchone()[0]
                
                # Total de canciones
                cursor.execute('SELECT COUNT(*) FROM playlist_songs')
                total_songs = cursor.fetchone()[0]
                
                # Playlists por servidor
                cursor.execute('''
                    SELECT guild_id, COUNT(*) 
                    FROM playlists 
                    GROUP BY guild_id
                ''')
                playlists_per_guild = dict(cursor.fetchall())
                
                return {
                    'total_playlists': total_playlists,
                    'total_songs': total_songs,
                    'playlists_per_guild': playlists_per_guild
                }
        except Exception as e:
            print(f"Error al obtener estadísticas: {e}")
            return {}
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        # SQLite cierra automáticamente con context managers
        pass
 
# ============================================    
#EJEMPLO DE USO (para testing)
# ============================================

if __name__ == "__main__":
    # Crear instancia
    db = DatabaseManager()
    
    # Pruebas
    print("\n🧪 Probando DatabaseManager...\n")
    
    # Crear playlist
    playlist_id = db.create_playlist("Rock Clásico", guild_id=123456, user_id=789012)
    if playlist_id:
        print(f"✅ Playlist creada con ID: {playlist_id}")
        
        # Agregar canciones
        db.add_song_to_playlist(
            playlist_id, 
            "https://youtube.com/watch?v=test1",
            "Bohemian Rhapsody",
            duration=354,
            thumbnail="https://i.ytimg.com/vi/test1/default.jpg"
        )
        print("✅ Canción agregada")
        
        # Obtener canciones
        songs = db.get_playlist_songs(playlist_id)
        print(f"✅ Canciones en playlist: {len(songs)}")
        
        # Obtener playlists del usuario
        user_playlists = db.get_user_playlists(123456, 789012)
        print(f"✅ Playlists del usuario: {len(user_playlists)}")
        
        # Estadísticas
        stats = db.get_stats()
        print(f"✅ Estadísticas: {stats}")
    
    print("\n✅ Pruebas completadas!\n")