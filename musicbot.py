from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped

from yt_dlp import YoutubeDL

import asyncio
import os

# ==========================================
# CONFIG
# ==========================================

API_ID = int(os.getenv("30393394"))
API_HASH = os.getenv("e6c11cf9308422a702de45fe4a95b543")
BOT_TOKEN = os.getenv("8738226196:AAHcD8BH12Ev3zABlDFBbiePeW5aZaGtjX4")
STRING_SESSION = os.getenv("BQHPxDIAqyC-rURYuKkGxyKYICv1VjZyCJLvTIS2kOTKZbNrI5ZA__oZ2YZINvtk6Ut286tZFvHIlEXoGkNQH9L0fW7dKGWK0c5DO5eOCtPRZUzCH0F3dK_60daPI4erELF5T71ykXgSQY1MGssSwjdTrWMdc0m5gp9B7F_rSGtun2g-SUNgA03BkILScVkAvKj8afLPZPFwCnbEKbImsYkpjDS4JZGApS7jM9BYnmgqvA8QtG93UMwbQr7iTLUonavv9qWOO7xVtu3wVfBnLw4zn8563ZZ5afQN-8M7g5cwF3tWrkMa5547JLllvy8wEr-cn0pI-9JBNyz_hoVlI-p9p71GmwAAAAFMSMrYAA")

BOT_USERNAME = "https://t.me/lightmusicibot"

OWNER = "@light_speedy"

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
    "quiet": True
}

# ==========================================
# START
# ==========================================

@app.on_message(filters.command("start"))
async def start(_, message):

    user = message.from_user

    text = f"""
✨ Hello [{user.first_name}](tg://user?id={user.id})

🎵 This Is **LIGHT MUSIC BOT**

⚡ Fast • Powerful • Professional

🎧 Stream Music In Telegram Voice Chat

━━━━━━━━━━━━━━━
🔥 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add Me",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    "👑 Owner",
                    url="https://t.me/light_speedy"
                ),
                InlineKeyboardButton(
                    "📚 Help",
                    callback_data="help"
                )
            ]
        ]
    )

    await message.reply_photo(
        photo="https://files.catbox.moe/l7m3k9.png",
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# HELP
# ==========================================

@app.on_callback_query(filters.regex("help"))
async def help_menu(_, query):

    text = f"""
📚 **LIGHT MUSIC BOT COMMANDS**

▶️ /play song name
▶️ /vplay video name
▶️ /pause
▶️ /resume
▶️ /skip
▶️ /stop
▶️ /queue

━━━━━━━━━━━━━━━
⚡ Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🔙 Back",
                    callback_data="back"
                )
            ]
        ]
    )

    await query.message.edit_caption(
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# BACK
# ==========================================

@app.on_callback_query(filters.regex("back"))
async def back(_, query):

    user = query.from_user

    text = f"""
✨ Hello [{user.first_name}](tg://user?id={user.id})

🎵 This Is **LIGHT MUSIC BOT**

⚡ Fast • Powerful • Professional

🎧 Stream Music In Telegram Voice Chat

━━━━━━━━━━━━━━━
🔥 Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ Add Me",
                    url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
                )
            ],
            [
                InlineKeyboardButton(
                    "👑 Owner",
                    url="https://t.me/light_speedy"
                ),
                InlineKeyboardButton(
                    "📚 Help",
                    callback_data="help"
                )
            ]
        ]
    )

    await query.message.edit_caption(
        caption=text,
        reply_markup=buttons
    )

# ==========================================
# PLAY
# ==========================================

@app.on_message(filters.command("play"))
async def play(_, message):

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Usage : /play song name"
        )

    query = " ".join(message.command[1:])

    searching = await message.reply_text(
        "🔍 Searching Song..."
    )

    with YoutubeDL(ydl_opts) as ydl:

        info = ydl.extract_info(
            f"ytsearch:{query}",
            download=False
        )

        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]
        duration = info["entries"][0]["duration"]
        thumb = info["entries"][0]["thumbnail"]

    await call_py.join_group_call(
        message.chat.id,
        AudioPiped(url)
    )

    caption = f"""
🎵 **Started Streaming**

━━━━━━━━━━━━━━━

🎧 **Title:** {title}

⏳ **Duration:** {duration} sec

👤 **Requested By:** {message.from_user.mention}

━━━━━━━━━━━━━━━
⚡ Powered By : {OWNER}
━━━━━━━━━━━━━━━
"""

    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "⏸",
                    callback_data="pause"
                ),
                InlineKeyboardButton(
                    "▶️",
                    callback_data="resume"
                ),
                InlineKeyboardButton(
                    "⏭",
                    callback_data="skip"
                ),
                InlineKeyboardButton(
                    "⏹",
                    callback_data="stop"
                )
            ]
        ]
    )

    await message.reply_photo(
        photo=thumb,
        caption=caption,
        reply_markup=buttons
    )

    await searching.delete()

# ==========================================
# BUTTON CONTROLS
# ==========================================

@app.on_callback_query(filters.regex("pause"))
async def pause(_, query):

    await call_py.pause_stream(query.message.chat.id)

    await query.answer(
        "Music Paused"
    )

@app.on_callback_query(filters.regex("resume"))
async def resume(_, query):

    await call_py.resume_stream(query.message.chat.id)

    await query.answer(
        "Music Resumed"
    )

@app.on_callback_query(filters.regex("stop"))
async def stop(_, query):

    await call_py.leave_group_call(
        query.message.chat.id
    )

    await query.answer(
        "Music Stopped"
    )

@app.on_callback_query(filters.regex("skip"))
async def skip(_, query):

    await query.answer(
        "Skipped"
    )

# ==========================================
# COMMAND CONTROLS
# ==========================================

@app.on_message(filters.command("pause"))
async def pause_cmd(_, message):

    await call_py.pause_stream(message.chat.id)

    await message.reply_text(
        "⏸ Music Paused"
    )

@app.on_message(filters.command("resume"))
async def resume_cmd(_, message):

    await call_py.resume_stream(message.chat.id)

    await message.reply_text(
        "▶️ Music Resumed"
    )

@app.on_message(filters.command("stop"))
async def stop_cmd(_, message):

    await call_py.leave_group_call(
        message.chat.id
    )

    await message.reply_text(
        "⏹ Music Stopped"
    )

@app.on_message(filters.command("skip"))
async def skip_cmd(_, message):

    await message.reply_text(
        "⏭ Skipped"
    )

@app.on_message(filters.command("queue"))
async def queue(_, message):

    await message.reply_text(
        "📜 Queue Is Empty"
    )

# ==========================================
# MAIN
# ==========================================

async def main():

    await app.start()

    await assistant.start()

    await call_py.start()

    print("LIGHT MUSIC BOT STARTED")

    await asyncio.Event().wait()

asyncio.run(main())
