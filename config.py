
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración del bot Pentakill"""
    
    # Token de Discord
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    
    # Prefijo de comandos (aunque usaremos slash commands)
    COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '/')
    
    # Configuración de música
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
        'executable': 'C:/ffmpeg/bin/ffmpeg.exe'
    }
    
    YT_DLP_OPTIONS = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
    }
    
    # Colores para embeds
    COLOR_PRIMARY = 0x9B59B6  # Púrpura (tema Pentakill)
    COLOR_SUCCESS = 0x2ECC71  # Verde
    COLOR_ERROR = 0xE74C3C    # Rojo
    COLOR_INFO = 0x3498DB     # Azul
    
    # Base de datos
    DB_PATH = 'database/music_bot.db'
    
    @classmethod
    def validate(cls):
        """Valida que la configuración esté completa"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN no está configurado en .env")
        return True