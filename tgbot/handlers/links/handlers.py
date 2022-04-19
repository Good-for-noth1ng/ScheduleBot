from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from tgbot.models import User, Links
from tgbot.handlers.links.static_text import (
    no_links_yet_text, 
    add_or_delete_text,
    put_link_name_text,
    put_link_text,
    link_is_added_text,
    choose_link_to_delete_text,
    successful_del_text,
    nothing_to_delete_text,
    number_requested_text, 
    cancel_delete_text,
    url_requested_text,
    ADD_BUTTON, 
    DELETE_LINK_BUTTON
)
from tgbot.handlers.links.keyboards import make_keyboard_add_or_delete_link, make_keyboard_to_delete
from tgbot.handlers.links.conversation_state import (
    ADD_LINK_STATE, 
    ADD_NAME_STATE, 
    ADD_OR_DELETE_STATE, 
    DELETE_STATE
)

def send_links(update: Update, context: CallbackContext):
    text = ""
    links = Links.objects.all()
    if links:
        for link in links:
            text += f'{link.lesson} - [  {link.url}  ]\n'
        update.message.reply_text(text=text)
    else:
        update.message.reply_text(no_links_yet_text)


def ask_add_or_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=add_or_delete_text, reply_markup=make_keyboard_add_or_delete_link())
    return ADD_OR_DELETE_STATE


def start_add(update: Update, context: CallbackContext):
    update.message.reply_text(text=put_link_name_text, reply_markup=ReplyKeyboardRemove())
    return ADD_NAME_STATE

def start_delete(update: Update, context: CallbackContext):
    links = Links.objects.all()
    text = ""
    if links:
        update.message.reply_text(text=choose_link_to_delete_text)
        for i in range(0, len(links)):            
            text += f"<--------{i + 1}-------->\n"
            text += f"{links[i].lesson} - [  {links[i].url}  ]\n"
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_delete(len(links)))
        return DELETE_STATE
    else: 
        update.message.reply_text(nothing_to_delete_text)
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["link_name"] = update.message.text
    update.message.reply_text(text=put_link_text)
    return ADD_LINK_STATE

def cancel_delete(update:Update, context: CallbackContext):
    update.message.reply_text(text=cancel_delete_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def add_link(update: Update, context: CallbackContext):
    url = update.message.text
    lesson = context.user_data["link_name"]
    link = Links(lesson=lesson, url=url)
    link.save()
    update.message.reply_text(link_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def url_requested(update: Update, context: CallbackContext):
    update.message.reply_text(url_requested_text)
    return ADD_LINK_STATE

def delete(update: Update, context: CallbackContext):
    link_to_delete_index = int(update.message.text) - 1     
    links = Links.objects.all()
    links[link_to_delete_index].delete()
    update.message.reply_text(text=successful_del_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def number_requested(update: Update, context: CallbackContext):
    update.message.reply_text(number_requested_text)
    start_delete(update, context)
    return DELETE_STATE

def stop_editing(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END