import os
import sys
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest

# Включаем логи
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

logger.info(f"API_ID: {API_ID}")
logger.info(f"API_HASH: {API_HASH[:10]}..." if API_HASH else "API_HASH: empty")
logger.info(f"SESSION_STRING: {SESSION_STRING[:20]}..." if SESSION_STRING else "SESSION_STRING: empty")

if not all([API_ID, API_HASH, SESSION_STRING]):
    logger.error("Missing environment variables!")
    sys.exit(1)

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    logger.info(f"Received /start from {event.sender_id}")
    await event.reply(
        "👋 Привет! Я бот для управления профилем.\n\n"
        "📋 Команды:\n"
        "/setname <имя> - изменить имя\n"
        "/setlastname <фамилия> - изменить фамилию\n"
        "/setphoto - отправь фото с этой командой\n"
        "/delphoto - удалить фото\n"
        "/help - помощь"
    )

@client.on(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.reply(
        "🔧 Команды:\n"
        "/setname Имя\n"
        "/setlastname Фамилия\n"
        "/setphoto (с фото)\n"
        "/delphoto"
    )

@client.on(events.NewMessage(pattern='/setname (.+)'))
async def set_name_handler(event):
    new_name = event.pattern_match.group(1).strip()
    logger.info(f"Setting name to: {new_name}")
    try:
        await client(UpdateProfileRequest(first_name=new_name))
        await event.reply(f"✅ Имя: **{new_name}**")
    except Exception as e:
        logger.error(f"Error setting name: {e}")
        await event.reply(f"❌ {str(e)}")

@client.on(events.NewMessage(pattern='/setlastname (.+)'))
async def set_lastname_handler(event):
    new_lastname = event.pattern_match.group(1).strip()
    logger.info(f"Setting lastname to: {new_lastname}")
    try:
        await client(UpdateProfileRequest(last_name=new_lastname))
        await event.reply(f"✅ Фамилия: **{new_lastname}**")
    except Exception as e:
        logger.error(f"Error setting lastname: {e}")
        await event.reply(f"❌ {str(e)}")

@client.on(events.NewMessage(pattern='/setphoto'))
async def set_photo_handler(event):
    if event.photo:
        logger.info("Setting new photo")
        try:
            path = await event.download_media()
            await client(UploadProfilePhotoRequest(
                file=await client.upload_file(path)
            ))
            os.remove(path)
            await event.reply("✅ Фото обновлено!")
        except Exception as e:
            logger.error(f"Error setting photo: {e}")
            await event.reply(f"❌ {str(e)}")
    else:
        await event.reply("📸 Отправь фото с подписью /setphoto")

@client.on(events.NewMessage(pattern='/delphoto'))
async def delete_photo_handler(event):
    logger.info("Deleting photo")
    try:
        photos = await client.get_profile_photos('me')
        if photos:
            await client(DeletePhotosRequest(photos))
            await event.reply("🗑️ Фото удалено!")
        else:
            await event.reply("ℹ️ Нет фото")
    except Exception as e:
        logger.error(f"Error deleting photo: {e}")
        await event.reply(f"❌ {str(e)}")

async def main():
    logger.info("🤖 Connecting to Telegram...")
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("Session string is invalid or expired!")
            return
            
        logger.info("✅ Connected and authorized!")
        
        # Отправляем себе сообщение что бот запущен
        me = await client.get_me()
        logger.info(f"Logged in as: {me.first_name} (@{me.username})")
        
        # Держим бота запущенным
        logger.info("🟢 Bot is running...")
        await client.run_until_disconnected()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        sys.exit(1)
