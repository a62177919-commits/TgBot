import os
import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
SESSION_STRING = os.environ['SESSION_STRING']

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)

@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.reply(
       (event):
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
    try:
        await client(UpdateProfileRequest(first_name=new_name))
        await event.reply(f"✅ Имя: **{new_name}**")
    except Exception as e:
        await event.reply(f"❌ {str(e)}")

@client.on(events.NewMessage(pattern='/setlastname (.+)'))
async def set_lastname_handler(event):
    new_lastname = event.pattern_match.group(1).strip()
    try:
        await client(UpdateProfileRequest(last_name=new_lastname))
        await event.reply(f"✅ Фамилия: **{new_lastname}**")
    except Exception as e:
        await event.reply(f"❌ {str(e)}")

@client.on(events.NewMessage(pattern='/setphoto'))
async def set_photo_handler(event):
    if event.photo:
        try:
            path = await event.download_media()
            await client(UploadProfilePhotoRequest(
                file=await client.upload_file(path)
            ))
            os.remove(path)
            await event.reply("✅ Фото обновлено!")
        except Exception as e:
            await event.reply(f"❌ {str(e)}")
    else:
        await event.reply("📸 Отправь фото с подписью /setphoto")

@client.on(events.NewMessage(pattern='/delphoto'))
async def delete_photo_handler(event):
    try:
        photos = await client.get_profile_photos('me')
        if photos:
            await client(DeletePhotosRequest(photos))
            await event.reply("🗑️ Фото удалено!")
        else:
            await event.reply("ℹ️ Нет фото")
    except Exception as e:
        await event.reply(f"❌ {str(e)}")

async def main():
    print("🤖 Бот запускается...")
    await client.start()
    print("✅ Бот работает!")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
