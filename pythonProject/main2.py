from datetime import datetime
import datetime as dt
import telebot
from telebot import types
import requests
from openai import OpenAI
from weather_translation import weather_translations

bot = telebot.TeleBot('6821604348:AAGOra9sGOqbi7PByMlFFCgCUZdKRGiQbAY')
weather_api = 'c79c565f3bdb994fb2dbbff8b517ebed'
IP_API = 'c27479254248f3'
open_ai_api = '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'
ip_address = '45.12.26.43'
client = OpenAI(api_key=open_ai_api)
model = "gpt-3.5-turbo"

def create_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    button1 = types.KeyboardButton('Дізнатися погоду за моєю геолокацією')
    button2 = types.KeyboardButton('Дізнатися погоду вручну')
    button3 = types.KeyboardButton('Поспілкуватися з WeatherAI')
    button5 = types.KeyboardButton("Розширений пошук")
    button4 = types.KeyboardButton('Прогноз на 3 дні')
    markup.add(button1, button2, button3, button4, button5)
    return markup

def get_city_by_coordinates(latitude, longitude):
    try:
        url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={latitude}&lon={longitude}&limit=1&appid={weather_api}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            city = data[0].get('name', 'Unknown')
            return city
        else:
            return None
    except Exception as e:
        print("Помилка отримання міста за координатами:", e)
        return None

def get_weather_forecast(city, days=3):
    try:
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={weather_api}&units=metric")
        if res.status_code == 200:
            data = res.json()
            forecast = []
            current_date = None
            for weather in data['list']:
                date = weather['dt_txt'].split()[0]
                time = weather['dt_txt'].split()[1]
                if date != current_date and time == "15:00:00":
                    temp = weather['main']['temp']
                    feels_like = weather['main']['feels_like']
                    weather_description = weather['weather'][0]['description']
                    weather_description_uk = weather_translations.get(weather_description, "Невідомо")
                    forecast.append({
                        'date': date,
                        'temp': temp,
                        'feels_like': feels_like,
                        'weather_description': weather_description_uk
                    })
                    current_date = date
                    if len(forecast) == days:
                        break
            return forecast
        else:
            return "Не вдалося отримати прогноз погоди."
    except Exception as e:
        print("Помилка отримання прогнозу погоди:", e)
        return "Виникла помилка при отриманні прогнозу погоди. Будь ласка, спробуйте пізніше."

def get_weather_by_city(city):
    try:
        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api}&units=metric")
        if res.status_code == 200:
            data = res.json()
            if 'main' in data:
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                weather_description = data['weather'][0]['main']
                weather_description_uk = weather_translations.get(weather_description, "Невідомо")
                return f"Погода в місті {city}: \nТемпература: {temp} °C\nВідчувається як: {feels_like} °C\nЗагальний стан погоди: {weather_description_uk}"
            else:
                return "На жаль, не вдається знайти інформацію про погоду для цього міста."
        else:
            return "Такого міста не існує!"
    except Exception as e:
        print("Помилка отримання погодних даних:", e)
        return "Виникла помилка при отриманні погодних даних. Будь ласка, спробуйте пізніше."

def recommend_activity_and_clothing(temp):
    if temp < 10:
        return "Рекомендації: Носіть теплий верхній одяг, шапку та рукавички."
    elif 10 <= temp <= 20:
        return "Рекомендації: Носіть легкий верхній одяг."
    else:
        return "Рекомендації: Носіть легкий одяг."

def recommend_activities(weather_description):
    if 'rain' in weather_description.lower():
        return "Рекомендації: У випадку дощу, краще залишатися всередині або вдягати дощовий одяг."
    else:
        return "Рекомендації: При сонячній та теплій погоді можна планувати прогулянки на свіжому повітрі або заняття спортом."

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привіт! Обери опцію:", reply_markup=create_menu())

def get_weather_by_date_and_city(city, month, day, time="15:00"):
    try:
        res = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={weather_api}&units=metric")
        if res.status_code == 200:
            data = res.json()
            for weather in data['list']:
                forecast_time = dt.datetime.strptime(weather['dt_txt'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
                if forecast_time == time and weather['dt_txt'].split()[0] == f'{dt.datetime.now().year}-{month:02d}-{day:02d}':
                    temp = weather['main']['temp']
                    feels_like = weather['main']['feels_like']
                    weather_description = weather['weather'][0]['description']
                    weather_description_uk = weather_translations.get(weather_description, "Невідомо")
                    return f"Погода в місті {city} на {day}.{month} о {forecast_time}: \nТемпература: {temp} °C\nВідчувається як: {feels_like} °C\nЗагальний стан погоди: {weather_description_uk}"
            return "Не знайдено прогнозу на заданий час."
        else:
            return "Не вдалося отримати прогноз погоди."
    except Exception as e:
        print("Помилка отримання погодного прогнозу:", e)
        return "Виникла помилка при отриманні погодного прогнозу. Будь ласка, спробуйте пізніше."

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == 'Дізнатися погоду за моєю геолокацією':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        button_location = types.KeyboardButton("Надіслати мою геолокацію", request_location=True)
        markup.add(button_location)
        bot.send_message(message.chat.id, "Будь ласка, відправте свою геолокацію, натиснувши на кнопку 'Додати' (прикріпити) у вашому чаті і оберіть 'Місцезнаходження'.", reply_markup=markup)
        bot.send_message(message.chat.id, "Або просто натисніть на кнопку 'Надіслати геолокацію', яка доступна у вашому чаті.")
    elif message.text == 'Дізнатися погоду вручну':
        bot.send_message(message.chat.id, "Введіть назву міста:")
        bot.register_next_step_handler(message, process_manual_city)
    elif message.text == 'Прогноз на 3 дні':
        bot.send_message(message.chat.id, "Ви обрали прогноз на 3 дні. Введіть місто:")
        bot.register_next_step_handler(message, process_manual_city_3days)
    elif message.text == 'Поспілкуватися з WeatherAI':
        bot.send_message(message.chat.id, "Починайте спілкування з WeatherAI!")
        bot.register_next_step_handler(message, handle_weather_ai_conversation)
    elif message.text == 'Розширений пошук':
        bot.send_message(message.chat.id, "Введіть день та місяць щоб дізнатися погоду!")
        bot.register_next_step_handler(message, process_advanced_search)
    else:
        bot.send_message(message.chat.id, "Не розпізнав команду. Виберіть опцію з меню.")

def process_advanced_search(message):
    try:
        parts = message.text.split(' ')
        if len(parts) != 2:
            bot.send_message(message.chat.id, "Введіть день та місяць через пробіл.")
            return
        day, month_input = parts
        month = None
        if month_input.isdigit():
            month = int(month_input)
        else:
            month_names = {
                "січня": 1,
                "лютого": 2,
                "березня": 3,
                "квітня": 4,
                "травня": 5,
                "червня": 6,
                "липня": 7,
                "серпня": 8,
                "вересня": 9,
                "жовтня": 10,
                "листопада": 11,
                "грудня": 12
            }
            month = month_names.get(month_input.lower())
            if not month:
                raise ValueError("Неправильний формат місяця.")
        bot.send_message(message.chat.id, f"Введіть місто для пошуку погоди {day}.{month}:")
        bot.register_next_step_handler(message, lambda msg: process_weather_by_date(msg, month, int(day)))
    except Exception as e:
        bot.send_message(message.chat.id, f"Виникла помилка: {str(e)}")

def process_weather_by_date(message, month, day):
    try:
        city = message.text
        weather_info = get_weather_by_date_and_city(city, month, day)
        bot.send_message(message.chat.id, weather_info)
    except Exception as e:
        bot.send_message(message.chat.id, f"Виникла помилка: {str(e)}")

def handle_weather_ai_conversation(message):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message.text},
            ]
        )
        if response and response.choices:
            reply = response.choices[0].message['content'].strip()
        else:
            reply = 'Ой щось не так!'
    except Exception as e:
        reply = f"Виникла помилка: {str(e)}"

    bot.send_message(message.chat.id, reply)

def process_manual_city_3days(message):
    city = message.text
    forecast = get_weather_forecast(city, days=3)
    if isinstance(forecast, list):
        for day in forecast:
            forecast_date = dt.datetime.strptime(f"{day['date']} 15:00", '%Y-%m-%d %H:%M')
            if forecast_date.time() == dt.time(15, 0):
                bot.send_message(message.chat.id,
                                 f"Погода в місті {city}, Дата: {day['date']}, Температура: {day['temp']}°C, Відчувається як: {day['feels_like']}°C, Погода: {day['weather_description']}")
    else:
        bot.send_message(message.chat.id, forecast)

def process_manual_city(message):
    city = message.text
    weather_info = get_weather_by_city(city)
    bot.send_message(message.chat.id, weather_info)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude
    city_by_coordinates = get_city_by_coordinates(latitude, longitude)
    if city_by_coordinates:
        weather_info = get_weather_by_city(city_by_coordinates)
        bot.send_message(message.chat.id, f"Ви знаходитесь в місті {city_by_coordinates}.")
        bot.send_message(message.chat.id, weather_info)
        temp = weather_info.split('Температура: ')[1].split(' °C')[0]
        weather_description = weather_info.split('Загальний стан погоди: ')[1]
        clothing_recommendation = recommend_activity_and_clothing(float(temp))
        activity_recommendation = recommend_activities(weather_description)
        bot.send_message(message.chat.id, clothing_recommendation)
        bot.send_message(message.chat.id, activity_recommendation)
        bot.send_message(message.chat.id, "Вертаюсь до головного меню.", reply_markup=create_menu())
    else:
        bot.send_message(message.chat.id, "Не вдалося визначити місто за вашою геолокацією. Будь ласка, введіть місто вручну.")

def log_weather_stats(city, weather_info):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open('weather_stats.txt', 'a') as file:
            file.write(f"Дата та час: {current_time}\n{weather_info}\n\n")
    except Exception as e:
        print("Помилка запису до файлу:", e)

def get_city_by_ip(ip_address, IP_API):
    url = f"http://ip-api.com/json/{ip_address}?token={IP_API}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['city']
        else:
            return "Failed to retrieve city information"
    else:
        return "Failed to connect to the IP"

bot.polling(none_stop=True)
