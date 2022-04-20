from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
import os
from pathlib import Path
from dtb.settings import MEDIA_ROOT
from tgbot.models import Requirements, RequirementFile
from tgbot.handlers.requirements.static_text import (
    no_requirements_yet_text,
    add_or_delete_text,
    put_require_name_text,
    put_require_text,
    require_is_added_text,
    choose_require_to_delete_text,
    successful_del_text,
    nothing_to_delete_text,
    number_requested_text,
    cancel_delete_text,
    ADD_RQMNT_BUTTON,
    DELETE_RQMNT_BUTTON
)
from tgbot.handlers.requirements.keyboards import make_keyboard_add_or_delete_require, make_keyboard_to_delete_require
from tgbot.handlers.requirements.conversation_state import (
    ADD_OR_DELETE_REQUIRE_STATE,
    ADD_REQUIR_NAME_STATE,
    ADD_REQUIRE_STATE,
    DELETE_REQUIRE_STATE
)

def send_requirements(update: Update, context: CallbackContext):
    requirements = Requirements.objects.all()
    if requirements:
        for requirement in requirements:
            text = f'📒 {requirement.name}\n'
            requirement_files = RequirementFile.objects.all().filter(requirements=requirement)
            if requirement.text:
                text += f'📄 {requirement.text}\n'
                update.message.reply_text(text=text)
            if requirement_files:
                for requirement_file in requirement_files:
                    update.message.reply_text(text=text)
                    update.message.reply_document(document=requirement_file.file_field)
            if requirement.photo_id:
                update.message.reply_text(text=text)
                update.message.reply_photo(photo=requirement.photo_id)
            text = ""
    else:
        update.message.reply_text(no_requirements_yet_text)

def ask_add_or_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=add_or_delete_text, reply_markup=make_keyboard_add_or_delete_require())
    return ADD_OR_DELETE_REQUIRE_STATE

def start_add(update: Update, context: CallbackContext):
    update.message.reply_text(text=put_require_name_text, reply_markup=ReplyKeyboardRemove())
    return ADD_REQUIR_NAME_STATE

def start_delete(update: Update, context: CallbackContext):
    requirements = Requirements.objects.all()
    text = ""
    if requirements:
        update.message.reply_text(text=choose_require_to_delete_text)
        for i in range(0, len(requirements)):            
            text += f"<--------{i + 1}-------->\n"
            text += f"{requirements[i].name}\n"
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_delete_require(len(requirements)))
        return DELETE_REQUIRE_STATE
    else: 
        update.message.reply_text(nothing_to_delete_text)
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["requirement_name"] = update.message.text
    update.message.reply_text(text=put_require_text)
    return ADD_REQUIRE_STATE

def cancel_delete(update:Update, context: CallbackContext):
    update.message.reply_text(text=cancel_delete_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def add_require_text(update: Update, context: CallbackContext):
    requirement_text = update.message.text
    name = context.user_data["requirement_name"]
    require = Requirements(name=name, text=requirement_text)
    require.save()
    update.message.reply_text(require_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def add_require_file(update: Update, context: CallbackContext):
    name = context.user_data["requirement_name"]
    document = update.message.document
    download_path = os.path.join(MEDIA_ROOT, document.file_name)
    downloaded_file = document.get_file().download(custom_path=download_path)     
    requirement = Requirements(name=name)
    requirement_file = RequirementFile(requirements=requirement)
    requirement_file.file_field = downloaded_file
    requirement.save()
    requirement_file.save()
    update.message.reply_text(require_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def add_require_photo_id(update: Update, context: CallbackContext):
    name = context.user_data["requirement_name"]
    photo_id = update.message.photo[-1].file_id
    requirement = Requirements(name=name, photo_id=photo_id)
    requirement.save()
    update.message.reply_text(require_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def delete(update: Update, context: CallbackContext):
    require_to_delete_index = int(update.message.text) - 1     
    requirements = Requirements.objects.all()
    requirements[require_to_delete_index].delete()
    update.message.reply_text(text=successful_del_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def number_requested(update: Update, context: CallbackContext):
    update.message.reply_text(number_requested_text)
    start_delete(update, context)
    return DELETE_REQUIRE_STATE

def stop_editing(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END