from tgbot.db.db_api import roles, settings


async def create_default_passwords(admin_password: str, user_password: str):
    admin_role = await roles.find_one({'name': 'admin'})
    if not admin_role:
        await roles.insert_one({'name': 'admin',
                                'password': admin_password})

    user_role = await roles.find_one({'name': 'user'})
    if not user_role:
        await roles.insert_one({'name': 'user',
                                'password': user_password})


async def get_instruction() -> str:
    instruction = await settings.find_one({'name': 'instruction'})
    if not instruction:
        await settings.insert_one({'name': 'instruction',
                                   'text': 'Инструкция'})
    instruction = await settings.find_one({'name': 'instruction'})
    return instruction.get('text')
