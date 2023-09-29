from motor.motor_asyncio import AsyncIOMotorClient

from tgbot.config import config

client = AsyncIOMotorClient(host=config.db.host,
                            port=config.db.port)

db = client[config.db.name]

roles = db['roles']
categories = db['categories']
users = db['users']
user_categories = db['user_categories']

settings = db['settings']

dialogs = db['dialogs']
