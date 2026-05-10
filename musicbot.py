from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from py_tgcalls import PyTgCalls, Stream
import py_tgcalls

from yt_dlp import YoutubeDL

import asyncio
import os

# ==========================================
# VARIABLES (Environment se lo, hardcode mat karo)
# ==========================================

API_ID = int(os.getenv("API_ID", 30393394))  # Default values daal sakte ho
API_HASH = os.getenv("API_HASH", "e6c11cf9308422a702de45fe4a95b543")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8738226196:AAHcD8BH12Ev3zABlDFBbiePeW5aZaGtjX4")
STRING_SESSION = os.getenv("STRING_SESSION")

BOT_USERNAME = "lightmusicibot"  # ✅ Sirf username, @ ke bina
OWNER = "@light_speedy"

START_IMAGE = "https://files.catbox.moe/l7m3k9.png"

# ==========================================
# CLIENTS
# ==========================================

app = Client(
    "LightMusicBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

assistant = Client(
    "LightAssistant",
    api_id=API_ID,
    api_hash=API_HASH,
    session_string=STRING_SESSION
)

call_py = PyTgCalls(assistant)

# ==========================================
# YTDL
# ==========================================

ydl_opts = {
    "format": "bestaudio",
    "quiet": True,
    "geo-bypass": True,
    "nocheckcertificate": True
}

# ==========================================
# START COMMAND
# ==========================================

@app.on_message(filters.command("start"))
async def start(_, message):
    user = message.from_user
    
    text = f"""
✨ **Hey [{user.first_name}](tg://user?id={user.id})** 🎵

╭━━━━━━━━━━━━━━━━━╮
      🎧 LIGHT MUSIC BOT
╰━━━━━━━━━━━━━━━━━╯

⚡ Fastest VC Music Player
🎶 Smooth Streaming
🔥 HD Audio Quality
💎 Professional Music System

━━━━━━━━━━━━━━━
🌟 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Me To Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("👑 Owner", url="https://t.me/light_speedy"),
            InlineKeyboardButton("📚 Help", callback_data="help")
        ]
    ])
    
    await message.reply_photo(
        photo=START_IMAGE,
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# HELP CALLBACK
# ==========================================

@app.on_callback_query(filters.regex("help"))
async def help_menu(_, query):
    text = f"""
📚 **LIGHT MUSIC BOT COMMANDS**

▶️ /play song name
▶️ /pause
▶️ /resume
▶️ /skip
▶️ /stop
▶️ /ping

━━━━━━━━━━━━━━━
🌟 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back", callback_data="back")]
    ])
    
    await query.message.edit_caption(
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# BACK CALLBACK
# ==========================================

@app.on_callback_query(filters.regex("back"))
async def back(_, query):
    user = query.from_user
    
    text = f"""
✨ **Hey [{user.first_name}](tg://user?id={user.id})** 🎵

╭━━━━━━━━━━━━━━━━━╮
      🎧 LIGHT MUSIC BOT
╰━━━━━━━━━━━━━━━━━╯

⚡ Fastest VC Music Player
🎶 Smooth Streaming
🔥 HD Audio Quality
💎 Professional Music System

━━━━━━━━━━━━━━━
🌟 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "➕ Add Me To Group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton("👑 Owner", url="https://t.me/light_speedy"),
            InlineKeyboardButton("📚 Help", callback_data="help")
        ]
    ])
    
    await query.message.edit_caption(
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# PING COMMAND
# ==========================================

@app.on_message(filters.command("ping"))
async def ping(_, message):
    await message.reply_text("🏓 Pong! Bot Working Fine")

# ==========================================
# PLAY COMMAND
# ==========================================

@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply_text("❌ Usage: /play song name")
    
    query = " ".join(message.command[1:])
    msg = await message.reply_text("🔍 Searching Song...")
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        song = info["entries"][0]
        
        url = song["url"]
        title = song["title"]
        thumb = song["thumbnail"]
        duration = song.get("duration", 0)
    
   # ✅ py-tgcalls syntax
await call_py.join_group_call(
    message.chat.id,
    Stream(url)  # Direct URL se stream karne ke liye
)
    except Exception as e:
        return await msg.edit(f"❌ Error:\n{e}")
    
    caption = f"""
🎵 **Started Streaming**

━━━━━━━━━━━━━━━

🎧 **Title:** {title}

⏳ **Duration:** {duration} sec

👤 **Requested By:** {message.from_user.mention}

━━━━━━━━━━━━━━━
🌟 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸", callback_data="pause"),
            InlineKeyboardButton("▶️", callback_data="resume"),
            InlineKeyboardButton("⏹", callback_data="stop")
        ]
    ])
    
    await message.reply_photo(photo=thumb, caption=caption, reply_markup=buttons)
    await msg.delete()

# ==========================================
# CALLBACK HANDLERS
# ==========================================

@app.on_callback_query(filters.regex("pause"))
async def pause(_, query):
    await call_py.pause_stream(query.message.chat.id)
    await query.answer("Music Paused")

@app.on_callback_query(filters.regex("resume"))
async def resume(_, query):
    await call_py.resume_stream(query.message.chat.id)
    await query.answer("Music Resumed")

@app.on_callback_query(filters.regex("stop"))
async def stop(_, query):
    await call_py.leave_group_call(query.message.chat.id)
    await query.answer("Music Stopped")

# ==========================================
# COMMAND HANDLERS
# ==========================================

@app.on_message(filters.command("pause"))
async def pause_cmd(_, message):
    await call_py.pause_stream(message.chat.id)
    await message.reply_text("⏸ Music Paused")

@app.on_message(filters.command("resume"))
async def resume_cmd(_, message):
    await call_py.resume_stream(message.chat.id)
    await message.reply_text("▶️ Music Resumed")

@app.on_message(filters.command("stop"))
async def stop_cmd(_, message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply_text("⏹ Music Stopped")

# ==========================================
# MAIN
# ==========================================

async def main():
    await app.start()
    await assistant.start()
    await call_py.start()
    
    print("✅ LIGHT MUSIC BOT STARTED SUCCESSFULLY!")
    
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
