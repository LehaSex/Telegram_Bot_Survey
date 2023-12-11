from uuid import uuid4
from aiogram import types, F, Router
from aiogram.types import Message, MessageEntity, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from misc import bot_name, channel_id, bot
import db
from keyboards import *
import json
import os
from excel_exporter import export_excel
from aiogram.utils.formatting import Code, Text


router = Router()

# admin check 
def is_admin(chat_id):
    try:
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT is_admin FROM users WHERE chat_id = ?", (chat_id,))
        user = db_cursor.fetchone()
        db_cursor.close()
        if user[0] == 1 or user[0] == 2:
            return True
        else:
            return False       
    except:
        return False 

async def get_username_by_chat_id(chat_id):
    # telegram api
    try:
        user = await bot.get_chat(chat_id)
        if user.username is None:
            return user.first_name
        else:
            return "@" + user.username
    except:
        # find in db
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
        user = db_cursor.fetchone()
        db_cursor.close()
        if user is None:
            return "Неизвестный пользователь"
        elif user[4] is None:
            return user[2]
        else:
            return "@" + user[4]
    

def check_superadmin(chat_id):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT is_admin FROM users WHERE chat_id = ?", (chat_id,))
    user = db_cursor.fetchone()
    db_cursor.close()
    if user[0] == 2:
        return True
    else:
        return False

def get_count_of_questions():
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT COUNT(*) FROM questions")
    count = db_cursor.fetchone()
    db_cursor.close()
    return int(count[0])

async def check_subscription(user_id):
    try:
        
        member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
        if member.status == "member"  or member.status == "creator" or member.status == "administrator":
            return True
        else:
            return False
    except:
        return False

def get_next_question_id(question_id):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT id FROM questions WHERE id > ? ORDER BY id ASC LIMIT 1", (question_id,))
    question = db_cursor.fetchone()
    db_cursor.close()
    if question is None:
        return None
    else:
        return int(question[0])

def get_question_text(question_id):
    try:
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT question_text FROM questions WHERE id = ?", (question_id,))
        question = db_cursor.fetchone()
        db_cursor.close()
        return question[0]
    except:
        return "Вопросов нет"

def get_question_photo(question_id):
    try:
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT question_photo FROM questions WHERE id = ?", (question_id,))
        question = db_cursor.fetchone()
        db_cursor.close()
        if question[0] is None or question[0] == "":
            return None
        else:
            try:
                # check is file exists
                if os.path.exists("photos/" + question[0]):
                    return FSInputFile("photos/" + question[0])
                else:
                    return None
            except:
                return None
    except:
        return None

def get_question_answers(question_id):
    try:
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT question_answers FROM questions WHERE id = ?", (question_id,))
        question = db_cursor.fetchone()
        db_cursor.close()
        json_answers = json.loads(question[0])
        return json_answers   
    except:
        return None     

def get_smart_column_count(question_id):
    answers = get_question_answers(question_id)
    for i in answers:
        if len(i) > 19:
            return 1
    return 2

#[{"type": "spoiler", "offset": 0, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "bold", "offset": 1, "length": 2, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "underline", "offset": 3, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "underline", "offset": 4, "length": 2, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "bold", "offset": 4, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "italic", "offset": 4, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "underline", "offset": 8, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "spoiler", "offset": 8, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "bold", "offset": 9, "length": 2, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "spoiler", "offset": 9, "length": 2, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "underline", "offset": 11, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "italic", "offset": 12, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "code", "offset": 13, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}, {"type": "bold", "offset": 14, "length": 1, "url": null, "user": null, "language": null, "custom_emoji_id": null}]
def get_question_entity(question_id):
    try:
        msg_ent : types.List[MessageEntity] = []
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT question_text_ent FROM questions WHERE id = ?", (question_id,))
        question = db_cursor.fetchone()
        db_cursor.close()
        if question[0] is None:
            return None
        else:
            json_quest = json.loads(question[0])
            # add attributes from json to MessageEntity
            for i in json_quest:
                msg_ent.append(MessageEntity(type=i["type"], offset=i["offset"], length=i["length"], url=i["url"], user=i["user"], language=i["language"], custom_emoji_id=i["custom_emoji_id"]))
            return msg_ent 
    except:
        return None       
    
def json_to_msg_ent(json_quest):
    msg_ent : types.List[MessageEntity] = []
    json_quest = json.loads(json_quest)
    # add attributes from json to MessageEntity
    for i in json_quest:
        msg_ent.append(MessageEntity(type=i["type"], offset=i["offset"], length=i["length"], url=i["url"], user=i["user"], language=i["language"], custom_emoji_id=i["custom_emoji_id"]))
    return msg_ent

def build_question_keyboard(question_id, column_count=2):
    try:
        buttons = []
        # json answers
        answers = get_question_answers(question_id)
        # get count of answers json
        answers_count = len(answers)
        # divide answers into columns
        for i in range(0, answers_count, column_count):
            buttons.append([])
            for j in range(column_count):
                if i + j < answers_count:
                    buttons[i // column_count].append(types.InlineKeyboardButton(text=answers[i + j], callback_data="question_" + str(question_id) + "_" + answers[i + j]))
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
        return keyboard  
    except:
        return None      

def build_question_preview_keyboard(questions : list, column_count=2):
    buttons = []
    for i in range(0, len(questions), column_count):
        buttons.append([])
        for j in range(column_count):
            if i + j < len(questions):
                buttons[i // column_count].append(types.InlineKeyboardButton(text=questions[i + j], callback_data="question_preview_" + str(questions[i + j])))
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def get_username(chat_id):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT nominal_name FROM users WHERE chat_id = ?", (chat_id,))
    user = db_cursor.fetchone()
    db_cursor.close()
    return user[0]

class BotQuests(StatesGroup):
    choosing_username = State()
    questions_complete = State()

class AdminActions(StatesGroup):
    admin_material_add = State()
    admin_material_add_image = State()
    admin_material_add_audio = State()
    admin_material_add_video = State()
    admin_material_add_document = State()
    admin_material_add_answer = State()
    admin_material_delete = State()
    admin_material_edit = State()
    admin_material_edit_text = State()
    admin_material_edit_image = State()
    admin_material_edit_audio = State()
    admin_material_edit_video = State()
    admin_material_edit_document = State()
    admin_material_edit_answer = State()
    admin_material_show = State()
    admin_question_add = State()
    admin_question_add_answers = State()
    admin_question_add_image = State()
    admin_question_delete = State()
    admin_question_edit = State()
    admin_question_edit_text = State()
    admin_question_edit_answers = State()
    admin_question_edit_image = State()
    admin_question_show = State()
    admin_admin_add = State()
    admin_admin_delete = State()
    admin_admin_show = State()

@router.message(Command("admin"))
async def admin_handler(msg: Message):
    if is_admin(msg.from_user.id):
        await msg.answer("Вы вошли в админ меню!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(msg.from_user.id)))
    else:
        await msg.answer("Не знаю такую команду")

@router.callback_query(F.data.startswith("admin_"))
async def admin_actions(callback: types.CallbackQuery, state: FSMContext):
    if is_admin(callback.from_user.id): 
        subject = callback.data.split("_")[1]
        if subject == "material":
            action = callback.data.split("_")[2]
            if action == "add":
                await callback.message.edit_text("Введите текст материала", reply_markup=admin_back())
                await state.set_state(AdminActions.admin_material_add)
            elif action == "delete":
                action = callback.data.split("_")[3]
                # списко материалов
                if action == "list":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT content_text FROM content")
                    materials = db_cursor.fetchall()
                    db_cursor.close()
                    # printing all materials
                    await callback.message.edit_text("Выберите материал для удаления.\nСписок материалов:")
                    # print like 1. text 2. text 3. text
                    if (len(materials) == 0):
                        await callback.message.answer(**Text(Code("Материалов нет")).as_kwargs())
                    else:
                        for i in range(len(materials)):
                            await callback.message.answer(str(i + 1) + ". " + materials[i][0][:50] + "...")
                    await callback.message.answer("Введите номер материала для удаления", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_material_delete)
                elif action == "confirm":
                    # delete from db
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("DELETE FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Материал удалён!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
            elif action == "edit":
                action = callback.data.split("_")[3]
                # списко материалов
                if action == "list":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT content_text FROM content")
                    materials = db_cursor.fetchall()
                    db_cursor.close()
                    # printing all materials
                    await callback.message.edit_text("Выберите материал для редактирования.\nСписок материалов:")
                    # print like 1. text 2. text 3. text
                    if len(materials) == 0:
                        await callback.message.answer(**Text(Code("Материалов нет")).as_kwargs())
                    else:
                        for i in range(len(materials)):
                            await callback.message.answer(str(i + 1) + ". " + materials[i][0][:50] + "...")
                    await callback.message.answer("Введите номер материала для редактирования", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_material_edit)
                elif action == "confirm":
                    # check is published
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                    material = db_cursor.fetchone()
                    db_cursor.close()
                    if material[0] == 1:
                        await callback.message.edit_reply_markup(reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                    else: 
                        await callback.message.edit_reply_markup(reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                elif action == "text":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Введите новый текст материала", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_material_edit_text)
                    elif action == "correct":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE content SET content_text = ?, content_text_ent = ? WHERE id = ?", ((await state.get_data()).get("new_material_text"), (await state.get_data()).get("new_material_entity"), (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Текст материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Текст материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Введите новый текст материала", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_material_edit_text)
                elif action == "image":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Отправьте новое фото материала или нажмите кнопку удаления фото", reply_markup=admin_delete_or_return("admin_material_edit_image_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_image)
                    elif action == "correct":
                        # update db
                        file_info = await bot.get_file((await state.get_data()).get("new_material_image"))
                        file_name = str(uuid4())
                        file_extension = file_info.file_path.split(".")[-1]
                        full_file_name = file_name + "." + file_extension
                        await bot.download_file(file_path=file_info.file_path, destination="photos/" + full_file_name)
                        db_cursor = db.db_connection.cursor()
                        # get old photo name
                        old_name = db_cursor.execute("SELECT content_photo FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_photo = ? WHERE id = ?", (full_file_name, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old photo
                        if old_name[0] is not None and os.path.exists("photos/" + old_name[0]):
                            os.remove("photos/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Фото материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Фото материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Отправьте новое фото материала или нажмите кнопку удаления фото", reply_markup=admin_delete_or_return("admin_material_edit_image_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_image)
                    elif action == "delete":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        # get old photo name
                        old_name = db_cursor.execute("SELECT content_photo FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_photo = ? WHERE id = ?", (None, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old photo
                        if old_name[0] is not None and os.path.exists("photos/" + old_name[0]):
                            os.remove("photos/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Фото материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Фото материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                elif action == "video":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Отправьте новое видео материала или нажмите кнопку удаления видео", reply_markup=admin_delete_or_return("admin_material_edit_video_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_video)
                    elif action == "correct":
                        # update db
                        file_info = await bot.get_file((await state.get_data()).get("new_material_video"))
                        file_name = str(uuid4())
                        file_extension = file_info.file_path.split(".")[-1]
                        full_file_name = file_name + "." + file_extension
                        await bot.download_file(file_path=file_info.file_path, destination="videos/" + full_file_name)
                        db_cursor = db.db_connection.cursor()
                        # get old video name
                        old_name = db_cursor.execute("SELECT content_video FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_video = ? WHERE id = ?", (full_file_name, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old video
                        if old_name[0] is not None and os.path.exists("videos/" + old_name[0]):
                            os.remove("videos/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Видео материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Видео материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Отправьте новое видео материала или нажмите кнопку удаления видео", reply_markup=admin_delete_or_return("admin_material_edit_video_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_video)
                    elif action == "delete":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        # get old video name
                        old_name = db_cursor.execute("SELECT content_video FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_video = ? WHERE id = ?", (None, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old video
                        if old_name[0] is not None and os.path.exists("videos/" + old_name[0]):
                            os.remove("videos/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Видео материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Видео материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                elif action == "audio":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Отправьте новое аудио материала или нажмите кнопку удаления аудио", reply_markup=admin_delete_or_return("admin_material_edit_audio_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_audio)
                    elif action == "correct":
                        # update db
                        file_info = await bot.get_file((await state.get_data()).get("new_material_audio"))
                        file_name = str(uuid4())
                        if "." in file_info.file_path:
                            file_extension = file_info.file_path.split(".")[-1]
                        else:
                            file_extension = "mp3"
                        full_file_name = file_name + "." + file_extension
                        await bot.download_file(file_path=file_info.file_path, destination="audios/" + full_file_name)
                        db_cursor = db.db_connection.cursor()
                        # get old audio name
                        old_name = db_cursor.execute("SELECT content_audio FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_audio = ? WHERE id = ?", (full_file_name, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old audio
                        if old_name[0] is not None and os.path.exists("audios/" + old_name[0]):
                            os.remove("audios/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Аудио материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Аудио материала изменено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Отправьте новое аудио материала или нажмите кнопку удаления аудио", reply_markup=admin_delete_or_return("admin_material_edit_audio_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_audio)
                    elif action == "delete":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        # get old audio name
                        old_name = db_cursor.execute("SELECT content_audio FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_audio = ? WHERE id = ?", (None, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old audio
                        if old_name[0] is not None and os.path.exists("audios/" + old_name[0]):
                            os.remove("audios/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Аудио материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Аудио материала удалено!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                elif action == "document":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Отправьте новый документ материала или нажмите кнопку удаления документа", reply_markup=admin_delete_or_return("admin_material_edit_document_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_document)
                    elif action == "correct":
                        # update db
                        file_info = await bot.get_file((await state.get_data()).get("new_material_document"))
                        file_name = str(uuid4())
                        file_extension = file_info.file_path.split(".")[-1]
                        full_file_name = file_name + "." + file_extension
                        await bot.download_file(file_path=file_info.file_path, destination="documents/" + full_file_name)
                        db_cursor = db.db_connection.cursor()
                        # get old document name
                        old_name = db_cursor.execute("SELECT content_document FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_document = ? WHERE id = ?", (full_file_name, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old document
                        if old_name[0] is not None and os.path.exists("documents/" + old_name[0]):
                            os.remove("documents/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Документ материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Документ материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Отправьте новый документ материала или нажмите кнопку удаления документа", reply_markup=admin_delete_or_return("admin_material_edit_document_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_document)
                    elif action == "delete":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        # get old document name
                        old_name = db_cursor.execute("SELECT content_document FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        old_name = db_cursor.fetchone()
                        db_cursor.execute("UPDATE content SET content_document = ? WHERE id = ?", (None, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # delete old document
                        if old_name[0] is not None and os.path.exists("documents/" + old_name[0]):
                            os.remove("documents/" + old_name[0])
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Документ материала удалён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Документ материала удалён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                elif action == "answer":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Отправьте новый ответ материала или нажмите кнопку удаления материала", reply_markup=admin_delete_or_return("admin_material_edit_answer_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_answer)
                    elif action == "correct":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE content SET on_answer = ? WHERE id = ?", ((await state.get_data()).get("new_material_answer"), (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Ответ материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Ответ материала изменён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
                        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
                    elif action == "incorrect":
                        await callback.message.edit_text("Отправьте новый ответ материала или нажмите кнопку удаления документа", reply_markup=admin_delete_or_return("admin_material_edit_answer_delete", "admin_back"))
                        await state.set_state(AdminActions.admin_material_edit_answer)
                    elif action == "delete":
                        # update db
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE content SET on_answer = ? WHERE id = ?", (None, (await state.get_data()).get("new_material_id")))
                        db.db_connection.commit()
                        db_cursor.close()
                        # if published
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("SELECT published FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                        material = db_cursor.fetchone()
                        db_cursor.close()
                        if material[0] == 1:
                            await callback.message.edit_text("Ответ материала удалён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Снять с публикации", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_unpublish", "admin_material_edit_answer_input"))
                        else:
                            await callback.message.edit_text("Ответ материала удалён!\n\nВыберите необходимое действие", reply_markup=admin_edit("Опубликовать", "admin_material_edit_text_input", "admin_material_edit_image_input", "admin_material_edit_audio_input", "admin_material_edit_video_input", "admin_material_edit_document_input", "admin_material_publish", "admin_material_edit_answer_input"))
            elif action == "show":
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("SELECT content_text FROM content")
                materials = db_cursor.fetchall()
                db_cursor.close()
                # printing all materials
                await callback.message.edit_text("Выберите материал для просмотра.\nСписок материалов:")
                # print like 1. text 2. text 3. text
                if len(materials) == 0:
                    await callback.message.answer(**Text(Code("Материалов нет")).as_kwargs())
                else:
                    for i in range(len(materials)):
                        await callback.message.answer(str(i + 1) + ". " + materials[i][0][:50] + "...")
                await callback.message.answer("Введите номер материала для просмотра", reply_markup=admin_back())
                await state.set_state(AdminActions.admin_material_show)
            elif action == "text":
                action = callback.data.split("_")[3]
                if action == "correct":
                    # add text to db
                    mat_text = (await state.get_data()).get("new_material_text")
                    mat_ent = (await state.get_data()).get("new_material_entity")
                    db_cursor = db.db_connection.cursor()
                    material = db_cursor.execute("INSERT INTO content (content_text, content_text_ent, published_by) VALUES (?, ?, ?)", (mat_text, mat_ent, callback.from_user.id))
                    db.db_connection.commit()
                    db_cursor.close()
                    # get all data from state
                    await state.set_data({"new_material_text": mat_text, "new_material_entity": mat_ent, "new_material_id": material.lastrowid})
                    await callback.message.edit_text("Отлично, пришлите картинку:", reply_markup=admin_back_or_skip("admin_material_image_skip"))
                    await state.set_state(AdminActions.admin_material_add_image)
                elif action == "incorrect":
                    await callback.message.edit_text("Введите текст материала:", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_material_add)
            elif action == "image":
                action = callback.data.split("_")[3]
                if action == "correct":
                    file_info = await bot.get_file((await state.get_data()).get("new_material_image"))
                    file_name = str(uuid4())
                    current_id = (await state.get_data()).get("new_material_id")
                    file_extension = file_info.file_path.split(".")[-1]
                    full_file_name = file_name + "." + file_extension
                    await bot.download_file(file_path=file_info.file_path, destination="photos/" + full_file_name)
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE content SET content_photo = ? WHERE id = ?", (full_file_name, current_id))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, картинка добавлена!\n\nДобавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                elif action == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите картинку", reply_markup=admin_back_or_skip("admin_material_image_skip"))
                    await state.set_state(AdminActions.admin_material_add_image)
                elif action == "skip":
                    await callback.message.edit_text("Пропущено добавление картинки. Добавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": None})
            elif action == "audio":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Пришлите аудио", reply_markup=admin_back_or_skip("admin_material_audio_skip"))
                    await state.set_state(AdminActions.admin_material_add_audio)
                elif action == "correct":
                    file_info = await bot.get_file((await state.get_data()).get("new_material_audio"))
                    file_name = str(uuid4())
                    current_id = (await state.get_data()).get("new_material_id")
                    file_extension = file_info.file_path.split(".")[-1]
                    full_file_name = file_name + "." + file_extension
                    await bot.download_file(file_path=file_info.file_path, destination="audios/" + full_file_name)
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE content SET content_audio = ? WHERE id = ?", (full_file_name, current_id))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, аудио добавлено!\n\nДобавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                elif action == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите аудио", reply_markup=admin_back_or_skip("admin_material_audio_skip"))
                    await state.set_state(AdminActions.admin_material_add_audio)
                elif action == "skip":
                    await callback.message.edit_text("Пропущено добавление аудио. Добавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
            elif action == "video":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Пришлите видео", reply_markup=admin_back_or_skip("admin_material_video_skip"))
                    await state.set_state(AdminActions.admin_material_add_video)
                elif action == "correct":
                    file_info = await bot.get_file((await state.get_data()).get("new_material_video"))
                    file_name = str(uuid4())
                    current_id = (await state.get_data()).get("new_material_id")
                    file_extension = file_info.file_path.split(".")[-1]
                    full_file_name = file_name + "." + file_extension
                    await bot.download_file(file_path=file_info.file_path, destination="videos/" + full_file_name)
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE content SET content_video = ? WHERE id = ?", (full_file_name, current_id))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, видео добавлено!\n\nДобавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                elif action == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите видео", reply_markup=admin_back_or_skip("admin_material_video_skip"))
                    await state.set_state(AdminActions.admin_material_add_video)
                elif action == "skip":
                    await callback.message.edit_text("Пропущено добавление аудио. Добавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
            elif action == "document":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Пришлите документ", reply_markup=admin_back_or_skip("admin_material_document_skip"))
                    await state.set_state(AdminActions.admin_material_add_document)
                elif action == "correct":
                    file_info = await bot.get_file((await state.get_data()).get("new_material_document"))
                    file_name = str(uuid4())
                    current_id = (await state.get_data()).get("new_material_id")
                    file_extension = file_info.file_path.split(".")[-1]
                    full_file_name = file_name + "." + file_extension
                    await bot.download_file(file_path=file_info.file_path, destination="documents/" + full_file_name)
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE content SET content_document = ? WHERE id = ?", (full_file_name, current_id))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, документ добавлен!\n\nДобавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                elif action == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите документ", reply_markup=admin_back_or_skip("admin_material_document_skip"))
                    await state.set_state(AdminActions.admin_material_add_document)
                elif action == "skip":
                    await callback.message.edit_text("Пропущено добавление документа. Добавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
            elif action == "answer":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Пришлите ответ на вопрос, который отобразит этот материал.", reply_markup=admin_back_or_skip("admin_material_answer_skip"))
                    # show all questions
                    await state.set_state(AdminActions.admin_material_add_answer)
                elif action == "correct":
                    on_answer = (await state.get_data()).get("new_material_answer")
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE content SET on_answer = ? WHERE id = ?", (on_answer, (await state.get_data()).get("new_material_id")))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, ответ добавлен!\n\nДобавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                elif action == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите ответ", reply_markup=admin_back_or_skip("admin_material_answer_skip"))
                    await state.set_state(AdminActions.admin_material_add_answer)
                elif action == "skip":
                    await callback.message.edit_text("Пропущено ответа на вопрос. Добавим что-то ещё?", reply_markup=admin_audio_video_document("admin_material_video_add", "admin_material_audio_add", "admin_material_document_add", "admin_material_finish", "admin_material_answer_add"))
                    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
            elif action == "finish":
                await callback.message.edit_text("Материал добавлен!\n\nПредпросмотр:")
                # construct message from db
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("SELECT * FROM content WHERE id = ?", ((await state.get_data()).get("new_material_id"),))
                material = db_cursor.fetchone()
                db_cursor.close()
                # get text

                text = material[1]
                # get entities
                if material[2] is not None:
                    entities = json.loads(material[2])
                else:
                    entities = None
                # get photo
                try:
                    photo = material[3]
                    with open("photos/" + photo, "rb") as file:
                        pass
                except:
                    photo = None
                # get video
                try:
                    video = material[4]
                    with open("videos/" + video, "rb") as file:
                        pass
                except:
                    video = None
                # get audio
                try:
                    audio = material[5]
                    with open("audios/" + audio, "rb") as file:
                        pass
                except:
                    audio = None
                # get document
                try:
                    document = material[6]
                    with open("documents/" + document, "rb") as file:
                        pass
                except:
                    document = None
                # send message
                if photo is not None:
                    photo = FSInputFile("photos/" + photo, "Фото для " + get_username(callback.from_user.id))
                    await callback.message.answer_photo(photo, caption=text, caption_entities=entities)
                    # check if video is not None
                    if video is not None:
                        video = FSInputFile("videos/" + video, "Видео для " + get_username(callback.from_user.id))
                        await callback.message.answer_video(video)
                    # check if audio is not None
                    if audio is not None:
                        audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(callback.from_user.id))
                        await callback.message.answer_audio(audio)
                    # check if document is not None
                    if document is not None:
                        document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(callback.from_user.id)+ "." + document.split(".")[-1])
                        await callback.message.answer_document(document)
                elif video is not None:
                    video = FSInputFile("videos/" + video, "Видео для " + get_username(callback.from_user.id))
                    await callback.message.answer_video(video, caption=text, caption_entities=entities)
                    # check if audio is not None
                    if audio is not None:
                        audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(callback.from_user.id))
                        await callback.message.answer_audio(audio)
                    # check if document is not None
                    if document is not None:
                        document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(callback.from_user.id)+ "." + document.split(".")[-1])
                        await callback.message.answer_document(document)
                elif audio is not None:
                    audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(callback.from_user.id))
                    await callback.message.answer_audio(audio, caption=text, caption_entities=entities)
                    # check if document is not None
                    if document is not None:
                        document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(callback.from_user.id)+ "." + document.split(".")[-1])
                        await callback.message.answer_document(document)
                elif document is not None:
                    document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(callback.from_user.id)+ "." + document.split(".")[-1])
                    await callback.message.answer_document(document, caption=text, caption_entities=entities)
                else:
                    await callback.message.answer(text=text, entities=entities)
                await callback.message.answer(text="Опубликовать?", reply_markup=admin_publish("admin_material_publish"))
            elif action == "publish":
                db_cursor = db.db_connection.cursor()
                content_id = (await state.get_data()).get("new_material_id")
                db_cursor.execute("UPDATE content SET published = 1, published_date = ? WHERE id = ?", (callback.message.date , content_id,))
                db.db_connection.commit()
                await send_to_all(content_id)
                db_cursor.close()
                await callback.message.edit_text("Материал опубликован!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))

                await state.clear()
            elif action == "unpublish":
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("UPDATE content SET published = 0, published_date = ? WHERE id = ?", (callback.message.date , (await state.get_data()).get("new_material_id"),))
                db.db_connection.commit()
                db_cursor.close()
                await callback.message.edit_text("Материал снят с публикации!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                await state.clear()
        elif subject == "back":
            await callback.message.edit_text("Вы вошли в админ меню!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
            await state.clear()
        elif subject == "question":
            action = callback.data.split("_")[2]
            if action == "text":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Введите вопрос:", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_question_add)
                elif action == "correct":
                        await callback.message.edit_text("Вопрос изменён!\n\nВведите ответы (каждый с новой строки)")
                        await state.set_state(AdminActions.admin_question_add_answers)
                elif action == "incorrect":
                        await callback.message.edit_text("Введите вопрос:", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_question_add)
            if action == "answers":
                action = callback.data.split("_")[3]
                if action == "add":
                    await callback.message.edit_text("Введите ответы (каждый с новой строки)")
                    await state.set_state(AdminActions.admin_question_add_answers)
                elif action == "correct":
                    # INSERT INTO DB
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("INSERT INTO questions (question_text, question_answers, question_text_ent) VALUES (?, ?, ?)", ((await state.get_data()).get("new_question_text"), (await state.get_data()).get("new_question_answer"), (await state.get_data()).get("new_question_entity")))
                    db.db_connection.commit()
                    # get id
                    question_id = db_cursor.lastrowid
                    db_cursor.close()
                    await state.set_data({"new_question_id": question_id})
                    # отлично пришлите картинку или пропустите этот шаг
                    await callback.message.edit_text("Отлично! Пришли картинку или пропусти этот шаг", reply_markup=admin_back_or_skip("admin_question_image_skip"))
                    await state.set_state(AdminActions.admin_question_add_image)
                elif action == "incorrect":
                    await callback.message.edit_text("Введите ответы (каждый с новой строки)")
                    await state.set_state(AdminActions.admin_question_add_answers)
            elif action == "image":
                if callback.data.split("_")[3] == "skip":
                    await callback.message.edit_text("Пропущено добавление картинки. Вопрос добавлен!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
                if callback.data.split("_")[3] == "correct":
                    file_info = await bot.get_file((await state.get_data()).get("new_question_image"))
                    file_name = str(uuid4())
                    current_id = (await state.get_data()).get("new_question_id")
                    file_extension = file_info.file_path.split(".")[-1]
                    full_file_name = file_name + "." + file_extension
                    print(current_id)
                    await bot.download_file(file_path=file_info.file_path, destination="photos/" + full_file_name)
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE questions SET question_photo = ? WHERE id = ?", (full_file_name, current_id))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Отлично, картинка добавлена!\n\nВопрос добавлен!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
                if callback.data.split("_")[3] == "incorrect":
                    await callback.message.edit_text("Отлично, пришлите картинку", reply_markup=admin_back_or_skip("admin_question_image_skip"))
                    await state.set_state(AdminActions.admin_question_add_image)
                
            elif action == "delete":
                action = callback.data.split("_")[3]
                if action == "list":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT * FROM questions")
                    questions = db_cursor.fetchall()
                    db_cursor.close()
                    # printing all questions
                    await callback.message.edit_text("Выберите вопрос для удаления.\nСписок вопросов:")
                    # print like 1. text 2. text 3. text
                    if len(questions) == 0:
                        await callback.message.answer(**Text(Code("Вопросов нет")).as_kwargs())
                    else:
                        for i in range(len(questions)):
                            await callback.message.answer(str(i + 1) + ". " + questions[i][1][:50] + "...")
                    await callback.message.answer("Введите номер вопроса для удаления", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_question_delete)
                elif action == "confirm":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("DELETE FROM questions WHERE id = ?", ((await state.get_data()).get("new_question_id"),))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Вопрос удалён!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
    ################ EDIT ##################
            elif action == "edit":
                action = callback.data.split("_")[3]
                if action == "confirm":
                    await callback.message.edit_text("Выберите необходимое действие", reply_markup=admin_edit_question("admin_question_edit_text_input", "admin_question_edit_answers_input", "admin_question_edit_image_input"))
                if action == "list":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT * FROM questions")
                    questions = db_cursor.fetchall()
                    db_cursor.close()
                    # printing all questions
                    await callback.message.edit_text("Выберите вопрос для редактирования.\nСписок вопросов:")
                    # print like 1. text 2. text 3. text
                    if len(questions) == 0:
                        await callback.message.answer(**Text(Code("Вопросов нет")).as_kwargs())
                    else:
                        for i in range(len(questions)):
                            await callback.message.answer(str(i + 1) + ". " + questions[i][1][:50] + "...")
                    await callback.message.answer("Введите номер вопроса для редактирования", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_question_edit)
                elif action == "text":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Введите новый текст вопроса:", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_question_edit_text)
                    elif action == "correct":
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE questions SET question_text = ?, question_text_ent = ? WHERE id = ?", ((await state.get_data()).get("new_question_text"), (await state.get_data()).get("new_question_entity"), (await state.get_data()).get("new_question_id"),))
                        db.db_connection.commit()
                        db_cursor.close()
                        await callback.message.edit_text("Вопрос изменён!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                        await state.clear()
                    elif action == "incorrect":
                        await callback.message.edit_text("Введите новый текст вопроса:", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_question_edit_text)
                elif action == "answers":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Введите новые ответы (каждый с новой строки):")
                        await state.set_state(AdminActions.admin_question_edit_answers)
                    elif action == "correct":
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE questions SET question_answers = ? WHERE id = ?", ((await state.get_data()).get("new_question_answer"), (await state.get_data()).get("new_question_id"),))
                        db.db_connection.commit()
                        db_cursor.close()
                        await callback.message.edit_text("Вопрос изменён!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                        await state.clear()
                    elif action == "incorrect":
                        await callback.message.edit_text("Введите новые ответы (каждый с новой строки):")
                        await state.set_state(AdminActions.admin_question_edit_answers)
                elif action == "image":
                    action = callback.data.split("_")[4]
                    if action == "input":
                        await callback.message.edit_text("Пришлите новую картинку:", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_question_edit_image)
                    elif action == "correct":
                        file_info = await bot.get_file((await state.get_data()).get("new_question_image"))
                        file_name = str(uuid4())
                        current_id = (await state.get_data()).get("new_question_id")
                        file_extension = file_info.file_path.split(".")[-1]
                        full_file_name = file_name + "." + file_extension
                        await bot.download_file(file_path=file_info.file_path, destination="photos/" + full_file_name)
                        db_cursor = db.db_connection.cursor()
                        db_cursor.execute("UPDATE questions SET question_photo = ? WHERE id = ?", (full_file_name, current_id))
                        db.db_connection.commit()
                        db_cursor.close()
                        await callback.message.edit_text("Отлично, картинка добавлена!\n\nВыберите необходимое действие", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                        await state.clear()
                    elif action == "incorrect":
                        await callback.message.edit_text("Пришлите новую картинку:", reply_markup=admin_back())
                        await state.set_state(AdminActions.admin_question_edit_image)
            elif action == "show":
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("SELECT question_text FROM questions")
                materials = db_cursor.fetchall()
                db_cursor.close()
                # printing all materials
                await callback.message.edit_text("Выберите вопрос для просмотра.\nСписок вопросов:")
                # print like 1. text 2. text 3. text
                if len(materials) == 0:
                    await callback.message.answer(**Text(Code("Вопросов нет")).as_kwargs())
                else:
                    for i in range(len(materials)):
                        await callback.message.answer(str(i + 1) + ". " + materials[i][0][:50] + "...")
                await callback.message.answer("Введите вопроса материала для просмотра", reply_markup=admin_back())
                await state.set_state(AdminActions.admin_question_show)
    ########################### EXPORT ############################
        elif subject == "export":
            action = callback.data.split("_")[2]
            if action == "excel":
                await callback.message.edit_text("Экспорт в Excel")
                await export_excel()
                await callback.message.answer_document(FSInputFile("export.xlsx"))
                await callback.message.answer("Excel файл экспортирован!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
    ############################################# ADMIN #############################################
        elif subject == "admin":
            action = callback.data.split("_")[2]
            if action == "menu":
                await callback.message.edit_text("Вы вошли в редактирования администраторов!\n\nВыберите необходимое действие", reply_markup=admin_admin_menu("admin_admin_add_input", "admin_admin_delete_list", "admin_admin_show"))
            if action == "add":
                action = callback.data.split("_")[3]
                if action == "input":
                    await callback.message.edit_text("Введите @никнейм пользователя:", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_admin_add)
                elif action == "correct":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE users SET is_admin = 1, admin_by = ? WHERE chat_id = ?", (callback.from_user.id, (await state.get_data()).get("new_admin_id"),))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Администратор добавлен!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
                elif action == "incorrect":
                    await callback.message.edit_text("Введите @никнейм пользователя:", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_admin_add)
            elif action == "delete":
                action = callback.data.split("_")[3]
                if action == "list":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("SELECT chat_id FROM users WHERE is_admin = 1 OR is_admin = 2")
                    admins = db_cursor.fetchall()
                    db_cursor.close()
                    # printing all admins
                    await callback.message.edit_text("Выберите администратора для удаления.\nСписок администраторов:")
                    # print like 1. text 2. text 3. text
                    if len(admins) == 0:
                        await callback.message.answer(**Text(Code("Администраторов нет")).as_kwargs())
                    else:
                        for i in range(len(admins)):
                            await callback.message.answer(str(i + 1) + ". " + await get_username_by_chat_id(admins[i][0]))
                    await callback.message.answer("Введите номер администратора для удаления", reply_markup=admin_back())
                    await state.set_state(AdminActions.admin_admin_delete)
                elif action == "confirm":
                    db_cursor = db.db_connection.cursor()
                    db_cursor.execute("UPDATE users SET is_admin = 0, admin_by = NULL WHERE id = ?", ((await state.get_data()).get("new_admin_id"),))
                    db.db_connection.commit()
                    db_cursor.close()
                    await callback.message.edit_text("Администратор удалён!", reply_markup=admin_menu(check_superadmin(callback.from_user.id)))
                    await state.clear()
            elif action == "show":
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("SELECT chat_id FROM users WHERE is_admin = 1 OR is_admin = 2")
                admins = db_cursor.fetchall()
                db_cursor.close()
                # printing all admins
                await callback.message.edit_text("Выберите администратора для просмотра.\nСписок администраторов:")
                # print like 1. text 2. text 3. text
                if len(admins) == 0:  
                    await callback.message.answer(**Text(Code("Администраторов нет")).as_kwargs())
                else:
                    for i in range(len(admins)):
                        await callback.message.answer(str(i + 1) + ". " + await get_username_by_chat_id(admins[i][0]))
                await callback.message.answer("Введите номер администратора для просмотра", reply_markup=admin_back())
                await state.set_state(AdminActions.admin_admin_show)
    else:
        await callback.message.answer("Что-то пошло не так, попробуйте ещё раз")
        await state.clear()


@router.message(AdminActions.admin_material_add, F.text)
async def admin_material_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Текст добавлен! Предпросмотр:")
    await msg.answer(text=msg.text, entities=msg.entities)
    # check entities is not empty
    if msg.entities is None:
        await state.set_data({"new_material_text": msg.text, "new_material_entity": None})
    else:
        msg_ent : types.List[MessageEntity] = msg.entities
        temp = []
        for i in msg_ent:
            temp.append(vars(i))
        await state.set_data({"new_material_text": msg.text, "new_material_entity": json.dumps(temp)})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_text_correct", "admin_material_text_incorrect"))

# IMAGE
@router.message(AdminActions.admin_material_add_image, F.photo)
async def admin_material_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Картинка добавлена! Предпросмотр:\n\n")
    await msg.answer_photo(msg.photo[-1].file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": msg.photo[-1].file_id})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_image_correct", "admin_material_image_incorrect"))

# AUDIO
@router.message(AdminActions.admin_material_add_audio, F.audio)
async def admin_material_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Аудио добавлено! Предпросмотр:\n\n")
    await msg.answer_audio(msg.audio.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": msg.audio.file_id, "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_audio_correct", "admin_material_audio_incorrect"))

# VIDEO
@router.message(AdminActions.admin_material_add_video, F.video)
async def admin_material_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Видео добавлено! Предпросмотр:\n\n")
    await msg.answer_video(msg.video.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": msg.video.file_id, "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_video_correct", "admin_material_video_incorrect"))

# DOCUMENT
@router.message(AdminActions.admin_material_add_document, F.document)
async def admin_material_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Документ добавлен! Предпросмотр:\n\n")
    await msg.answer_document(msg.document.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": msg.document.file_id, "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_document_correct", "admin_material_document_incorrect"))

@router.message(AdminActions.admin_material_add_answer, F.text &  ~F.text.startswith('/'))
async def admin_material_add_handler(msg: Message, state: FSMContext):
    # check if text that recieved exists in question answers
    temp = None
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT question_answers FROM questions")
    question_answers = db_cursor.fetchall()
    db_cursor.close()
    for i in question_answers:
        if (msg.text in json.loads(i[0])):
            temp = i[0]
    if temp is None:
        await msg.answer("Такого ответа на вопрос нет, попробуйте ещё раз")
    else:
        await msg.answer("Ответ добавлен! Предпросмотр:\n\n" + msg.text)
        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": msg.text})
        await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_answer_correct", "admin_material_answer_incorrect"))


@router.message(AdminActions.admin_material_delete, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_material_delete_handler(msg: Message, state: FSMContext):
    await build_show_message(msg, state, "admin_material_delete_confirm")

@router.message(AdminActions.admin_material_edit, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_material_edit_handler(msg: Message, state: FSMContext):
    await build_show_message(msg, state, "admin_material_edit_confirm")

@router.message(AdminActions.admin_material_show, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_material_show_handler(msg: Message, state: FSMContext):
    await build_show_message(msg, state, "x")

@router.message(AdminActions.admin_question_delete, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_material_delete_handler(msg: Message, state: FSMContext):
    await build_show_question(msg, state, "admin_question_delete_confirm")

@router.message(AdminActions.admin_question_edit, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_material_edit_handler(msg: Message, state: FSMContext):
    await build_show_question(msg, state, "admin_question_edit_confirm")

@router.message(AdminActions.admin_question_show, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_question_show_handler(msg: Message, state: FSMContext):
    await build_show_question(msg, state, "x")

@router.message(AdminActions.admin_admin_delete, F.text.regexp(r"^(\d+)$").as_("digits"))
async def admin_admin_delete_handler(msg: Message, state: FSMContext):
    await build_show_admin(msg, state, "admin_admin_delete_confirm")
    

@router.message(Command("start"))
async def start_handler(msg: Message, state: FSMContext):
    await state.clear()
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT * FROM users WHERE chat_id = ?", (msg.from_user.id,))
    user = db_cursor.fetchone()
    # check if username is None 
    usernm = msg.from_user.username
    if usernm is None:
        usernm = msg.from_user.id
    if user is None:
        db_cursor.execute("INSERT INTO users (chat_id, first_name, last_name, username, date) VALUES (?, ?, ?, ?, ?)", (msg.from_user.id, msg.from_user.first_name, msg.from_user.last_name, usernm, msg.date))
        db.db_connection.commit()
    elif (user[2] != msg.from_user.first_name or user[3] != msg.from_user.last_name or user[4] != msg.from_user.username) and user[1] == msg.from_user.id:
        db_cursor.execute("UPDATE users SET first_name = ?, last_name = ?, username = ? WHERE chat_id = ?", (msg.from_user.first_name, msg.from_user.last_name, usernm, msg.from_user.id))
        db.db_connection.commit()
    db_cursor.close()
    await msg.answer("Привет!\nРада Вас видеть! Давайте познакомимся!\nМеня зовут "+ bot_name + ", я твой виртуальный стилист бренда Luxury Plus. Помогу подобрать образ на свидание или деловую встречу.\n\nКак я могу к Вам обращаться?\n\nВведите свое имя в ответ на это сообщение")
    await state.set_state(BotQuests.choosing_username)
    try:
        if user[6] == 1:
            await msg.answer("Привет, администратор!\n\nВведите /admin для доступа к админ-панели")
        if user[6] == 2:
            await msg.answer("Привет, ты главный администратор!\n\nВведите /admin для доступа к админ-панели")
    except:
        pass


async def build_show_content(chat_id, material_id):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT * FROM content WHERE id = ? AND published = 1", (material_id,))
    material = db_cursor.fetchone()
    db_cursor.close()
    # get text
    text = material[1]
    # get entities
    if material[2] is not None:
        entities = json.loads(material[2])
    else:
        entities = None
    # get photo
    # check if photo exists on disk
    try:
        photo = material[3]
        with open("photos/" + photo, "rb") as file:
            pass
    except:
        photo = None
    # get video
    try:
        video = material[4]
        with open("videos/" + video, "rb") as file:
            pass
    except:
        video = None
    # get audio
    try:
        audio = material[5]
        with open("audios/" + audio, "rb") as file:
            pass
    except:
        audio = None
    # get document
    try:
        document = material[6]
        with open("documents/" + document, "rb") as file:
            pass
    except:
        document = None
    # send message
    if photo is not None:
        photo = FSInputFile("photos/" + photo, "Фото для " + get_username(chat_id))
        await bot.send_photo(chat_id, photo, caption=text, caption_entities=entities)
        # check if video is not None
        if video is not None:
            video = FSInputFile("videos/" + video, "Видео для " + get_username(chat_id))
            await bot.send_video(chat_id, video)
        # check if audio is not None
        if audio is not None:
            audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(chat_id))
            await bot.send_audio(chat_id, audio)
        # check if document is not None
        if document is not None:
            document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(chat_id) + "." + document.split(".")[-1])
            await bot.send_document(chat_id, document)
    elif video is not None:
        video = FSInputFile("videos/" + video, "Видео для " + get_username(chat_id))
        await bot.send_video(chat_id, video, caption=text, caption_entities=entities)
        # check if audio is not None
        if audio is not None:
            audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(chat_id))
            await bot.send_audio(chat_id, audio)
        # check if document is not None
        if document is not None:
            document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(chat_id) + "." + document.split(".")[-1])
            await bot.send_document(chat_id, document)
    elif audio is not None:
        audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(chat_id))
        await bot.send_audio(chat_id, audio, caption=text, caption_entities=entities)
        # check if document is not None
        if document is not None:
            document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(chat_id) + "." + document.split(".")[-1])
            await bot.send_document(chat_id, document)
    elif document is not None:
        document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(chat_id) + "." + document.split(".")[-1])
        await bot.send_document(chat_id, document, caption=text, caption_entities=entities)
    else:
        await bot.send_message(chat_id, text=text, entities=entities)

async def send_to_all(id):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT chat_id FROM users")
    users = db_cursor.fetchall()
    db_cursor.close()
    for i in users:
        try:
            if await on_answer_check(id, i[0]):
                await build_show_content(i[0], id)
        except:
            pass

async def build_show_message(msg: Message, state: FSMContext, state_name: str):
    material_id = int(msg.text)-1
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT id FROM content")
    #get all material ids
    ids = db_cursor.fetchall()
    db_cursor.close()
    # check if material id is exist in ids
    temp = []
    for i in ids:
        temp.append(i[0])      
    if 0 <= material_id <= len(temp)-1:
        await state.set_data({"new_material_id": temp[material_id]})
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM content WHERE id = ?", (temp[material_id],))
        material = db_cursor.fetchone()
        db_cursor.close()
        await msg.answer("Предпросмотр материала:")
        # construct message from db
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM content WHERE id = ?", (temp[material_id],))
        material = db_cursor.fetchone()
        db_cursor.close()
        # get text
        text = material[1]
        # get entities
        if material[2] is not None:
            entities = json.loads(material[2])
        else:
            entities = None
        # get photo
        try:
            photo = material[3]
            with open("photos/" + photo, "rb") as file:
                pass
        except:
            photo = None
        # get video
        try:
            video = material[4]
            with open("videos/" + video, "rb") as file:
                pass
        except:
            video = None
        # get audio
        try:
            audio = material[5]
            with open("audios/" + audio, "rb") as file:
                pass
        except:
            audio = None
        # get document
        try:
            document = material[6]
            with open("documents/" + document, "rb") as file:
                pass
        except:
            document = None
        # send message
        if photo is not None:
            photo = FSInputFile("photos/" + photo, "Фото для " + get_username(msg.from_user.id))
            await msg.answer_photo(photo, caption=text, caption_entities=entities)
            # check if video is not None
            if video is not None:
                video = FSInputFile("videos/" + video, "Видео для " + get_username(msg.from_user.id))
                await msg.answer_video(video)
            # check if audio is not None
            if audio is not None:
                audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(msg.from_user.id))
                await msg.answer_audio(audio)
            # check if document is not None
            if document is not None:
                document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(msg.from_user.id) + "." + document.split(".")[-1])
                await msg.answer_document(document)
        elif video is not None:
            video = FSInputFile("videos/" + video, "Видео для " + get_username(msg.from_user.id))
            await msg.answer_video(video, caption=text, caption_entities=entities)
            # check if audio is not None
            if audio is not None:
                audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(msg.from_user.id))
                await msg.answer_audio(audio)
            # check if document is not None
            if document is not None:
                document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(msg.from_user.id) + "." + document.split(".")[-1])
                await msg.answer_document(document)
        elif audio is not None:
            audio = FSInputFile("audios/" + audio, "Аудио для " + get_username(msg.from_user.id))
            await msg.answer_audio(audio, caption=text, caption_entities=entities)
            # check if document is not None
            if document is not None:
                document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(msg.from_user.id) + "." + document.split(".")[-1])
                await msg.answer_document(document)
        elif document is not None:
            document = FSInputFile("documents/" + document, "Полезный материал для " + get_username(msg.from_user.id) + "." + document.split(".")[-1])
            await msg.answer_document(document, caption=text, caption_entities=entities)
        else:
            await msg.answer(text=text, entities=entities)
        await msg.answer("Выберите необходимое действие", reply_markup=admin_delete(state_name))
    else:
        await msg.answer("Такого материала не существует!")

async def build_show_question(msg: Message, state: FSMContext, state_name: str):
    material_id = int(msg.text)-1
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT id FROM questions")
    #get all material ids
    ids = db_cursor.fetchall()
    db_cursor.close()
    # check if material id is exist in ids
    temp = []
    for i in ids:
        temp.append(i[0])      
    if 0 <= material_id <= len(temp)-1:
        await state.set_data({"new_question_id": temp[material_id]})
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM questions WHERE id = ?", (temp[material_id],))
        material = db_cursor.fetchone()
        db_cursor.close()
        await msg.answer("Предпросмотр вопроса:")
        # construct message from db
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM questions WHERE id = ?", (temp[material_id],))
        material = db_cursor.fetchone()
        db_cursor.close()
        # get text
        text = material[1]
        # get entities
        if material[3] is not None:
            entities = json.loads(material[3])
        else:
            entities = None
        answers = material[2]
        try:
            photo = material[4]
            with open("photos/" + photo, "rb") as file:
                pass
        except:
            photo = None       
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT question_answers FROM questions WHERE id = ?", (temp[material_id],))
        question = db_cursor.fetchone()
        db_cursor.close()
        # get answers
        answers = json.loads(question[0])
        if photo is not None:
            photo = FSInputFile("photos/" + photo, "Фото для " + get_username(msg.from_user.id))
            await msg.answer_photo(photo, caption=text, caption_entities=entities, reply_markup=build_question_preview_keyboard(answers))
        else:
            await msg.answer(text=text, entities=entities, reply_markup=build_question_preview_keyboard(answers))
        await msg.answer("Выберите необходимое действие", reply_markup=admin_delete(state_name))
    else:
        await msg.answer("Такого материала не существует!")    

async def build_show_admin(msg: Message, state: FSMContext, state_name: str):
    material_id = int(msg.text)-1
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT id FROM users WHERE is_admin = 1 OR is_admin = 2")
    #get all material ids
    ids = db_cursor.fetchall()
    db_cursor.close()
    # check if material id is exist in ids
    temp = []
    for i in ids:
        temp.append(i[0])      
    if 0 <= material_id <= len(temp)-1:
        await state.set_data({"new_admin_id": temp[material_id]})
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM users WHERE id = ?", (temp[material_id],))
        material = db_cursor.fetchone()
        db_cursor.close()
        # user cant delete himself
        if material[1] == msg.from_user.id:
            await msg.answer("Вы не можете удалить самого себя!")
        else:
            await msg.answer("Предпросмотр админа:")
            # construct message
            admin_by = ""
            if material[8] is None:
                admin_by = "Назначен админом: Никем"
            else:
                #find admin by id
                db_cursor = db.db_connection.cursor()
                db_cursor.execute("SELECT username FROM users WHERE chat_id = ?", (material[8],))
                admin = db_cursor.fetchone()
                db_cursor.close()
                admin_by = "Назначен админом: @" + admin[0]

            await msg.answer(("Имя: Без имени\n" if material[2] is None else "Имя: " + str(material[2]) + "\n") + ("Фамилия: Без фамилии\n" if material[3] is None else "Фамилия: " + str(material[3]) + "\n") + ("Никнейм: Без никнейма\n" if material[4] is None else "Никнейм: @" + str(material[4]) + "\n") + ("Дата регистрации: Без даты\n" if material[5] is None else "Дата регистрации: " + str(material[5]) + "\n") + admin_by)
            await msg.answer("Выберите необходимое действие", reply_markup=admin_delete(state_name))            
    else:
        await msg.answer("Такого админа не существует!")    

@router.message(BotQuests.choosing_username, F.text)
async def choosing_username_handler(msg: Message, state: FSMContext):
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("UPDATE users SET nominal_name = ? WHERE chat_id = ?", (msg.text, msg.from_user.id))
    db.db_connection.commit()
    db_cursor.close()
    await msg.answer("Приятно познакомиться, " + msg.text + "!\n\nПозвольте я задам несколько вопросов о Вас и вашем гардеробе?\n\nЭто поможет мне лучше узнать Вас, чтобы подобрать индивидуальные образы, на любой жизненный случай", reply_markup=get_yes_no())

@router.callback_query(F.data.startswith("callback_"))
async def callback_yes_no(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split("_")[1]
    if action == "yes":
        # remove keyboard
        await callback.message.edit_reply_markup()
        if (get_question_photo(1) is not None):
            await callback.message.answer_photo(get_question_photo(1), caption=get_question_text(1), entities=get_question_entity(1), reply_markup=build_question_keyboard(1, 2))
        else:
            await callback.message.answer(text=get_question_text(1), entities=get_question_entity(1), reply_markup=build_question_keyboard(1, 2))
        await state.clear()
    elif action == "no":
        await callback.message.edit_reply_markup()
        await callback.message.answer("Поняла тебя. Возвращайся когда будет время. Хорошего вам дня, "+ get_username(callback.from_user.id) +"!", reply_markup=come_back())
        await state.clear()
    elif action == "maybe":
        await callback.message.edit_reply_markup()
        await callback.message.answer("Дорогая, "+ get_username(callback.from_user.id) +"! Я займу всего 5 минут. Продолжим?", reply_markup=persuade())
        await state.clear()
    elif action == "sub":
        if await check_subscription(callback.from_user.id):
            await callback.message.edit_reply_markup()
            await bot.answer_callback_query(callback.id, text="Вы подписаны на канал", show_alert=True)
            await callback.message.answer(text="Фух, закончили! Спасибо что так подробно и честно ответили на мои вопросы. Для меня это очень ценно и важно.\n\nТеперь я точно знаю, как сделать ваш гардероб индивидуальным, стильным и удобным.\n\nЯ ценю ваше время, поэтому сама залезла на ВБ и нашла вещи, которые точно Вам подойдут. \n\nПосмотрите, что я для Вас нашла", reply_markup=show_data())
        else:
            await bot.answer_callback_query(callback.id, text="Вы не подписаны на канал", show_alert=True)
    elif action == "dontshow":
        await callback.message.edit_reply_markup()
        await callback.message.answer("Поняла Вас, тогда обязательно посмотрите информацию на канале https://t.me/luxury_plus_size, и возвращайтесь ко мне скорее!", reply_markup=come_back2())
    
@router.callback_query(F.data.startswith("show_"))
async def show_content(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BotQuests.questions_complete)
    await callback.message.edit_reply_markup()
    await callback.message.answer("⬇Держи полезные материалы⬇")
    # get all content ids
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT id FROM content WHERE published = 1")
    ids = db_cursor.fetchall()
    db_cursor.execute("SELECT id FROM content WHERE on_answer NOT NULL")
    db_cursor.close()
    # check if content is not empty
    if ids is None:
        await callback.message.answer("Подожди пожалуйста, и я пришлю тебе полезные материалы")
    else:
        for i in ids:
            if await on_answer_check(i[0], callback.from_user.id):
                await build_show_content(callback.from_user.id, i[0])

    
async def on_answer_check(current_content_id, user_id):
    # check if current question id on_answer is not None
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT on_answer FROM content WHERE id = ?", (current_content_id,))
    on_answer = db_cursor.fetchone()
    db_cursor.close()
    # if on_answer is None
    if on_answer[0] is None:
        # print content
        return True
    else:
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT answer FROM answers WHERE user_id = ? AND answer = ?", (user_id, on_answer[0]))
        user_answer = db_cursor.fetchone()
        db_cursor.close()
        if user_answer is not None:
            return True
        else:
            return False

@router.callback_query(F.data.startswith("question_"))
async def questions(callback: types.CallbackQuery, state: FSMContext):
    # get question id
    question_id = callback.data.split("_")[1]
    # get answer
    answer = callback.data.split("_")[2]
    # write answer to db
    db_cursor = db.db_connection.cursor()
    # check if user already answered this question
    db_cursor.execute("SELECT * FROM answers WHERE user_id = ? AND question_id = ?", (callback.from_user.id, question_id))
    user = db_cursor.fetchone()
    if user is None:
        db_cursor.execute("INSERT INTO answers (user_id, question_id, answer) VALUES (?, ?, ?)", (callback.from_user.id, question_id, answer))
    else:
        db_cursor.execute("UPDATE answers SET answer = ? WHERE user_id = ? AND question_id = ?", (answer, callback.from_user.id, question_id))
    db.db_connection.commit()
    db_cursor.close()
    # get next question
    next_question_id = get_next_question_id(question_id)
    if next_question_id is None:
        await callback.message.edit_reply_markup()
        # get user answers
        db_cursor = db.db_connection.cursor()
        db_cursor.execute("SELECT * FROM answers WHERE user_id = ?", (callback.from_user.id,))
        answers = db_cursor.fetchall()
        db_cursor.close()
        if len(answers) >= 4:
            await callback.message.answer("Такс, в итоге:\nВаш регион - " + answers[0][3] + "\nВам - "+ answers[1][3] +"\nВаш размер - " + answers[2][3] + "\nВаш тип фигуры - " + answers[3][3] + "\n\nУчитывая все это, вот, что я для Вас подобрала.\n\nОдин момент, подпишитесь обязательно на канал: https://t.me/luxury_plus_size\n\nВ долгу не останусь", reply_markup=check_button())
        else:
            await callback.message.answer("Такс, мы закончили!\n\nУчитывая Ваши ответы, вот, что я для Вас подобрала.\n\nОдин момент, подпишитесь обязательно на канал: https://t.me/luxury_plus_size\n\nВ долгу не останусь", reply_markup=check_button())
        await state.clear()
    else:
        await callback.message.edit_reply_markup()
        if (get_question_photo(next_question_id) is not None):
            await callback.message.answer_photo(get_question_photo(next_question_id), caption=get_question_text(next_question_id), entities=get_question_entity(next_question_id), reply_markup=build_question_keyboard(next_question_id, get_smart_column_count(next_question_id)))
        else:
            await callback.message.answer(text=get_question_text(next_question_id), entities=get_question_entity(next_question_id), reply_markup=build_question_keyboard(next_question_id, get_smart_column_count(next_question_id)))

@router.message(AdminActions.admin_material_edit_text, F.text)
async def admin_material_edit_text_handler(msg: Message, state: FSMContext):
    await msg.answer("Текст изменен! Предпросмотр:")
    await msg.answer(text=msg.text, entities=msg.entities)
    temp = []
    # check entities is not empty
    if msg.entities is None:
        await state.set_data({"new_material_text": msg.text, "new_material_entity": None, "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    else:
        msg_ent : types.List[MessageEntity] = msg.entities    
        for i in msg_ent:
            temp.append(vars(i))
    await state.set_data({"new_material_text": msg.text, "new_material_entity": json.dumps(temp), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_text_correct", "admin_material_edit_text_incorrect"))

@router.message(AdminActions.admin_material_edit_image, F.photo)
async def admin_material_edit_image_handler(msg: Message, state: FSMContext):
    await msg.answer("Картинка изменена! Предпросмотр:\n\n")
    await msg.answer_photo(msg.photo[-1].file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": msg.photo[-1].file_id, "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_image_correct", "admin_material_edit_image_incorrect"))

@router.message(AdminActions.admin_material_edit_video, F.video)
async def admin_material_edit_video_handler(msg: Message, state: FSMContext):
    await msg.answer("Видео изменено! Предпросмотр:\n\n")
    await msg.answer_video(msg.video.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": msg.video.file_id, "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_video_correct", "admin_material_edit_video_incorrect"))

@router.message(AdminActions.admin_material_edit_audio, F.audio)
async def admin_material_edit_audio_handler(msg: Message, state: FSMContext):
    await msg.answer("Аудио изменено! Предпросмотр:\n\n")
    await msg.answer_audio(msg.audio.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": msg.audio.file_id, "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_audio_correct", "admin_material_edit_audio_incorrect"))

@router.message(AdminActions.admin_material_edit_document, F.document)
async def admin_material_edit_document_handler(msg: Message, state: FSMContext):
    await msg.answer("Документ изменен! Предпросмотр:\n\n")
    await msg.answer_document(msg.document.file_id)
    await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": msg.document.file_id, "new_material_answer": (await state.get_data()).get("new_material_answer")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_document_correct", "admin_material_edit_document_incorrect"))

@router.message(AdminActions.admin_material_edit_answer, F.text & ~F.text.startswith("/"))
async def admin_material_edit_answer_handler(msg: Message, state: FSMContext):
    temp = None
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT question_answers FROM questions")
    question_answers = db_cursor.fetchall()
    db_cursor.close()
    for i in question_answers:
        if (msg.text in json.loads(i[0])):
            temp = i[0]
    if temp is None:
        await msg.answer("Такого ответа на вопрос нет, попробуйте ещё раз")
    else:
        await msg.answer("Ответ изменен! Предпросмотр:\n\n" + msg.text)
        await state.set_data({"new_material_text": (await state.get_data()).get("new_material_text"), "new_material_entity": (await state.get_data()).get("new_material_entity"), "new_material_id": (await state.get_data()).get("new_material_id"), "new_material_image": (await state.get_data()).get("new_material_image"), "new_material_audio": (await state.get_data()).get("new_material_audio"), "new_material_video": (await state.get_data()).get("new_material_video"), "new_material_document": (await state.get_data()).get("new_material_document"), "new_material_answer": msg.text})
        await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_material_edit_answer_correct", "admin_material_edit_answer_incorrect"))

@router.message(AdminActions.admin_question_add_answers, F.text)
async def admin_question_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Ответы добавлены! Предпросмотр:")
    # generate array of answers that are separated by \n
    answers = msg.text.split("\n")
    await state.set_data({"new_question_text": (await state.get_data()).get("new_question_text"), "new_question_entity": (await state.get_data()).get("new_question_entity"), "new_question_answer": json.dumps(answers), "new_question_id": None})
    if (await state.get_data()).get("new_question_entity") is None:
        msg_ent = None
    else:
        msg_ent = json_to_msg_ent((await state.get_data()).get("new_question_entity"))
    await msg.answer(text=(await state.get_data()).get("new_question_text"), entities=msg_ent, reply_markup=build_question_preview_keyboard(answers))
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_answers_correct", "admin_question_answers_incorrect"))

@router.message(AdminActions.admin_question_add_image, F.photo)
async def admin_question_add_image_handler(msg: Message, state: FSMContext):
    await msg.answer("Картинка добавлена! Предпросмотр:\n\n")
    await msg.answer_photo(msg.photo[-1].file_id)
    await state.set_data({"new_question_id": (await state.get_data()).get("new_question_id"), "new_question_image": msg.photo[-1].file_id})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_image_correct", "admin_question_image_incorrect"))

@router.message(AdminActions.admin_question_add, F.text)
async def admin_question_add_handler(msg: Message, state: FSMContext):
    await msg.answer("Текст вопроса добавлен! Предпросмотр:")
    await msg.answer(text=msg.text, entities=msg.entities)
    # check entities is not empty
    if msg.entities is None:
        await state.set_data({"new_question_text": msg.text, "new_question_entity": None, "new_question_answer": None, "new_question_id": None})
    else:
        msg_ent : types.List[MessageEntity] = msg.entities
        temp = []
        for i in msg_ent:
            temp.append(vars(i))
        await state.set_data({"new_question_text": msg.text, "new_question_entity": json.dumps(temp), "new_question_answer": None, "new_question_id": None})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_text_correct", "admin_question_text_incorrect"))

@router.message(AdminActions.admin_question_edit_text, F.text)
async def admin_question_edit_text_handler(msg: Message, state: FSMContext):
    await msg.answer("Текст вопроса изменен! Предпросмотр:")
    await msg.answer(text=msg.text, entities=msg.entities)
    # check entities is not empty
    if msg.entities is None:
        await state.set_data({"new_question_text": msg.text, "new_question_entity": None, "new_question_answer": (await state.get_data()).get("new_question_answer"), "new_question_id": (await state.get_data()).get("new_question_id")})
    else:
        msg_ent : types.List[MessageEntity] = msg.entities
        temp = []
        for i in msg_ent:
            temp.append(vars(i))
        await state.set_data({"new_question_text": msg.text, "new_question_entity": json.dumps(temp), "new_question_answer": (await state.get_data()).get("new_question_answer"), "new_question_id": (await state.get_data()).get("new_question_id")})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_edit_text_correct", "admin_question_edit_text_incorrect"))

@router.message(AdminActions.admin_question_edit_answers, F.text)
async def admin_question_edit_answers_handler(msg: Message, state: FSMContext):
    await msg.answer("Ответы изменены! Предпросмотр:")
    # generate array of answers that are separated by \n
    answers = msg.text.split("\n")
    # get question text
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT question_text FROM questions WHERE id = ?", ((await state.get_data()).get("new_question_id"),))
    question = db_cursor.fetchone()
    # get question entities
    db_cursor.execute("SELECT question_text_ent FROM questions WHERE id = ?", ((await state.get_data()).get("new_question_id"),))
    question_entities = db_cursor.fetchone()
    db_cursor.close()
    await state.set_data({"new_question_text": question[0], "new_question_entity": question_entities[0], "new_question_answer": json.dumps(answers), "new_question_id": (await state.get_data()).get("new_question_id")})
    if (await state.get_data()).get("new_question_entity") is None:
        msg_ent = None
    else:
        msg_ent = json_to_msg_ent((await state.get_data()).get("new_question_entity"))
    await msg.answer(text=(await state.get_data()).get("new_question_text"), entities=msg_ent, reply_markup=build_question_preview_keyboard(answers))
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_edit_answers_correct", "admin_question_edit_answers_incorrect"))

@router.message(AdminActions.admin_question_edit_image, F.photo)
async def admin_question_edit_image_handler(msg: Message, state: FSMContext):
    await msg.answer("Картинка изменена! Предпросмотр:\n\n")
    await msg.answer_photo(msg.photo[-1].file_id)
    await state.set_data({"new_question_text": (await state.get_data()).get("new_question_text"), "new_question_entity": (await state.get_data()).get("new_question_entity"), "new_question_answer": (await state.get_data()).get("new_question_answer"), "new_question_id": (await state.get_data()).get("new_question_id"), "new_question_image": msg.photo[-1].file_id})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_question_edit_image_correct", "admin_question_edit_image_incorrect"))

@router.message(AdminActions.admin_admin_add, F.text.startswith('@'))
async def admin_admin_add_handler(msg: Message, state: FSMContext):
    # find user in db
    db_cursor = db.db_connection.cursor()
    db_cursor.execute("SELECT * FROM users WHERE username = ?", (msg.text[1:],))
    user = db_cursor.fetchone()
    # get user id
    db_cursor.close()
    if user is None:
        await msg.answer("Такого пользователя не существует в базе данных бота!")
        return
    # check if user is admin
    if user[6] == 1 or user[6] == 2:
        await msg.answer("Пользователь уже является администратором!")
        return
    user_id = user[1]
    await msg.answer("Администратор добавлен! Предпросмотр:")
    await msg.answer("Имя: " + ("Без имени" if user[2] is None else str(user[2])) + "\nФамилия: " + ("Без фамилии" if user[2] is None else str(user[3])) + "\nUsername: @" + ("Без никнейма" if user[2] is None else str(user[4])))
    await state.set_data({"new_admin_username": msg.text[1:], "new_admin_id": user_id})
    await msg.answer(text="Всё корректно?", reply_markup=admin_correct_or_not("admin_admin_add_correct", "admin_admin_add_incorrect")) 

@router.message()
async def message_handler(msg: Message, state: FSMContext):
    #    msg_ent : types.List[MessageEntity] = msg.entities
#    print(msg_ent)
    # json
    temp = []
#    for i in msg_ent:
#        temp.append(vars(i))
#    print(json.dumps(temp))
#    photo = FSInputFile("photos/1.jpg")
#    await msg.answer_photo(photo, caption="test", reply_markup=build_question_preview_keyboard(["test", "test2"]))
    await msg.answer("Не знаю такую команду")
