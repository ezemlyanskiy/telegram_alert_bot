import os

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID')

# List of user IDs for DM alerts (integers or strings)
DM_USERS = os.getenv("TELEGRAM_DM_USERS", "").split(",")
