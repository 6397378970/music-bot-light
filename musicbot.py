from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types.input_stream import AudioPiped
from yt_dlp import YoutubeDL
import asyncio
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client(
    "musicbot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

call_py = PyTgCalls(app)

ydl_opts = {
    "format": "bestaudio",
    "quiet": True
}

@app.on_message(filters.command("play"))
async def play(_, message):
    if len(message.command) < 2:
        return await message.reply("Usage: /play song")

    query = " ".join(message.command[1:])

    msg = await message.reply("🔍 Searching...")

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=False)
        url = info["entries"][0]["url"]
        title = info["entries"][0]["title"]

    await call_py.join_group_call(
        message.chat.id,
        AudioPiped(url)
    )

    await msg.edit(f"🎵 Playing: {title}")

@app.on_message(filters.command("stop"))
async def stop(_, message):
    await call_py.leave_group_call(message.chat.id)
    await message.reply("⏹ Stopped")

async def main():
    await app.start()
    await call_py.start()
    print("Bot Started")
    await asyncio.Event().wait()

asyncio.run(main())