# 🎸 Pentakill - Bot de Música para Discord

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**Un bot de música poderoso para Discord con reproducción automática, controles interactivos y playlists guardadas.**

[Características](#-características) •
[Instalación](#-instalación) •
[Configuración](#-configuración) •
[Comandos](#-comandos) •
[Deploy](#-deploy)

</div>

---

## ✨ Características

### 🎵 Reproducción Avanzada

- ✅ Reproducción desde **YouTube** (URLs o búsqueda por nombre)
- ✅ **Autoplay inteligente** - Busca música relacionada automáticamente
- ✅ **Cola ilimitada** de canciones
- ✅ **Controles interactivos** con botones (⏮️ Anterior | ⏸️ Pausa | ⏭️ Skip | ⏹️ Stop)
- ✅ **Historial** de canciones reproducidas
- ✅ Control de **volumen** (0-100%)
- ✅ Modos **loop** (canción actual o cola completa)
- ✅ **Shuffle** - Mezcla aleatoriamente la cola

### 📁 Sistema de Playlists

- ✅ **Crea y guarda** playlists personalizadas
- ✅ **Base de datos SQLite** - Tus playlists se guardan permanentemente
- ✅ Comparte playlists con tu servidor
- ✅ Agrega, elimina y renombra playlists fácilmente

### 🎨 Interfaz Moderna

- ✅ **Embeds visuales** con información de canciones
- ✅ **Thumbnails** de YouTube
- ✅ **Botones interactivos** para control rápido
- ✅ **Paginación** en colas largas
- ✅ Mensajes de estado en tiempo real

### 🚀 Rendimiento

- ✅ **Autoplay por defecto** - La música nunca se detiene
- ✅ **Búsqueda inteligente** - Encuentra música relacionada por artista o género
- ✅ **Reproducción continua** sin interrupciones
- ✅ **Bajo consumo** de recursos

---

## 📋 Requisitos

- **Python 3.8 o superior**
- **FFmpeg** (para reproducción de audio)
- **Token de bot de Discord**
- Conexión a internet estable

---

## 🚀 Instalación

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/MarianoPonce187/bot-Discord-music.git
cd bot-Discord-music
```

### 2️⃣ Crear entorno virtual (recomendado)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4️⃣ Instalar FFmpeg

#### Windows:

- **Opción A (Chocolatey):**

  ```powershell
  choco install ffmpeg
  ```

- **Opción B (Manual):**
  1. Descarga desde: https://github.com/BtbN/FFmpeg-Builds/releases
  2. Extrae en `C:\ffmpeg`
  3. Agrega `C:\ffmpeg\bin` al PATH

#### Linux:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch
sudo pacman -S ffmpeg
```

#### Mac:

```bash
brew install ffmpeg
```

---

## ⚙️ Configuración

### 1️⃣ Crear un Bot en Discord

1. Ve al [Discord Developer Portal](https://discord.com/developers/applications)
2. Click en **New Application**
3. Dale un nombre a tu aplicación
4. Ve a la sección **Bot**
5. Click en **Add Bot**
6. Copia el **TOKEN** (lo necesitarás después)
7. Habilita estos **Privileged Gateway Intents**:
   - ✅ Presence Intent
   - ✅ Server Members Intent
   - ✅ Message Content Intent

### 2️⃣ Invitar el bot a tu servidor

1. Ve a **OAuth2** → **URL Generator**
2. Selecciona estos **scopes**:
   - ✅ `bot`
   - ✅ `applications.commands`
3. Selecciona estos **permisos**:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Attach Files
   - ✅ Read Message History
   - ✅ Connect
   - ✅ Speak
   - ✅ Use Voice Activity
4. Copia la URL generada y ábrela en tu navegador
5. Selecciona tu servidor y autoriza

### 3️⃣ Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DISCORD_TOKEN=tu_token_aqui
COMMAND_PREFIX=/
```

**⚠️ IMPORTANTE:** Nunca subas tu `.env` a GitHub. Ya está incluido en `.gitignore`.

---

## 🎮 Comandos

### 🎵 Reproducción Básica

| Comando              | Descripción                              |
| -------------------- | ---------------------------------------- |
| `/play [canción]`    | Reproduce una canción (URL o búsqueda)   |
| `/playnow [canción]` | Reproduce inmediatamente (salta la cola) |
| `/pause`             | Pausa la reproducción                    |
| `/resume`            | Reanuda la reproducción                  |
| `/skip`              | Salta a la siguiente canción             |
| `/previous`          | Vuelve a la canción anterior             |
| `/stop`              | Detiene y limpia la cola                 |
| `/join`              | Une el bot al canal de voz               |
| `/leave`             | Desconecta el bot                        |

### 📋 Control de Cola

| Comando              | Descripción                      |
| -------------------- | -------------------------------- |
| `/lista [página]`    | Muestra la cola actual           |
| `/nowplaying`        | Información de la canción actual |
| `/clear`             | Limpia toda la cola              |
| `/remove [posición]` | Elimina una canción de la cola   |
| `/shuffle`           | Mezcla la cola aleatoriamente    |
| `/loop`              | Repite la canción actual         |
| `/looplista`         | Repite toda la cola              |

### 📁 Playlists

| Comando                          | Descripción                   |
| -------------------------------- | ----------------------------- |
| `/createlist [nombre]`           | Crea una nueva playlist       |
| `/mylists`                       | Muestra tus playlists         |
| `/showlist [nombre]`             | Ver canciones de una playlist |
| `/addtolist [nombre] [canción]`  | Agrega canción a playlist     |
| `/removefromlist [nombre] [pos]` | Quita canción de playlist     |
| `/playplaylist [nombre]`         | Reproduce playlist completa   |
| `/renamelist [viejo] [nuevo]`    | Renombra una playlist         |
| `/deletelist [nombre]`           | Elimina una playlist          |
| `/clearlist [nombre]`            | Limpia todas las canciones    |

### ⚙️ Configuración

| Comando           | Descripción                              |
| ----------------- | ---------------------------------------- |
| `/volume [0-100]` | Ajusta el volumen del bot                |
| `/autoplay`       | Activa/desactiva reproducción automática |
| `/help`           | Muestra todos los comandos               |

---

## 🎛️ Controles Interactivos

Cada canción incluye botones para control rápido:

- **⏮️ Anterior** - Vuelve a la canción anterior
- **⏸️ Pausa/Resume** - Pausa o reanuda la reproducción
- **⏭️ Siguiente** - Salta a la siguiente canción
- **⏹️ Stop** - Detiene la reproducción

---

## 🔄 Sistema Autoplay

El bot incluye un sistema inteligente de reproducción automática:

1. **Busca videos relacionados** en YouTube
2. Si no encuentra, **busca por artista/género**
3. **Mantiene la música sonando** sin interrupciones

**¿Cómo activarlo?**

- El autoplay está **activado por defecto**
- Puedes desactivarlo con `/autoplay`

---

## 🚢 Deploy en Producción

### Opción 1: Discloud (Recomendado para principiantes)

1. Crea un archivo `discloud.config` en la raíz:

   ```
   ID=tu_app_id
   NAME=Pentakill
   TYPE=bot
   MAIN=bot.py
   RAM=512
   AUTORESTART=true
   VERSION=recommended
   APT=tools
   ```

2. Comprime tu proyecto en ZIP (sin incluir `.env`, `venv/`, `__pycache__/`)

3. Sube el ZIP en [Discloud](https://discloud.app/)

4. Configura la variable de entorno `DISCORD_TOKEN` en el dashboard

### Opción 2: VPS (DigitalOcean, AWS, etc.)

1. **Conéctate a tu servidor:**

   ```bash
   ssh user@tu-servidor
   ```

2. **Instala Python y FFmpeg:**

   ```bash
   sudo apt update
   sudo apt install python3 python3-pip ffmpeg
   ```

3. **Clona el repositorio:**

   ```bash
   git clone https://github.com/MarianoPonce187/bot-Discord-music.git
   cd bot-Discord-music
   ```

4. **Instala dependencias:**

   ```bash
   pip3 install -r requirements.txt
   ```

5. **Configura el .env** con tu token

6. **Ejecuta con screen o tmux:**

   ```bash
   screen -S pentakill
   python3 bot.py
   # Presiona Ctrl+A, luego D para detach
   ```

7. **Para volver al bot:**
   ```bash
   screen -r pentakill
   ```

### Opción 3: Servicio systemd (Linux)

Crea `/etc/systemd/system/pentakill.service`:

```ini
[Unit]
Description=Pentakill Discord Bot
After=network.target

[Service]
Type=simple
User=tu_usuario
WorkingDirectory=/ruta/a/bot-Discord-music
ExecStart=/usr/bin/python3 /ruta/a/bot-Discord-music/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Luego:

```bash
sudo systemctl daemon-reload
sudo systemctl enable pentakill
sudo systemctl start pentakill
```

---

## 📂 Estructura del Proyecto

```
bot-Discord-music/
├── bot.py                 # Archivo principal
├── config.py             # Configuración
├── requirements.txt      # Dependencias
├── .env                  # Variables de entorno (NO subir a Git)
├── .gitignore           # Archivos ignorados
├── README.md            # Este archivo
│
├── cogs/                # Comandos del bot
│   ├── music.py        # Comandos de música
│   └── playlist.py     # Comandos de playlists
│
├── utils/               # Utilidades
│   ├── music_player.py     # Reproductor de música
│   ├── queue_manager.py    # Gestión de cola
│   ├── autoplay_manager.py # Sistema autoplay
│   └── music_controls.py   # Botones interactivos
│
└── database/            # Base de datos
    ├── db_manager.py   # Gestión de BD
    └── music_bot.db    # SQLite (se crea automáticamente)
```

---

## 🛠️ Solución de Problemas

### El bot no se conecta

- ✅ Verifica que el token en `.env` sea correcto
- ✅ Revisa que los intents estén habilitados en Discord Developer Portal
- ✅ Asegúrate de que el bot esté invitado al servidor

### No reproduce música

- ✅ Verifica que FFmpeg esté instalado: `ffmpeg -version`
- ✅ En Windows, asegúrate que FFmpeg esté en el PATH
- ✅ Revisa los logs en consola para ver errores

### Comandos no aparecen en Discord

- ✅ Espera 1-2 minutos después de iniciar el bot
- ✅ Usa el comando `!sync` en Discord para forzar sincronización
- ✅ Re-invita el bot con los permisos correctos

### Error con yt-dlp

```bash
pip install --upgrade yt-dlp
```

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Si quieres mejorar Pentakill:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📝 Notas Importantes

- ⚠️ **No compartas tu token de Discord** con nadie
- ⚠️ El archivo `.env` está en `.gitignore` por seguridad
- ⚠️ La base de datos SQLite se crea automáticamente
- ⚠️ Los botones expiran después de 15 minutos (límite de Discord)

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

---

## 👨‍💻 Autor

Creado con ❤️ por [Mariano](https://github.com/MarianoPonce187)

---

## 🎸 ¡Disfruta de Pentakill!

Si te gusta el proyecto, ¡dale una ⭐ en GitHub!

---

<div align="center">

**¿Problemas? [Abre un Issue](https://github.com/MarianoPonce187/bot-Discord-music/issues)**

**¿Preguntas? [Discussions](https://github.com/MarianoPonce187/bot-Discord-music/discussions)**

</div>
