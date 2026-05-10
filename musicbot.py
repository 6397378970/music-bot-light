import asyncio
import os
from datetime import datetime

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.enums import ChatType, ParseMode
from pyrogram.errors import RPCError

# ❌ Yeh hata do
# from py_tgcalls import PyTgcalls, Stream

# ✅ Yeh daal do
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# ==========================================
# CONFIGURATION
# ==========================================

API_ID = int(os.getenv("30393394"))
API_HASH = os.getenv("e6c11cf9308422a702de45fe4a95b543")
BOT_TOKEN = os.getenv("8738226196:AAHcD8BH12Ev3zABlDFBbiePeW5aZaGtjX4")
STRING_SESSION = os.getenv("BQHPxDIAqyC-rURYuKkGxyKYICv1VjZyCJLvTIS2kOTKZbNrI5ZA__oZ2YZINvtk6Ut286tZFvHIlEXoGkNQH9L0fW7dKGWK0c5DO5eOCtPRZUzCH0F3dK_60daPI4erELF5T71ykXgSQY1MGssSwjdTrWMdc0m5gp9B7F_rSGtun2g-SUNgA03BkILScVkAvKj8afLPZPFwCnbEKbImsYkpjDS4JZGApS7jM9BYnmgqvA8QtG93UMwbQr7iTLUonavv9qWOO7xVtu3wVfBnLw4zn8563ZZ5afQN-8M7g5cwF3tWrkMa5547JLllvy8wEr-cn0pI-9JBNyz_hoVlI-p9p71GmwAAAAFMSMrYAA")

OWNER_ID = int(os.getenv("OWNER_ID", "7676301555"))
BOT_USERNAME = "LightMusicBot"  # Your bot username without @

START_IMG = "https://files.catbox.moe/l7m3k9.png"
SUPPORT_LINK = "https://t.me/midnight_chatclub"
CHANNEL_LINK = "https://t.me/anonymous_rides"

# ==========================================
# CLIENTS INITIALIZATION
# ==========================================

bot = Client(
    "MusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

userbot = Client(
    "UserBot",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

call = PyTgCalls(userbot)

# ==========================================
# VARIABLES
# ==========================================

queues = {}
current_playing = {}
paused = {}

# ==========================================
# HELPERS
# ==========================================

def get_duration(seconds: int):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def get_size(bytes: int):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes < 1024:
            return f"{bytes:.2f} {unit}"
        bytes /= 1024
    return f"{bytes:.2f} TB"

async def get_audio_info(url: str):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info.get('title', 'Unknown'),
            'duration': info.get('duration', 0),
            'thumbnail': info.get('thumbnail', ''),
            'uploader': info.get('uploader', 'Unknown'),
            'views': info.get('view_count', 0),
            'url': url
        }

async def search_song(query: str):
    ydl_opts = {
        'format': 'bestaudio',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch5'
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                return info['entries'][0]
            return info
        except:
            return None

# ==========================================
# MUSIC CONTROLS
# ==========================================

async def play_song(chat_id: int, song_url: str, title: str):
    try:
        await call.join_group_call(
            chat_id,
            MediaStream(song_url)
        )
        current_playing[chat_id] = {
            'title': title,
            'url': song_url,
            'start_time': datetime.now()
        }
        return True
    except Exception as e:
        print(f"Error playing: {e}")
        return False


async def add_to_queue(chat_id: int, song_info: dict):
    if chat_id not in queues:
        queues[chat_id] = []
    queues[chat_id].append(song_info)
    
async def play_next(chat_id: int):
    if chat_id in queues and queues[chat_id]:
        next_song = queues[chat_id].pop(0)
        await play_song(chat_id, next_song['url'], next_song['title'])
        
        # Send now playing message
        await bot.send_message(
            chat_id,
            f"🎵 **Now Playing:**\n\n"
            f"**Title:** {next_song['title']}\n"
            f"**Duration:** {get_duration(next_song['duration'])}\n"
            f"**Requested By:** {next_song.get('requester', 'Unknown')}\n\n"
            f"**Queue Left:** {len(queues[chat_id])} songs"
        )
    else:
        await call.leave_group_call(chat_id)
        if chat_id in current_playing:
            del current_playing[chat_id]

# ==========================================
# COMMANDS
# ==========================================

@bot.on_message(filters.command(["start", "help"]))
async def start_command(client: Client, message: Message):
    user = message.from_user
    
    text = f"""**✨ Welcome {user.mention()}!**

**🎧 I'm an Advanced Music Bot**
I can play high-quality music in voice chats with queue system!

**📚 Available Commands:**

**▶️ Playback:**
• `/play <song name>` - Play a song
• `/pause` - Pause current song
• `/resume` - Resume paused song
• `/skip` - Skip current song
• `/stop` - Stop playback

**📋 Queue:**
• `/queue` - Show queue list
• `/clear` - Clear entire queue

**ℹ️ Info:**
• `/ping` - Check bot status
• `/help` - Show this menu

**🎵 Features:**
• High Quality Audio
• Queue System
• YouTube Support
• 24/7 Stable

**💝 Made with ❤️ by @OwnerUsername**
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true"),
            InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK)
        ],
        [
            InlineKeyboardButton("🆘 Support", url=SUPPORT_LINK),
            InlineKeyboardButton("👑 Owner", url="@light_speedy")
        ]
    ])
    
    await message.reply_photo(
        photo=START_IMG,
        caption=text,
        reply_markup=buttons
    )

@bot.on_message(filters.command("play"))
async def play_command(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("❌ **Please provide a song name!**\n\nUsage: `/play <song name>`")
    
    query = " ".join(message.command[1:])
    user = message.from_user
    
    msg = await message.reply_text("🔍 **Searching for song...**")
    
    # Search song
    song = await search_song(query)
    
    if not song:
        return await msg.edit_text("❌ **No results found!**")
    
    # Get audio URL
    with YoutubeDL({'format': 'bestaudio', 'quiet': True}) as ydl:
        info = ydl.extract_info(f"https://youtube.com/watch?v={song['id']}", download=False)
        audio_url = info['url']
    
    song_info = {
        'title': song.get('title', 'Unknown'),
        'duration': int(song.get('duration', 0)),
        'url': audio_url,
        'requester': user.mention,
        'thumbnail': f"https://img.youtube.com/vi/{song['id']}/hqdefault.jpg"
    }
    
    # Check if already playing
    if message.chat.id in current_playing:
        await add_to_queue(message.chat.id, song_info)
        await msg.edit_text(
            f"✅ **Added to Queue!**\n\n"
            f"**Title:** {song_info['title']}\n"
            f"**Duration:** {get_duration(song_info['duration'])}\n"
            f"**Position:** {len(queues[message.chat.id])}\n\n"
            f"**Requested by:** {user.mention}"
        )
    else:
        # Play immediately
        success = await play_song(message.chat.id, audio_url, song_info['title'])
        if success:
            await msg.edit_text(
                f"🎵 **Now Playing!**\n\n"
                f"**Title:** {song_info['title']}\n"
                f"**Duration:** {get_duration(song_info['duration'])}\n"
                f"**Requested by:** {user.mention}"
            )
        else:
            await msg.edit_text("❌ **Failed to play!**")

@bot.on_message(filters.command("pause"))
async def pause_command(client: Client, message: Message):
    if message.chat.id in current_playing:
        try:
            await call.pause_stream(message.chat.id)
            await message.reply_text("⏸ **Music Paused!**\n\nUse `/resume` to continue.")
        except:
            await message.reply_text("❌ **Nothing is playing!**")
    else:
        await message.reply_text("❌ **No music is playing!**")

@bot.on_message(filters.command("resume"))
async def resume_command(client: Client, message: Message):
    if message.chat.id in current_playing:
        try:
            await call.resume_stream(message.chat.id)
            await message.reply_text("▶️ **Music Resumed!**")
        except:
            await message.reply_text("❌ **Nothing is paused!**")
    else:
        await message.reply_text("❌ **No music is playing!**")

@bot.on_message(filters.command("skip"))
async def skip_command(client: Client, message: Message):
    if message.chat.id in current_playing:
        await message.reply_text("⏭️ **Skipping current song...**")
        await play_next(message.chat.id)
    else:
        await message.reply_text("❌ **Nothing is playing!**")

@bot.on_message(filters.command("stop"))
async def stop_command(client: Client, message: Message):
    if message.chat.id in current_playing:
        await call.leave_group_call(message.chat.id)
        if message.chat.id in current_playing:
            del current_playing[message.chat.id]
        if message.chat.id in queues:
            queues[message.chat.id].clear()
        await message.reply_text("⏹️ **Music Stopped! Queue Cleared.**")
    else:
        await message.reply_text("❌ **Nothing is playing!**")

@bot.on_message(filters.command("queue"))
async def queue_command(client: Client, message: Message):
    chat_id = message.chat.id
    
    if chat_id not in queues or not queues[chat_id]:
        return await message.reply_text("📭 **Queue is empty!**\n\nUse `/play` to add songs.")
    
    queue_list = queues[chat_id]
    current = current_playing.get(chat_id, {})
    
    text = f"**📋 Current Queue**\n\n"
    text += f"**▶️ Now Playing:**\n{current.get('title', 'None')}\n\n"
    text += f"**📝 Queue List:**\n"
    
    for i, song in enumerate(queue_list[:10], 1):
        text += f"{i}. {song['title']} - `{get_duration(song['duration'])}`\n"
    
    if len(queue_list) > 10:
        text += f"\n*And {len(queue_list) - 10} more...*"
    
    await message.reply_text(text)

@bot.on_message(filters.command("clear"))
async def clear_command(client: Client, message: Message):
    if message.chat.id in queues:
        queues[message.chat.id].clear()
        await message.reply_text("🗑️ **Queue Cleared!**")
    else:
        await message.reply_text("📭 **Queue is already empty!**")

@bot.on_message(filters.command("ping"))
async def ping_command(client: Client, message: Message):
    start = datetime.now()
    msg = await message.reply_text("🏓 **Pinging...**")
    end = datetime.now()
    latency = (end - start).microseconds / 1000
    await msg.edit_text(f"🏓 **Pong!**\n\n**Latency:** `{latency}ms`\n**Status:** 🟢 Online")

# ==========================================
# VOICE CHAT HANDLERS
# ==========================================

@call.on_stream_end()
async def stream_end_handler(chat_id: int):
    await play_next(chat_id)

@call.on_kicked()
async def kicked_handler(chat_id: int):
    if chat_id in current_playing:
        del current_playing[chat_id]
    if chat_id in queues:
        queues[chat_id].clear()

# ==========================================
# START BOT
# ==========================================

async def main():
    await bot.start()
    await userbot.start()
    await call.start()
    
    print("""
    ╔═══════════════════════════════╗
    ║   🎵 MUSIC BOT STARTED! 🎵    ║
    ║                               ║
    ║   Status: 🟢 Online           ║
    ║   Commands: ✅ Loaded         ║
    ╚═══════════════════════════════╝
    """)
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
