import misc
import asyncio
import logging
from handlers import router
import db
import art

async def main():
    art.tprint("Luxury Plus")
    art.tprint("SIZE Bot")
    print("Starting bot...")
    print("Initializing database...")
    db.init_db()
    print("BOT STARTED")
    print("\n\n")
    misc.dp.include_router(router)
    await misc.bot.delete_webhook(drop_pending_updates=True)
    await misc.dp.start_polling(misc.bot, allowed_updates=misc.dp.resolve_used_update_types())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())