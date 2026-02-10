import telebot
import requests
import time
import os

BOT_TOKEN = "8305185652:AAHjJn27N7isL89Hb9LWDJC7XrsD4pgTyJM"
DEEPSEEK_KEY = "sk-fd79b474893f4632bb5042ec116d85ad"

bot = telebot.TeleBot(BOT_TOKEN)

def ask_deepseek(prompt):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_KEY}"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, json=data, headers=headers)
    result = response.json()

    try:
        return result["choices"][0]["message"]["content"]
    except:
        return "Ошибка DeepSeek API."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я ИИ‑бот на DeepSeek. Задавай вопросы.")

@bot.message_handler(content_types=['text'])
def ai(message):
    user_text = message.text
    answer = ask_deepseek(user_text)
    bot.send_message(message.chat.id, answer)

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(3)
