from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
import os
from pathlib import Path

from tgbot.models import Homework
from tgbot.handlers.homework.static_text import (
    which_homework_text,
    no_homework_yet_text,
    add_or_delete_text,
    put_homework_name_text,
    put_homework_task_text,
    homework_is_added_text,
    choose_homework_to_delete_text,
    successful_del_text,
    nothing_to_delete_text,
    number_requested_text,
    cancel_delete_text,
    ADD_HMWRK_BUTTON,
    DELETE_HMWRK_BUTTON,
    CANCEL_DELETE_HMWRK_BUTTON
)
from tgbot.handlers.homework.keyboards import make_keyboard_add_or_delete_homework, make_keyboard_to_choose_or_delete
from tgbot.handlers.homework.conversation_state import (
    SEND_HOMEWORK_STATE,
    ADD_HMWRK_NM_STATE, 
    ADD_HMWRK_TSK_STATE, 
    ADD_OR_DLT_STATE, 
    DLT_HMWRK_STATE
)
from dtb.settings import MEDIA_ROOT

def ask_which_homework(update: Update, context: CallbackContext):
    homework_num = Homework.get_num_of_homework()
    if homework_num > 0:
        update.message.reply_text(text=which_homework_text)
        text = Homework.make_string_for_choosing_homework()
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose_or_delete(link_list_lenght=homework_num))
        return SEND_HOMEWORK_STATE
    else:
        update.message.reply_text(no_homework_yet_text)
        return ConversationHandler.END

def send_homework(update: Update, context: CallbackContext):
    homeworks = Homework.objects.all()
    if homeworks:
        for homework in homeworks:
            text = ""
            text += f"{homework.name}\n"
            if homework.task_text:
                text += f"{homework.task_text}"
                update.message.reply_text(text=text)
            if homework.task_doc:
                update.message.reply_text(text=text)
                update.message.reply_document(document=homework.task_doc)
            if homework.task_photo_id:
                update.message.reply_text(text=text)
                update.message.reply_photo(photo=homework.task_photo_id)

def ask_add_or_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=add_or_delete_text, reply_markup=make_keyboard_add_or_delete_homework())
    return ADD_OR_DLT_STATE

def start_add(update: Update, context: CallbackContext):
    update.message.reply_text(text=put_homework_name_text, reply_markup=ReplyKeyboardRemove())
    return ADD_HMWRK_NM_STATE

def start_delete(update: Update, context: CallbackContext):
    homeworks = Homework.objects.all()
    text = ""
    if homeworks:
        update.message.reply_text(text=choose_homework_to_delete_text)
        for i in range(0, len(homeworks)):            
            text += f"<--------{i + 1}-------->\n"
            text += f"{homeworks[i].name}\n"
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_delete_homework(len(homeworks)))
        return DLT_HMWRK_STATE
    else: 
        update.message.reply_text(nothing_to_delete_text)
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["homework_name"] = update.message.text
    update.message.reply_text(text=put_homework_task_text)
    return ADD_HMWRK_TSK_STATE

def cancel_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=cancel_delete_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def add_task_text(update: Update, context: CallbackContext):
    task = update.message.text
    name = context.user_data["homework_name"]
    homework = Homework(name=name, task_text=task)
    homework.save()
    update.message.reply_text(homework_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def add_task_file(update: Update, context: CallbackContext):
    name = context.user_data["homework_name"]
    document = update.message.document
    download_path = os.path.join(MEDIA_ROOT, document.file_name)
    task = document.get_file().download(custom_path=download_path)     
    homework = Homework(name=name)
    homework.task_doc = task
    homework.save()
    update.message.reply_text(homework_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def add_task_file_as_photo(update: Update, context: CallbackContext):
    name = context.user_data["homework_name"]
    photo_id = update.message.photo[-1].file_id
    homework = Homework(name=name, task_photo_id=photo_id)
    homework.save()
    update.message.reply_text(homework_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def delete(update: Update, context: CallbackContext):
    homework_to_delete_index = int(update.message.text) - 1     
    homeworks = Homework.objects.all()
    homeworks[homework_to_delete_index].delete()
    update.message.reply_text(text=successful_del_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def number_requested(update: Update, context: CallbackContext):
    update.message.reply_text(number_requested_text)
    start_delete(update, context)
    return DLT_HMWRK_STATE

def stop_editing(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END