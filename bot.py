import os
import sys
import asyncio
import logging
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.errors import AuthKeyDuplicatedError, PhoneNumberInvalidError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

logger.info(f"API_ID: {API_ID}")
logger.info(f"API_HASH present: {bool(API_HASH)}")
logger.info(f"SESSION_STRING present: {bool(SESSION_STRING)}")

if not all([API_ID, API_HASH, SESSION_STRING]):
    logger.error("❌ Missing environment variables!")
    logger.error(f"API_ID: {API_ID}")
    logger.error(f"API_HASH: {'set' if API_HASH else 'NOT SET'}")
    logger.error(f"SESSION_STRING: {'set' if SESSION_STRING else 'NOT SET'}")
    sys.exit(1)

def create_client():
    return TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 Привет! Я бот для управления профилем.\n\n"
        "📋 Команды:\n"
        "/setname <имя> - изменить имя\n"
        "/setlastname <фамилия> - изменить фамилию\n"
        "/setphoto - отправь фото с этой командой\n"
        "/delphoto - удалить фото\n"
        "/ping - проверить работу\n"
        "/help - помощь"
    )

@events.register(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    await event.reply("🏓 Pong! Бот работает.")

@events.register(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.reply(
        "🔧 Команды:\n"
        "/setname Имя\n"
        "/setlastname Фамилия\n"
        "/setphoto (с фото)\n"
        "/delphoto\n"
        "/ping"
    )

@events.register(events.NewMessage(pattern='/setname (.+)'))
async def set_name_handler(event):
    new_name = event.pattern_match.group(1).strip()
    try:
        await event.client(UpdateProfileRequest(first_name=new_name))
        await event.reply(f"✅ Имя: **{new_name}**")
    except Exception as e:
        logger.error(f"Error: {e}")
        await event.reply(f"❌ {str(e)}")

@events.register(events.NewMessage(pattern='/setlastname (.+)'))
async def set_lastname_handler(event):
    new_lastname = event.pattern_match.group(1).strip()
    try:
        await event.client(UpdateProfileRequest(last_name=new_lastname))
        await event.reply(f"✅ Фамилия: **{new_lastname}**")
    except Exception as e:
        logger.error(f"Error: {e}")
        await event.reply(f"❌ {str(e)}")

@events.register(events.NewMessage(pattern='/setphoto'))
async def set_photo_handler(event):
    if event.photo:
        try:
            path = await event.download_media()
            await event.client(UploadProfilePhotoRequest(
                file=await event.client.upload_file(path)
            ))
            os.remove(path)
            await event.reply("✅ Фото обновлено!")
        except Exception as e:
            logger.error(f"Error: {e}")
            await event.reply(f"❌ {str(e)}")
    else:
        await event.reply("📸 Отправь фото с подписью /setphoto")

@events.register(events.NewMessage(pattern='/delphoto'))
async def delete_photo_handler(event):
    try:
        photos = await event.client.get_profile_photos('me')
        if photos:
            await event.client(DeletePhotosRequest(photos))
            await event.reply("🗑️ Фото удалено!")
        else:
            await event.reply("ℹ️ Нет фото")
    except Exception as e:
        logger.error(f"Error: {e}")
        await event.reply(f"❌ {str(e)}")

async def run_bot():
    client = create_client()
    
    # Регистрируем обработчики
    client.add_event_handler(start_handler)
    client.add_event_handler(ping_handler)
    client.add_event_handler(help_handler)
    client.add_event_handler(set_name_handler)
    client.add_event_handler(set_lastname_handler)
    client.add_event_handler(set_photo_handler)
    client.add_event_handler(delete_photo_handler)
    
    try:
        logger.info("🔄 Connecting...")
        await client.connect()
        
        if not await client.is_user_authorized():
            logger.error("❌ Session invalid!")
            return False
            
        me = await client.get_me()
        logger.info(f"✅ Logged in as: {me.first_name} (@{me.username})")
        
        # Отправляем себе сообщение о запуске
        try:
            await client.send_message('me', f'🤖 Бот запущен! Время: {time.strftime("%H:%M:%S")}')
        except:
            pass
        
        logger.info("🟢 Bot is running...")
        await client.run_until_disconnected()
        logger.info("🔴 Disconnected")
        return True
        
    except AuthKeyDuplicatedError:
        logger.error("❌ Session used elsewhere!")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False
    finally:
        await client.disconnect()

async def main():
    restart_count = 0
    max_restarts = 100  # Бесконечно почти
    
    while restart_count < max_restarts:
        restart_count += 1
        logger.info(f"=== Попытка #{restart_count} ===")
        
        success = await run_bot()
        
        if not success:
            logger.info("⏳ Перезапуск через 10 секунд...")
            await asyncio.sleep(10)
        else:
            logger.info("⏳ Переподключение через 5 секунд...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Stopped by user")
    except Exception as e:
        logger.error(f"Fatal: {e}")
        sys.exit(1)
