import asyncio
from typing import Any

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandObject
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import Message

from config.bot_configuration import Config
from src.api.weather_api import get_weather, get_weather_by_coordinates

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
polling_task: asyncio.Task[None] | None = None


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:

    builder = ReplyKeyboardBuilder()

    builder.row(types.KeyboardButton(
        text="Get weather for my location", request_location=True))

    await message.answer(f"Hello! I'm a weather bot. Use /weather <location> to get the current weather information for a specific location.", reply_markup=builder.as_markup(resize_keyboard=True))


@dp.message(F.location)
async def handle_location(message: Message) -> None:
    """Обробляє повідомлення з локацією користувача"""
    if message.location is None:
        return

    try:
        weather_info = get_weather_by_coordinates(
            message.location.latitude, message.location.longitude)
        response_message = (
            f"Weather in {weather_info['location']['name']}, {weather_info['location']['country']}:\n"
            f"Temperature: {weather_info['current']['temp_c']}°C\n"
            f"Condition: {weather_info['current']['condition']['text']}\n"
            f"Humidity: {weather_info['current']['humidity']}%\n"
            f"Wind: {weather_info['current']['wind_kph']} kph\n"
        )
        await message.answer(response_message)
    except Exception:
        await message.answer("Sorry, I couldn't fetch the weather information for your location. Please try again later.")


@dp.message(Command("weather"))
async def cmd_weather(message: Message, command: CommandObject) -> None:
    location = (command.args or "").strip()
    if not location:
        await message.answer("Please provide a location. Usage: /weather <location>")
        return

    try:
        weather_info = get_weather(location)
        response_message = (
            f"Weather in {weather_info['location']['name']}, {weather_info['location']['country']}:\n"
            f"Temperature: {weather_info['current']['temp_c']}°C\n"
            f"Condition: {weather_info['current']['condition']['text']}\n"
            f"Humidity: {weather_info['current']['humidity']}%\n"
            f"Wind: {weather_info['current']['wind_kph']} kph\n"
        )
        await message.answer(response_message)
    except Exception:
        await message.answer(f"Sorry, I couldn't fetch the weather information for '{location}'. Please try again later.")


async def main():
    await dp.start_polling(bot)


async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    global polling_task

    if scope.get("type") == "lifespan":
        while True:
            message = await receive()

            if message["type"] == "lifespan.startup":
                polling_task = asyncio.create_task(main())
                await send({"type": "lifespan.startup.complete"})

            elif message["type"] == "lifespan.shutdown":
                if polling_task is not None:
                    polling_task.cancel()
                    try:
                        await polling_task
                    except asyncio.CancelledError:
                        pass
                await bot.session.close()
                await send({"type": "lifespan.shutdown.complete"})
                return

    if scope.get("type") != "http":
        return

    body = b"ASGI app is running. Start bot polling with: python3 main.py"
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [(b"content-type", b"text/plain; charset=utf-8")],
        }
    )
    await send({"type": "http.response.body", "body": body})

if __name__ == "__main__":
    asyncio.run(main())
