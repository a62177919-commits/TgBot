import telebot
import time
import random

BOT_TOKEN = "8305185652:AAHjJn27N7isL89Hb9LWDJC7XrsD4pgTyJM"

bot = telebot.TeleBot(BOT_TOKEN)

# --- БАЗОВЫЕ ПАТТЕРНЫ ДЛЯ ИМИТАЦИИ ИИ ---

def generate_ai_answer(text):
    text = text.lower()

    # 1. Ответы на вопросы "что такое"
    if "что такое" in text:
        obj = text.replace("что такое", "").strip()
        return f"{obj.capitalize()} — это интересная тема. Если коротко, это понятие описывает определённый объект или явление. Если хочешь, могу объяснить подробнее."

    # 2. Ответы на "как работает"
    if "как работает" in text:
        obj = text.replace("как работает", "").strip()
        return f"Работа {obj} основана на нескольких принципах. Обычно это включает логику, последовательность действий и взаимодействие компонентов. Могу разобрать по шагам."

    # 3. Ответы на "почему"
    if "почему" in text:
        return "Причин может быть несколько. Обычно это связано с логикой процесса, внешними факторами или особенностями системы."

    # 4. Ответы на "как сделать"
    if "как сделать" in text:
        return "Чтобы это сделать, нужно разбить задачу на шаги. Начни с простого, затем усложняй. Могу подсказать конкретный план."

    # 5. Ответы на приветствия
    if any(word in text for word in ["привет", "здрав", "ку", "хай"]):
        return random.choice([
            "Привет! Готов помочь.",
            "Здравствуй! Что хочешь узнать?",
            "Хай! Я тут, спрашивай."
        ])

    # 6. Ответы на прощания
    if any(word in text for word in ["пока", "до свид", "увид"]):
        return "До встречи! Если что — пиши."

    # 7. Если ничего не подошло — умный универсальный ответ
    return random.choice([
        "Интересная мысль. Могу объяснить подробнее, если уточнишь.",
        "Хороший вопрос. Давай разберёмся вместе.",
        "Это звучит любопытно. Хочешь, дам подробный разбор?",
        "Понимаю, о чём ты. Могу объяснить глубже."
    ])

# --- ОБРАБОТЧИКИ ---

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я автономный ИИ‑бот. Работает без API, всегда онлайн.")

@bot.message_handler(content_types=['text'])
def ai(message):
    user_text = message.text
    answer = generate_ai_answer(user_text)
    bot.send_message(message.chat.id, answer)

# --- БЕСКОНЕЧНЫЙ ЦИКЛ ---

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print("Ошибка:", e)
        time.sleep(3)
