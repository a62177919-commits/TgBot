import os
import sys
import asyncio
import logging
import time
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateStatusRequest, UpdateNotifySettingsRequest
from telethon.tl.functions.users import SetPrivacyRequest
from telethon.tl.types import InputPrivacyKeyStatusTimestamp, InputPrivacyKeyPhoneCall, InputPrivacyKeyChatInvite, InputPrivacyKeyPhoneNumber, InputPrivacyKeyForwards, InputPrivacyKeyProfilePhoto, InputPrivacyKeyPhoneNumber, InputPrivacyValueDisallowAll, InputPrivacyValueAllowAll, InputPeerNotifySettings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_ID = int(os.environ.get('API_ID', 0))
API_HASH = os.environ.get('API_HASH', '')
SESSION_STRING = os.environ.get('SESSION_STRING', '')

if not all([API_ID, API_HASH, SESSION_STRING]):
    logger.error("❌ Missing environment variables!")
    sys.exit(1)

def create_client():
    return TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@events.register(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
        "👋 Привет! Бот для управления профилем.\n\n"
        "📋 Команды:\n"
        "/setname <имя> - изменить имя\n"
        "/setlastname <фамилия> - изменить фамилию\n"
        "/setphoto - отправь фото с этой командой\n"
        "/delphoto - удалить фото\n"
        "/security - 🔒 режим безопасности (очистка профиля)\n"
        "/online - включить онлайн\n"
        "/offline - скрыть онлайн\n"
        "/ping - проверить работу\n"
        "/help - помощь"
    )

@events.register(events.NewMessage(pattern='/help'))
async def help_handler(event):
    await event.reply(
        "🔧 Команды:\n\n"
        "👤 Профиль:\n"
        "/setname Имя\n"
        "/setlastname Фамилия\n"
        "/setphoto (с фото)\n"
        "/delphoto\n\n"
        "🔒 Безопасность:\n"
        "/security - полная очистка профиля\n"
        "/online - показывать онлайн\n"
        "/offline - скрывать онлайн\n\n"
        "📊 Другое:\n"
        "/ping - проверка\n"
        "/help - помощь"
    )

@events.register(events.NewMessage(pattern='/ping'))
async def ping_handler(event):
    await event.reply("🏓 Pong! await event.reply("🏓 Pong! Бот работает.")

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

@events.register(events.NewMessage(pattern='/online'))
async def online_handler(event):
    try:
        await event.client(UpdateStatusRequest(offline=False))
        await event.reply("🟢 Онлайн виден")
    except Exception as e:
        logger.error(f"Error: {e}")
        await event.reply(f"❌ {str(e)}")

@events.register(events.NewMessage(pattern='/offline'))
async def offline_handler(event):
    try:
        await event.client(UpdateStatusRequest(offline=True))
        await event.reply("🔴 Онлайн скрыт")
    except Exception as e:
        logger.error(f"Error: {e}")
        await event.reply(f"❌ {str(e)}")

@events.register(events.NewMessage(pattern='/security'))
async def security_handler(event):
    """Режим безопасности - полная очистка профиля"""
    client = event.client
    results = []
    
    await event.reply("🔒 **Активация режима безопасности...**")
    
    try:
        # 1. Удалить аватарку
        try:
            photos = await client.get_profile_photos('me')
            if photos:
                await client(DeletePhotosRequest(photos))
                results.append("🗑️ Аватарка удалена")
            else:
                results.append("ℹ️ Аватарки не было")
        except Exception as e:
            results.append(f"❌ Ошибка аватарки: {e}")
        
        # 2. Сменить имя на {NULL}
        try:
            await client(UpdateProfileRequest(first_name="{NULL}", last_name=""))
            results.append("👤 Имя изменено на {NULL}")
        except Exception as e:
            results.append(f"❌ Ошибка имени: {e}")
        
        # 3. Удалить username
        try:
            await client(UpdateProfileRequest(username=""))
            results.append("🔗 Username удалён")
        except Exception as e:
            results.append(f"❌ Ошибка username: {e}")
        
        # 4. Удалить био (about)
        try:
            await client(UpdateProfileRequest(about=""))
            results.append("📝 Био очищено")
        except Exception as e:
            results.append(f"❌ Ошибка био: {e}")
        
        # 5. Скрыть онлайн статус
        try:
            await client(SetPrivacyRequest(
                key=InputPrivacyKeyStatusTimestamp(),
                rules=[InputPrivacyValueDisallowAll()]
            ))
            results.append("👻 Онлайн скрыт для всех")
        except Exception as e:
            results.append(f"❌ Ошибка скрытия онлайна: {e}")
        
        # 6. Отключить звонки от всех
        try:
            await client(SetPrivacyRequest(
                key=InputPrivacyKeyPhoneCall(),
                rules=[InputPrivacyValueDisallowAll()]
            ))
            results.append("📞 Звонки отключены")
        except Exception as e:
            results.append(f"❌ Ошибка звонков: {e}")
        
        # 7. Запретить пересылку сообщений
        try:
            await client(SetPrivacyRequest(
                key=InputPrivacyKeyForwards(),
                rules=[InputPrivacyValueDisallowAll()]
            ))
            results.append("↪️ Пересылка запрещена")
        except Exception as e
