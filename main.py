from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import asyncio

# --- YOUR CREDENTIALS ---
API_ID = 20175333
API_HASH = "3b543185edc59bc1268baaf9aa4a14c9"
BOT_TOKEN = "8035609232:AAE7rdGsMG47adwLqvMvOjf5B8eptFnzEN8"
WORKER_URL = "https://tgflix.alphamovies.workers.dev"

# --- YOUR LOG CHANNEL ID ---
LOG_CHANNEL = -1003292159300 # 👈 REPLACE THIS WITH YOUR ACTUAL CHANNEL ID

bot = Client("file_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_details(message: Message):
    """Gets file_id and file_name from any media message."""
    if message and message.media:
        media = getattr(message, message.media.value)
        if media:
            return media.file_id, getattr(media, "file_name", "file")
    return None, None

media_filter = filters.private & (filters.video | filters.document | filters.audio | filters.photo)

@bot.on_message(media_filter)
async def handle_file(client, message: Message):
    """Handles all media, gets a new valid file_id, and generates a link."""
    processing_message = await message.reply_text("⏳ Processing...", quote=True)
    
    try:
        # Step 1: Copy the file to the log channel to get a new, valid file_id.
        # This works for both uploads and forwards.
        copied_message = await message.copy(chat_id=LOG_CHANNEL)
        
        # Step 2: THE CRITICAL FIX - Wait 2 seconds for Telegram to process the file.
        await asyncio.sleep(2)
        
        # Step 3: Get the details from the NEW message in the log channel.
        new_file_id, file_name = get_details(copied_message)

        if not new_file_id:
            raise ValueError("Could not get file_id from the copied message.")

        final_url = f"{WORKER_URL}/file/{new_file_id}"
        reply = (
            f"File: {file_name or 'file'}\n\n"
            f"[📥 Download / ▶️ Stream]({final_url})\n\n"
            f"⚠️ *Link works as long as the file exists on Telegram.*"
        )
        await processing_message.edit_text(reply, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

    except Exception as e:
        print(f"❌ An error occurred: {e}")
        await processing_message.edit_text(f"❌ Bot Error: {e}")

@bot.on_message(filters.private & filters.text)
async def handle_text(client, message: Message):
    await message.reply_text("👋 Send or forward any file to get a link.", parse_mode=ParseMode.MARKDOWN)

print("Bot is starting...")
bot.run()