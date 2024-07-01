import folium

# Функція для додавання шару погоди на карту
def add_weather_layer(map_obj, lat, lon):
    api_key = 'c79c565f3bdb994fb2dbbff8b517ebed'
    url = f"https://tile.openweathermap.org/map/weather_new/{lat}/{lon}/10/10/{api_key}.png"
    layer = folium.TileLayer(url, attr='OpenWeatherMap', name='Weather')
    map_obj.add_child(layer)

# Створення початкової точки карти
map_center = [48.8566, 2.3522]  # Наприклад, Париж

# Ініціалізація карти
mymap = folium.Map(location=map_center, zoom_start=10)

# Додавання шару погоди
add_weather_layer(mymap, map_center[0], map_center[1])

# Відображення карти
mymap.save('weather_map.html')
