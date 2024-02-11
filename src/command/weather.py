import textwrap

import requests

import terminal_mode


def get_weather_info() -> str:

    # TODO: search the input place and get the latitude and longitude
    latitude = 23.0
    longitude = 120.2

    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m'

    response = requests.get(api_url)
    data = response.json()
    current_temperature = data['current']['temperature_2m']
    wind_speed = data['current']['wind_speed_10m']
    return textwrap.dedent(
        f"""\
        ```
        Current Temperature: {current_temperature}°C
        Wind Speed: {wind_speed} km/h
        {terminal_mode.current_path()}
        ```
    """
    )
