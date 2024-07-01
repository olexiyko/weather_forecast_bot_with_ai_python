import telebot
from openai import OpenAI

bot = telebot.TeleBot('6821604348:AAGOra9sGOqbi7PByMlFFCgCUZdKRGiQbAY')
client = OpenAI(api_key='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')
model = "gpt-3.5-turbo"

@bot.message_handler(commands=['start'])
def hello(message):
    bot.send_message(message.chat.id, 'Привіт, я твій ChatGPT бот')

@bot.message_handler(content_types=['text'])
def main(message):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text},
            ]
        )
        if response and response.choices:
            reply = response.choices[0].text.strip()
        else:
            reply = 'Ой щось не так!'
    except Exception as e:
        reply = f"Виникла помилка: {str(e)}"
    bot.send_message(message.chat.id, reply)

bot.polling(none_stop=True)
