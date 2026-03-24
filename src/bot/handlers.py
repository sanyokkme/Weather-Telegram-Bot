from typing import Callable

from aiogram import F, Router, types
from aiogram.filters import Command, CommandObject
from aiogram.types import BufferedInputFile, Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.api.weather_api import WeatherResponse, get_weather, get_weather_by_coordinates
from src.rendering.weather_card import render_weather_card

router = Router()

START_MESSAGE = "Hello! I'm a weather bot. Use /weather <location> to get the current weather information for a specific location."
LOCATION_BUTTON_TEXT = "Get weather for my location"
LOCATION_FETCH_ERROR = "Sorry, I couldn't fetch the weather information for your location. Please try again later."
LOCATION_USAGE_MESSAGE = "Please provide a location. Usage: /weather <location>"


def build_weather_text(weather_info: WeatherResponse) -> str:
    return (
        f"Weather in {weather_info['location']['name']}, {weather_info['location']['country']}:\n"
        f"Temperature: {weather_info['current']['temp_c']}°C\n"
        f"Condition: {weather_info['current']['condition']['text']}\n"
        f"Humidity: {weather_info['current']['humidity']}%\n"
        f"Wind: {weather_info['current']['wind_kph']} kph\n"
    )


async def send_weather_card(message: Message, weather_info: WeatherResponse) -> None:
    response_message = build_weather_text(weather_info)
    image_bytes = render_weather_card(weather_info)
    weather_image = BufferedInputFile(image_bytes, filename="weather.png")
    await message.answer_photo(photo=weather_image, caption=response_message)


async def fetch_and_send_weather(
    message: Message,
    fetch_weather: Callable[[], WeatherResponse],
    error_message: str,
) -> None:
    try:
        weather_info = fetch_weather()
        await send_weather_card(message, weather_info)
    except Exception:
        await message.answer(error_message)


def build_location_keyboard() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(
        text=LOCATION_BUTTON_TEXT, request_location=True))
    return builder.as_markup(resize_keyboard=True)


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(START_MESSAGE, reply_markup=build_location_keyboard())


@router.message(F.location)
async def handle_location(message: Message) -> None:
    if message.location is None:
        return

    location = message.location

    await fetch_and_send_weather(
        message=message,
        fetch_weather=lambda: get_weather_by_coordinates(
            location.latitude, location.longitude),
        error_message=LOCATION_FETCH_ERROR,
    )


@router.message(Command("weather"))
async def cmd_weather(message: Message, command: CommandObject) -> None:
    location = (command.args or "").strip()
    if not location:
        await message.answer(LOCATION_USAGE_MESSAGE)
        return

    await fetch_and_send_weather(
        message=message,
        fetch_weather=lambda: get_weather(location),
        error_message=f"Sorry, I couldn't fetch the weather information for '{location}'. Please try again later.",
    )
