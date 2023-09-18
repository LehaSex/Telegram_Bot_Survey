from aiogram import types
from misc import channel_link

def get_yes_no():
    buttons = [
        [
            types.InlineKeyboardButton(text="Я только за", callback_data="callback_yes"),
            types.InlineKeyboardButton(text="Давай потом", callback_data="callback_maybe")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def persuade():
    buttons = [
        [
            types.InlineKeyboardButton(text="Да, давай", callback_data="callback_yes"),
            types.InlineKeyboardButton(text="Нет, не хочу", callback_data="callback_no")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def come_back():
    buttons = [
        [
            types.InlineKeyboardButton(text="Вернуться", callback_data="callback_yes")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
def come_back2():
    buttons = [
        [
            types.InlineKeyboardButton(text="Вернуться", callback_data="show_data")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def check_button():
    buttons = [
        [
            types.InlineKeyboardButton(text="Ссылка на канал", url=channel_link)
        ],
        [
            types.InlineKeyboardButton(text="Проверить подписку", callback_data="callback_sub")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def show_data():
    buttons = [
        [
            types.InlineKeyboardButton(text="Скорей показывай", callback_data="show_data")
        ],
        [
            types.InlineKeyboardButton(text="Позже гляну", callback_data="callback_dontshow")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_menu(var: bool = False):
    # check if user superadmin
    if var:
        buttons = [
            [
                types.InlineKeyboardButton(text="➕📖Добавить материал", callback_data="admin_material_add")
            ],
            [
                types.InlineKeyboardButton(text="➖📖Удалить материал", callback_data="admin_material_delete_list"),
                types.InlineKeyboardButton(text="✏📖Изменить материал", callback_data="admin_material_edit_list")
            ],
            [
                types.InlineKeyboardButton(text="👀📖Просмотреть материалы", callback_data="admin_material_show")
            ],
            [
                types.InlineKeyboardButton(text="➕❓Добавить вопрос", callback_data="admin_question_text_add")
            ],
            [
                types.InlineKeyboardButton(text="➖❓Удалить вопрос", callback_data="admin_question_delete_list"),
                types.InlineKeyboardButton(text="✏❓Изменить вопрос", callback_data="admin_question_edit_list")
            ],
            [
                types.InlineKeyboardButton(text="👀❓Просмотреть вопросы", callback_data="admin_question_show_list")
            ],
            [
                types.InlineKeyboardButton(text="⤴📗Экспортировать данные в Excel", callback_data="admin_export_excel")
            ],
            [
                types.InlineKeyboardButton(text="✏🔒Управление администраторами", callback_data="admin_admin_menu")
            ],
        ]
    else:
        buttons = [
            [
                types.InlineKeyboardButton(text="➕📖Добавить материал", callback_data="admin_material_add")
            ],
            [
                types.InlineKeyboardButton(text="➖📖Удалить материал", callback_data="admin_material_delete_list"),
                types.InlineKeyboardButton(text="✏📖Изменить материал", callback_data="admin_material_edit_list")
            ],
            [
                types.InlineKeyboardButton(text="👀📖Просмотреть материалы", callback_data="admin_material_show")
            ],
            [
                types.InlineKeyboardButton(text="➕❓Добавить вопрос", callback_data="admin_question_text_add")
            ],
            [
                types.InlineKeyboardButton(text="➖❓Удалить вопрос", callback_data="admin_question_delete_list"),
                types.InlineKeyboardButton(text="✏❓Изменить вопрос", callback_data="admin_question_edit_list")
            ],
            [
                types.InlineKeyboardButton(text="👀❓Просмотреть вопросы", callback_data="admin_question_show_list")
            ],
            [
                types.InlineKeyboardButton(text="⤴📗Экспортировать данные в Excel", callback_data="admin_export_excel")
            ],
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_back():
    buttons = [
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_back_or_skip(callback_data : str):
    buttons = [
        [
            types.InlineKeyboardButton(text="Пропустить", callback_data=callback_data)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_correct_or_not(callback_data : str, callback_data2 : str):
    buttons = [
        [
            types.InlineKeyboardButton(text="✅Всё верно", callback_data=callback_data),
            types.InlineKeyboardButton(text="❌Не верно", callback_data=callback_data2)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_audio_video_document(callback_data : str, callback_data2 : str, callback_data3 : str, callback_data4 : str):
    buttons = [
        [
            types.InlineKeyboardButton(text="🎥Видео", callback_data=callback_data),
            types.InlineKeyboardButton(text="🎧Аудио", callback_data=callback_data2),
            types.InlineKeyboardButton(text="📄Документ", callback_data=callback_data3)
        ],
        [
            types.InlineKeyboardButton(text="Пропустить", callback_data=callback_data4)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],

    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_publish(callback_data: str):
    buttons = [
        [
            types.InlineKeyboardButton(text="Опубликовать", callback_data=callback_data)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_delete(callback_data: str):
    if callback_data != "x":
        buttons = [
            [
                types.InlineKeyboardButton(text="Подтвердить", callback_data=callback_data)
            ],
            [
                types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
            ],
        ]
    else:
        buttons = [
            [
                types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
            ],
        ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_edit(text : str,callback_data1: str, callback_data2: str, callback_data3: str, callback_data4: str, callback_data5: str, callback_data6):
    buttons = [
        [
            types.InlineKeyboardButton(text="Изменить текст", callback_data=callback_data1)
        ],
        [
            types.InlineKeyboardButton(text="Изменить фото", callback_data=callback_data2)
        ],
        [
            types.InlineKeyboardButton(text="Изменить аудио", callback_data=callback_data3)
        ],
        [
            types.InlineKeyboardButton(text="Изменить видео", callback_data=callback_data4)
        ],
        [
            types.InlineKeyboardButton(text="Изменить документ", callback_data=callback_data5)
        ],
        [
            types.InlineKeyboardButton(text=text, callback_data=callback_data6)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_delete_or_return(callback_data1: str, callback_data2: str):
    buttons = [
        [
            types.InlineKeyboardButton(text="Удалить", callback_data=callback_data1)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data=callback_data2)
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_edit_question(callback_data1: str, callback_data2: str, callback_data3: str):
    buttons = [
        [
            types.InlineKeyboardButton(text="Изменить текст", callback_data=callback_data1)
        ],
        [
            types.InlineKeyboardButton(text="Изменить ответы", callback_data=callback_data2)
        ],
        [
            types.InlineKeyboardButton(text="Изменить фото", callback_data=callback_data3)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def admin_admin_menu(callback_data1: str, callback_data2: str, callback_data3: str):
    buttons = [
        [
            types.InlineKeyboardButton(text="➕Добавить администратора", callback_data=callback_data1)
        ],
        [
            types.InlineKeyboardButton(text="➖Удалить администратора", callback_data=callback_data2)
        ],
        [
            types.InlineKeyboardButton(text="👀Просмотреть администраторов", callback_data=callback_data3)
        ],
        [
            types.InlineKeyboardButton(text="Вернуться в меню", callback_data="admin_back")
        ],
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard