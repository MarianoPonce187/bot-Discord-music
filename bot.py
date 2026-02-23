
import discord
from discord.ext import commands
import asyncio
import sys
from config import Config

class Pentakill(commands.Bot):
    """Bot de música Pentakill para Discord"""
    
    def __init__(self):
        # Configurar intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.voice_states = True
        intents.guilds = True
        
        super().__init__(
            command_prefix=Config.COMMAND_PREFIX,
            intents=intents,
            help_command=None
        )
        
        self.initial_extensions = [
            'cogs.music',
            'cogs.playlist'
        ]
    
    async def setup_hook(self):
        """Se ejecuta antes de que el bot inicie"""
        print("🎸 Pentakill está despertando...")
        
        # Cargar extensiones (cogs)
        for ext in self.initial_extensions:
            try:
                await self.load_extension(ext)
                print(f"✅ Extensión cargada: {ext}")
            except Exception as e:
                print(f"❌ Error al cargar {ext}: {e}")
        
        # Sincronizar comandos slash
        try:
            synced = await self.tree.sync()
            print(f"✅ {len(synced)} comandos slash sincronizados")
        except Exception as e:
            print(f"❌ Error al sincronizar comandos: {e}")
    
    async def on_ready(self):
        """Evento cuando el bot está listo"""
        print("=" * 50)
        print(f"🎸 Bot: {self.user.name}")
        print(f"🆔 ID: {self.user.id}")
        print(f"🌐 Servidores: {len(self.guilds)}")
        print(f"👥 Usuarios: {sum(g.member_count for g in self.guilds)}")
        print("=" * 50)
        print("✅ Pentakill está listo para rockear! 🤘")
        
        # Establecer estado del bot
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="🎵 /help para comandos"
            )
        )
    
    async def on_guild_join(self, guild):
        """Evento cuando el bot se une a un servidor"""
        print(f"✅ Pentakill se unió a: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild):
        """Evento cuando el bot sale de un servidor"""
        print(f"❌ Pentakill salió de: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Manejo global de errores"""
        if isinstance(error, commands.CommandNotFound):
            return  # Ignorar comandos no encontrados
        
        print(f"❌ Error en comando: {error}")
        
    @commands.command(name='sync')
    @commands.is_owner()
    async def sync(self, ctx):
        """Sincroniza comandos slash manualmente (solo owner)"""
        try:
            synced = await self.tree.sync()
            await ctx.send(f'✅ {len(synced)} comandos sincronizados!')
        except Exception as e:
            await ctx.send(f'❌ Error: {e}')

    @commands.command(name='clearsync')
    @commands.is_owner()
    async def clearsync(self, ctx):
        """Limpia y vuelve a sincronizar todos los comandos"""
        try:
            self.tree.clear_commands(guild=None)
            await self.tree.sync()
            synced = await self.tree.sync()
            await ctx.send(f'✅ Comandos limpiados y {len(synced)} comandos re-sincronizados!')
        except Exception as e:
            await ctx.send(f'❌ Error: {e}')


async def main():
    """Función principal para iniciar el bot"""
    
    # Validar configuración
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Error de configuración: {e}")
        sys.exit(1)
    
    # Crear instancia del bot
    bot = Pentakill()
    
    # Iniciar el bot
    try:
        print("🚀 Iniciando Pentakill...")
        await bot.start(Config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupción detectada. Cerrando Pentakill...")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
    finally:
        await bot.close()
        print("👋 Pentakill se ha desconectado")


if __name__ == "__main__":
    # Ejecutar el bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Adiós!")