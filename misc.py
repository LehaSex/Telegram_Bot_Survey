from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import os
from dotenv import load_dotenv
from storage import SQLiteStorage
import sys

abs_pth = os.path.abspath(sys.argv[0])

# .env file path
env_path = os.path.join(os.path.dirname(abs_pth), ".env")

load_dotenv(env_path)
# os go to dir sys.argv[0]
# create photo folder
if not os.path.exists("photos"):
    os.makedirs("photos")

# create video folder
if not os.path.exists("videos"):
    os.makedirs("videos")

# create audio folder
if not os.path.exists("audios"):
    os.makedirs("audios")

# create document folder
if not os.path.exists("documents"):
    os.makedirs("documents")

# check if .env file exists
if not os.path.exists(".env"):
    print("Please create .env file with BOT_TOKEN, BOT_NAME, DB_NAME, CHANNEL_ID and CHANNEL_LINK variables")
    exit()

# check if BOT_TOKEN is set
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher(storage=SQLiteStorage())
bot_name = os.getenv("BOT_NAME")
db_name = os.getenv("DB_NAME")
channel_id = os.getenv("CHANNEL_ID")
channel_link = os.getenv("CHANNEL_LINK")