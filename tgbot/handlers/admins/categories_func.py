from tgbot.db.db_api import user_categories, users


async def get_category_info(category: dict, current: bool = False):
    _id = category['_id']
    name = category['name']
    count_users = await user_categories.count_documents({'category_id': _id})

    creator_id = category['created_by']
    creator = await users.find_one({'_id': creator_id})
    creator_name = creator['name']
    mention = f'<a href="tg://user?id={creator_id}">{creator_name}</a>'

    text = (f'Категория <b>«{name}»</b>\n'
            f'<b>Создатель:</b> {mention}\n'
            f'<b>Количество пользователей:</b> {count_users}\n\n')

    if current:
        cursor = user_categories.find({'category_id': _id})
        users_in_category = await cursor.to_list(length=None)
        if users_in_category:
            users_text = '<b>Пользователи:</b>\n'
            for index, user in enumerate(users_in_category):
                user_id = user['user_id']
                _user = await users.find_one({'_id': user_id})
                user_name = _user['name']
                mention = f'<a href="tg://user?id={user_id}">{user_name}</a>'
                users_text += f'{index + 1}. {mention}\n'
            text = text + users_text

    return text
