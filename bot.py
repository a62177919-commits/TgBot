import telebot
import time

bot = telebot.TeleBot("8305185652:AAHjJn27N7isL89Hb9LWDJC7XrsD4pgTyJM")

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Бот работает на GitHub Actions!")

@bot.message_handler(content_types=['text'])
def echo(message):
    bot.send_message(message.chat.id, message.text)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(3)
