import asyncio
import logging
from musicbot import Config
from kurigram import Client, filters
from kurigram.types import Message
import yt_dlp
from py_tgcalls import PyTgCalls
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load config
config = Config()

# Initialize bot
bot = Client(
    name="MusicBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    workers=4
)

# Initialize userbot for voice calls
userbot = Client(
    name="UserBot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION1,
    workers=4
)

# Initialize PyTgCalls
call = PyTgCalls(userbot)

# Storage for queue and current playing
queues = {}
current_playing = {}

async def get_youtube_url(query: str) -> dict:
    """Get YouTube URL and info from query"""
    try:
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            return {
                'url': info.get('url'),
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception as e:
        logger.error(f"Error getting YouTube URL: {e}")
        return None

@bot.on_message(filters.command("start"))
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    await message.reply_text(
        "🎵 **Welcome to Music Bot!**\n\n"
        "Commands:\n"
        "• `/play <song>` - Play a song\n"
        "• `/pause` - Pause music\n"
        "• `/resume` - Resume music\n"
        "• `/skip` - Skip current song\n"
        "• `/stop` - Stop music\n"
        "• `/queue` - Show queue\n"
        "• `/ping` - Check bot status"
    )

@bot.on_message(filters.command("play"))
async def play_handler(client: Client, message: Message):
    """Handle /play command"""
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: `/play <song name>`")
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text(f"🔍 Searching for: **{query}**")
    
    try:
        song_info = await get_youtube_url(query)
        if not song_info:
            return await msg.edit_text("❌ Song not found!")
        
        chat_id = message.chat.id
        
        # Add to queue
        if chat_id not in queues:
            queues[chat_id] = []
        
        queues[chat_id].append(song_info)
        
        await msg.edit_text(
            f"✅ **Added to Queue**\n\n"
            f"**Title:** {song_info['title']}\n"
            f"**Duration:** {song_info['duration']}s\n"
            f"**Queue Position:** {len(queues[chat_id])}"
        )
        
        # If nothing is playing, start playing
        if chat_id not in current_playing:
            await play_next(chat_id)
            
    except Exception as e:
        logger.error(f"Play error: {e}")
        await msg.edit_text(f"❌ Error: {str(e)}")

async def play_next(chat_id: int):
    """Play next song in queue"""
    try:
        if chat_id not in queues or not queues[chat_id]:
            if chat_id in current_playing:
                await call.leave_group_call(chat_id)
                del current_playing[chat_id]
            return
        
        song = queues[chat_id].pop(0)
        current_playing[chat_id] = song
        
        # Join and play
        await call.join_group_call(
            chat_id,
            song['url'],
            stream_type="local_file"
        )
        
        logger.info(f"Now playing: {song['title']} in {chat_id}")
        
    except Exception as e:
        logger.error(f"Play next error: {e}")

@bot.on_message(filters.command("pause"))
async def pause_handler(client: Client, message: Message):
    """Handle /pause command"""
    try:
        await call.pause_stream(message.chat.id)
        await message.reply_text("⏸ **Music Paused**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("resume"))
async def resume_handler(client: Client, message: Message):
    """Handle /resume command"""
    try:
        await call.resume_stream(message.chat.id)
        await message.reply_text("▶️ **Music Resumed**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("skip"))
async def skip_handler(client: Client, message: Message):
    """Handle /skip command"""
    try:
        chat_id = message.chat.id
        await call.leave_group_call(chat_id)
        if chat_id in current_playing:
            del current_playing[chat_id]
        await play_next(chat_id)
        await message.reply_text("⏭️ **Skipped**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("stop"))
async def stop_handler(client: Client, message: Message):
    """Handle /stop command"""
    try:
        chat_id = message.chat.id
        await call.leave_group_call(chat_id)
        if chat_id in current_playing:
            del current_playing[chat_id]
        if chat_id in queues:
            queues[chat_id].clear()
        await message.reply_text("⏹️ **Music Stopped**")
    except Exception as e:
        await message.reply_text(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("queue"))
async def queue_handler(client: Client, message: Message):
    """Handle /queue command"""
    chat_id = message.chat.id
    
    if chat_id not in queues or not queues[chat_id]:
        return await message.reply_text("📭 **Queue is empty**")
    
    text = "📋 **Queue:**\n\n"
    for i, song in enumerate(queues[chat_id][:10], 1):
        text += f"{i}. {song['title']} ({song['duration']}s)\n"
    
    if len(queues[chat_id]) > 10:
        text += f"\n... and {len(queues[chat_id]) - 10} more"
    
    await message.reply_text(text)

@bot.on_message(filters.command("ping"))
async def ping_handler(client: Client, message: Message):
    """Handle /ping command"""
    await message.reply_text("🏓 **Pong!** Bot is online ✅")

async def main():
    """Main bot entry point"""
    try:
        config.check()
        logger.info("✅ Configuration validated")
    except SystemExit as e:
        logger.error(f"❌ Config error: {e}")
        raise
    
    logger.info("🎵 Music Bot Starting...")
    logger.info(f"Bot: @{config.BOT_TOKEN.split(':')[0]}")
    logger.info(f"Owner: {config.OWNER_ID}")
    
    try:
        # Start userbot for voice calls
        await userbot.start()
        logger.info("✅ Userbot started")
        
        # Start PyTgCalls
        await call.start()
        logger.info("✅ PyTgCalls started")
        
        # Start bot
        await bot.start()
        logger.info("✅ Bot started and listening for commands")
        
        # Keep running
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot error: {e}", exc_info=True)
        raise
    finally:
        await bot.stop()
        await userbot.stop()

if __name__ == "__main__":
    asyncio.run(main())
