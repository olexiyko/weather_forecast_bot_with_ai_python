from collections import defaultdict
from datetime import datetime

def load_weather_data(file_path):
    """
    Завантажує дані про погоду з файлу.
    """
    weather_data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 4):
            timestamp_str = lines[i].strip().split(': ')[1]
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue  # Пропускаємо цю ітерацію, якщо не можемо розпізнати дату та час
            temperature = float(lines[i + 2].strip().split(': ')[1][:-3])  # Видаляємо символи "°C"
            feels_like = float(lines[i + 3].strip().split(': ')[1][:-3])
            weather_data.append({'timestamp': timestamp, 'temperature': temperature, 'feels_like': feels_like})
    return weather_data

def min_max_temp(file_path='weather_stats.txt'):
    max_temp = None
    min_temp = None
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 4):
            timestamp_str = lines[i].strip().split(': ')[1]
            try:
                timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue  # Пропускаємо цю ітерацію, якщо не можемо розпізнати дату та час
            temperature = float(lines[i + 2].strip().split(': ')[1][:-3])  # Видаляємо символи "°C"
            if max_temp is None or temperature > max_temp:
                max_temp = temperature
            if min_temp is None or temperature < min_temp:
                min_temp = temperature
        print("Максимальна температура:", max_temp)
        print("Мінімальна температура:", min_temp)

def analyze_weather_data_intervals(weather_data, interval_start, interval_end):
    """
    Аналізує дані про погоду та обчислює середню температуру за заданим інтервалом часу.
    """

    interval_temperatures = defaultdict(list)


    for data in weather_data:
        timestamp = data['timestamp']

        if interval_start <= timestamp <= interval_end:
            interval_key = timestamp.replace(minute=0, second=0, microsecond=0)  # Запуск інтервалу
            interval_temperatures[interval_key].append(data['temperature'])

    temperatures_for_interval = []
    for temperatures in interval_temperatures.values():
        temperatures_for_interval.extend(temperatures)

    if temperatures_for_interval:
        average_temperature = sum(temperatures_for_interval) / len(temperatures_for_interval)
    else:
        average_temperature = None

    return average_temperature


def main():
    file_path = 'weather_stats.txt'
    min_max_temp()
    weather_data = load_weather_data(file_path)

    city = input("Введіть місто: ")

    interval_start_str = input("Введіть початок інтервалу (у форматі YYYY-MM-DD HH:MM:SS): ")
    interval_end_str = input("Введіть кінець інтервалу (у форматі YYYY-MM-DD HH:MM:SS): ")

    try:
        interval_start = datetime.strptime(interval_start_str, '%Y-%m-%d %H:%M:%S')
        interval_end = datetime.strptime(interval_end_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print("Неправильний формат дати або часу!")
        return

    average_temperature = analyze_weather_data_intervals(weather_data, interval_start, interval_end)

    if average_temperature is not None:
        print(f"Середня температура у вказаний інтервал часу: {average_temperature:.2f} °C")
    else:
        print("Для вказаного інтервалу часу немає даних про температуру.")


if __name__ == "__main__":
    main()
