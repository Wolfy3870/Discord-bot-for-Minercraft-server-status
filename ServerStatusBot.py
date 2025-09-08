import discord
from discord.ext import commands, tasks
import asyncio
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)

try:
    from mcstatus import JavaServer
except ImportError:
    print("❌ mcstatus not installed. Run: pip install mcstatus")
    exit(1)

# ---------------- CONFIG ----------------
# Use a dictionary to store configuration, making it easier to modify
config = {
    "DISCORD_TOKEN": "YOUR_DISCORD_BOT_TOKEN",
    "MINECRAFT_IP": "MINECRAFT_SERVER_IP",
    "MINECRAFT_PORT": 00000,
    "CHANNEL_ID": 0000000000000000000,
    "STATUS_CHANNEL_ID": 00000000000000000000,
    "UPDATE_INTERVAL": 60,
}
# ----------------------------------------

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

status_message = None  # Reference to the status message
maintenance_mode = False  # Flag for maintenance mode

# Change the font
def to_math_bold(text: str) -> str:
    """Convert normal text to Unicode Math Serif Bold"""
    result = ""
    for char in text:
        if "A" <= char <= "Z":
            result += chr(ord("𝐀") + ord(char) - ord("A"))
        elif "a" <= char <= "z":
            result += chr(ord("𝐚") + ord(char) - ord("a"))
        elif "0" <= char <= "9":
            result += chr(ord("𝟎") + ord(char) - ord("0"))
        else:
            result += char
    return result


async def get_server_status():
    """Check Minecraft server status and return a formatted string."""
    global maintenance_mode

    # If in maintenance, return maintenance status
    if maintenance_mode:
        return "🛠 | *Server Status: MAINTENANCE*", False, 0

    try:
        # Create connection to the server with a timeout
        server = JavaServer.lookup(f"{config['MINECRAFT_IP']}:{config['MINECRAFT_PORT']}")

        # First, try to ping to check connectivity
        await asyncio.wait_for(asyncio.to_thread(server.ping), timeout=10.0)

        # Get full status
        status = await asyncio.wait_for(asyncio.to_thread(server.status), timeout=15.0)

        # Extract player information
        players_online = status.players.online if status.players else 0
        players_max = status.players.max if status.players else 0

        # Extract version - handle different formats
        version_name = "N/A"
        if hasattr(status, 'version') and status.version:
            if hasattr(status.version, 'name'):
                version_name = status.version.name
            elif hasattr(status.version, 'protocol'):
                # If there's no name, use the protocol number
                version_name = f"Protocol {status.version.protocol}"

        # Player list (if available)
        player_list = ""
        if status.players and status.players.sample and len(status.players.sample) > 0:
            player_names = [player.name for player in status.players.sample[:10]]  # Max 10 names
            if len(player_names) > 0:
                player_list = f"\n🎯 | *Players online:* {', '.join(player_names)}"
                if len(status.players.sample) > 10:
                    player_list += f" *(+{len(status.players.sample) - 10} others)*"

        return (
            f"🟢 | *Server Status: ONLINE*\n"
            f"👥 | *Players:* {players_online}/{players_max}\n"
            f"🎮 | *Version:* {version_name}"
            f"{player_list}"
        ), True, players_online

    except asyncio.TimeoutError:
        logging.warning("Timeout while connecting to the Minecraft server")
        return "🟡 | *Server Status: TIMEOUT (server might be overloaded)*", False, 0
    except Exception as e:
        logging.error(f"Error while checking status: {e}")
        return "🔴 | *Server Status: OFFLINE*", False, 0


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🔍 Monitoring server: {config['MINECRAFT_IP']}:{config['MINECRAFT_PORT']}")

    channel = bot.get_channel(config['CHANNEL_ID'])
    global status_message

    if channel:
        try:
            status_text, _, _ = await get_server_status()
            status_message = await channel.send(status_text)
            print("✅ Initial status message sent")
        except Exception as e:
            print(f"❌ Error sending initial message: {e}")
    else:
        print(f"❌ Channel with ID {config['CHANNEL_ID']} not found")

    # Start the update task with the default interval
    if not update_status.is_running():
        update_status.change_interval(seconds=config['UPDATE_INTERVAL'])
        update_status.start()


@tasks.loop(seconds=config['UPDATE_INTERVAL'])  # update every xs
async def update_status():
    global status_message, maintenance_mode

    try:
        if status_message:
            status_text, online, players = await get_server_status()
            await status_message.edit(content=status_text)

            # 🔹 Update channel name
            status_channel = bot.get_channel(config['STATUS_CHANNEL_ID'])
            if status_channel:
                try:
                    if maintenance_mode:
                        new_name = f"🛠 | {to_math_bold('Maintenance')}"
                    elif online:
                        new_name = f"🟢 | {to_math_bold('Online')} [{players}]"
                    else:
                        new_name = f"🔴 | {to_math_bold('Offline')}"

                    # Only update if the name is different
                    if status_channel.name != new_name:
                        await status_channel.edit(name=new_name)

                except discord.HTTPException as e:
                    if e.status == 429:  # Rate limit
                        logging.warning("Rate limit for channel name change")
                    else:
                        logging.error(f"Error changing channel name: {e}")

    except Exception as e:
        logging.error(f"Error during status update: {e}")


@update_status.before_loop
async def before_update_status():
    await bot.wait_until_ready()


@bot.command()
async def status(ctx):
    """Check server status manually"""
    try:
        msg, online, players = await get_server_status()
        embed = discord.Embed(
            title="🖥️ Server Status",
            description=msg,
            color=0x00ff00 if online else 0xff0000
        )
        embed.set_footer(text=f"Server: {config['MINECRAFT_IP']}:{config['MINECRAFT_PORT']}")
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error checking status: {e}")


@bot.command()
@commands.has_permissions(administrator=True)
async def maintenance(ctx, mode: str = None):
    """Toggle maintenance mode: !maintenance on / off"""
    global status_message, maintenance_mode

    if mode == "on":
        maintenance_mode = True
        if status_message:
            await status_message.edit(content="🛠 | *Server Status: MAINTENANCE*")

        status_channel = bot.get_channel(config['STATUS_CHANNEL_ID'])
        if status_channel:
            try:
                await status_channel.edit(name=f"🛠 | {to_math_bold('Maintenance')}")
            except Exception as e:
                logging.error(f"Error changing channel name: {e}")

        await ctx.send("🛠 | Maintenance mode enabled.")

    elif mode == "off":
        maintenance_mode = False
        if status_message:
            new_status, online, players = await get_server_status()
            await status_message.edit(content=new_status)

        status_channel = bot.get_channel(config['STATUS_CHANNEL_ID'])
        if status_channel:
            try:
                if online:
                    await status_channel.edit(name=f"🟢 | {to_math_bold('Online')} [{players}]")
                else:
                    await status_channel.edit(name=f"🔴 | {to_math_bold('Offline')}")
            except Exception as e:
                logging.error(f"Error changing channel name: {e}")

        await ctx.send("✅ | Maintenance mode disabled.")

    else:
        await ctx.send("⚠️ | Usage: `!maintenance on` or `!maintenance off`")


@bot.command()
async def ping(ctx):
    """Test bot responsiveness"""
    try:
        server = JavaServer.lookup(f"{config['MINECRAFT_IP']}:{config['MINECRAFT_PORT']}")
        start_time = asyncio.get_event_loop().time()
        latency = await asyncio.to_thread(server.ping)
        end_time = asyncio.get_event_loop().time()

        bot_latency = round(bot.latency * 1000, 2)
        server_latency = round((end_time - start_time) * 1000, 2)

        embed = discord.Embed(
            title="🏓 Ping Test",
            color=0x00ff00
        )
        embed.add_field(name="Bot Latency", value=f"{bot_latency}ms", inline=True)
        embed.add_field(name="Server Latency", value=f"{server_latency}ms", inline=True)
        embed.add_field(name="MC Server Ping", value=f"{latency:.2f}ms", inline=True)
        embed.set_footer(text=f"Server: {config['MINECRAFT_IP']}:{config['MINECRAFT_PORT']}")

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"❌ Error pinging: {e}")


# ---------------- NEW COMMANDS ----------------
@bot.command()
@commands.has_permissions(administrator=True)
async def setip(ctx, ip: str):
    """Set the new Minecraft server IP address."""
    if not ip:
        await ctx.send("⚠️ | Usage: `!setip <new_ip>`")
        return
    config['MINECRAFT_IP'] = ip
    await ctx.send(f"✅ | Minecraft server IP updated to: `{ip}`")
    logging.info(f"IP updated to: {ip}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setport(ctx, port: int):
    """Set the new Minecraft server port."""
    if not port or not isinstance(port, int):
        await ctx.send("⚠️ | Usage: `!setport <new_port>` (the port must be an integer)")
        return
    config['MINECRAFT_PORT'] = port
    await ctx.send(f"✅ | Minecraft server port updated to: `{port}`")
    logging.info(f"Port updated to: {port}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setUpdateChannel(ctx, channel_id: int):
    """Set the ID of the channel for status updates."""
    if not channel_id or not isinstance(channel_id, int):
        await ctx.send("⚠️ | Usage: `!setUpdateChannel <channel_id>` (the ID must be an integer)")
        return
    config['CHANNEL_ID'] = channel_id
    await ctx.send(f"✅ | Status updates channel updated to: `{channel_id}`")
    logging.info(f"Update channel ID updated to: {channel_id}")

@bot.command()
@commands.has_permissions(administrator=True)
async def setChannelToRename(ctx, channel_id: int):
    """Set the ID of the channel to rename with the status."""
    if not channel_id or not isinstance(channel_id, int):
        await ctx.send("⚠️ | Usage: `!setChannelToRename <channel_id>` (the ID must be an integer)")
        return
    config['STATUS_CHANNEL_ID'] = channel_id
    await ctx.send(f"✅ | Channel to rename updated to: `{channel_id}`")
    logging.info(f"Channel to rename ID updated to: {channel_id}")

@bot.command()
@commands.has_permissions(administrator=True)
async def updateInterval(ctx, seconds: int):
    """Set the new update interval (min 25, max 300)."""
    min_interval = 25
    max_interval = 300

    if seconds < min_interval or seconds > max_interval:
        await ctx.send(f"⚠️ | The interval must be between `{min_interval}` and `{max_interval}` seconds.")
        return

    config['UPDATE_INTERVAL'] = seconds
    update_status.change_interval(seconds=seconds)
    await ctx.send(f"✅ | Update interval set to `{seconds}` seconds.")
    logging.info(f"Update interval changed to: {seconds} seconds.")

# ----------------------------------------

# Global error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have the permissions to run this command.")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore commands not found
    else:
        logging.error(f"Command error: {error}")
        await ctx.send(f"❌ An error occurred: {error}")


if __name__ == "__main__":
    try:
        bot.run(config['DISCORD_TOKEN'])
    except Exception as e:
        print(f"❌ Error starting the bot: {e}")
        print("Please check that the Discord token is correct and that the bot has the necessary permissions.")