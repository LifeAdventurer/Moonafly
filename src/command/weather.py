import textwrap

import requests

import terminal_mode
from command import command_help
from constants import HELP_FLAG


def get_weather_info() -> str:
    latitude = 23.0
    longitude = 120.2

    api_url = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m'

    response = requests.get(api_url)
    data = response.json()
    current_temperature = data['current']['temperature_2m']
    wind_speed = data['current']['wind_speed_10m']
    return textwrap.dedent(
        f"""
        ```
        Current Temperature: {current_temperature}°C
        Wind Speed: {wind_speed} km/h
        ```
        ```
        {terminal_mode.current_path()}
        ```
        """
    )


def get_weather_response(msg: str) -> str:
    if msg.startswith(HELP_FLAG):
        return command_help.load_help_cmd_info('weather')

    if msg == 'get':
        return get_weather_info()
    else:
        return terminal_mode.command_not_found(msg)
