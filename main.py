import asyncio
from typing import Any

from aiogram import Bot, Dispatcher

from config.bot_configuration import Config
from src.bot.handlers import router

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)
polling_task: asyncio.Task[None] | None = None


async def main() -> None:
    await dp.start_polling(bot)


async def shutdown_bot_polling() -> None:
    if polling_task is None:
        return

    polling_task.cancel()
    try:
        await polling_task
    except asyncio.CancelledError:
        pass


async def handle_lifespan(receive: Any, send: Any) -> None:
    global polling_task

    while True:
        message = await receive()

        if message["type"] == "lifespan.startup":
            polling_task = asyncio.create_task(main())
            await send({"type": "lifespan.startup.complete"})

        elif message["type"] == "lifespan.shutdown":
            await shutdown_bot_polling()
            await bot.session.close()
            await send({"type": "lifespan.shutdown.complete"})
            return


async def app(scope: dict[str, Any], receive: Any, send: Any) -> None:
    if scope.get("type") == "lifespan":
        await handle_lifespan(receive, send)
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
