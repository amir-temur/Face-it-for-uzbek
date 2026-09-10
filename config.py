import os
from dotenv import load_dotenv

load_dotenv()

# Telegram bot tokeni (@BotFather dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Faceit Web API kaliti (faceit.com developer portalidan olinadi)
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY", "")

# E'lonlar chiqadigan kanal yoki guruh ID'si (masalan -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# Admin telegram ID'lari, vergul bilan ajratilgan: "12345,67890"
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()]

# Bitta foydalanuvchi nechchi daqiqada bitta lobbi e'lon qila oladi
LOBBY_COOLDOWN_MINUTES = int(os.getenv("LOBBY_COOLDOWN_MINUTES", "15"))

# SQLite fayl manzili
DB_PATH = os.getenv("DB_PATH", "bot.db")

# Qaysi o'yin: "cs2" yoki "csgo" (Faceit API'dagi kalit nomi)
FACEIT_GAME_KEY = os.getenv("FACEIT_GAME_KEY", "cs2")
