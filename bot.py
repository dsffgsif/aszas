import os
import re
import threading
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import Message
from yt_dlp import YoutubeDL

# ذخیره کوکی در صورت وجود در تنظیمات رندر
COOKIE_DATA = os.environ.get("YOUTUBE_COOKIES", "")
if COOKIE_DATA:
    with open("cookies.txt", "w", encoding="utf-8") as f:
        f.write(COOKIE_DATA)

# وب‌سرور برای زنده نگه داشتن سرور در رندر
web_app = Flask(__name__)


@web_app.route("/")
def home():
    return "Bot is Running 24/7!"


def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host="0.0.0.0", port=port)


threading.Thread(target=run_web, daemon=True).start()

# دریافت مشخصات تلگرام
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


@app.on_message(filters.command("start"))
async def start_cmd(client: Client, message: Message):
    await message.reply_text("👋 سلام! لینک ویدیو رو بفرست تا برات دانلود کنم.")


@app.on_message(filters.text & ~filters.command(["start"]))
async def download_video(client: Client, message: Message):
    url = message.text.strip()

    if not re.match(r"^https?://", url):
        await message.reply_text("❌ لطفاً یک لینک معتبر بفرستید.")
        return

    status = await message.reply_text("⏳ در حال دریافت و دانلود ویدیو...")

    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "merge_output_format": "mp4",
        "quiet": True,
    }

    # اگر کوکی وجود داشت از آن استفاده کن
    if os.path.exists("cookies.txt"):
        ydl_opts["cookiefile"] = "cookies.txt"

    try:
        os.makedirs("downloads", exist_ok=True)

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)

            if not os.path.exists(file_path):
                file_path = os.path.splitext(file_path)[0] + ".mp4"

            title = info.get("title", "ویدیو")
            duration = int(info.get("duration", 0))

        await status.edit_text("📤 دانلود تمام شد. در حال آپلود به تلگرام...")

        await client.send_video(
            chat_id=message.chat.id,
            video=file_path,
            caption=f"🎬 **{title}**",
            duration=duration,
            supports_streaming=True,
        )

        await status.delete()

        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await status.edit_text(f"❌ خطا در پردازش:\n`{str(e)}`")
        if "file_path" in locals() and os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    print("ربات روشن شد...")
    app.run()
