from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from tgbot.models import ExternalResource
import tgbot.handlers.external.static_text as st
from tgbot.handlers.external.keyboards import make_keyboard_add_or_delete, make_keyboard_to_choose
import tgbot.handlers.external.conversation_state as cs

def setting_reply_keyboard(ext_num, is_book=False, is_link=False):
    if ext_num > 0:
        buttons = ExternalResource.extract_names_for_keyboard(is_book=is_book, is_link=is_link)
        return buttons
    else:
        return False

def ask_which_book(update: Update, context: CallbackContext):
    ext_num = ExternalResource.get_books_num()
    context.user_data["ext_type"] = "book"
    buttons = setting_reply_keyboard(ext_num=ext_num, is_book=True)
    if buttons:
        update.message.reply_text(text=st.which_book_text, reply_markup=make_keyboard_to_choose(buttons=buttons))
        return cs.SEND_STATE
    else:
        update.message.reply_text(text=st.nothing_yet_text)
        return ConversationHandler.END 

def ask_which_link(update: Update, context: CallbackContext):
    ext_num = ExternalResource.get_urls_num()
    context.user_data["ext_type"] = "link"
    buttons = setting_reply_keyboard(ext_num=ext_num, is_link=True)
    if buttons:
        update.message.reply_text(text=st.which_link_text, reply_markup=make_keyboard_to_choose(buttons=buttons))
        return cs.SEND_STATE
    else:
        update.message.reply_text(text=st.nothing_yet_text)
        return ConversationHandler.END 

def send(update: Update, context: CallbackContext):
    chosen_name = update.message.text
    if context.user_data["ext_type"] == "book":
        ext_res = ExternalResource.get_books_by_name(name=chosen_name)
    elif context.user_data["ext_type"] == "link":
        ext_res = ExternalResource.get_urls_by_name(name=chosen_name)
    if ext_res:
        text = f"🔍 {ext_res.name} 🔗 {ext_res.url}"
        update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(text=st.no_such_name_text)
        return cs.SEND_STATE

def ask_add_or_delete_book(update: Update, context: CallbackContext):
    context.user_data["ext_type"] = "book"
    update.message.reply_text(text=st.add_or_delete_book_text, reply_markup=make_keyboard_add_or_delete())
    return cs.ADD_OR_DELETE_STATE

def ask_add_or_delete_link(update: Update, context: CallbackContext):
    context.user_data["ext_type"] = "link"
    update.message.reply_text(text=st.add_or_delete_link_text, reply_markup=make_keyboard_add_or_delete())
    return cs.ADD_OR_DELETE_STATE

def start_add(update: Update, context: CallbackContext):
    if context.user_data["ext_type"] == "book":
        update.message.reply_text(text=st.put_book_name_text, reply_markup=ReplyKeyboardRemove())
    elif context.user_data["ext_type"] == "link":
        update.message.reply_text(text=st.put_link_name_text, reply_markup=ReplyKeyboardRemove())
    return cs.ADD_NAME_STATE

def start_delete(update: Update, context: CallbackContext):
    if context.user_data["ext_type"] == "book":
        ext_num = ExternalResource.get_books_num()
        is_book = True
        is_link = False
    elif context.user_data["ext_type"] == "link":
        ext_num = ExternalResource.get_urls_num()
        is_book = False
        is_link = True

    if ext_num > 0:
        buttons = ExternalResource.extract_names_for_keyboard(is_book=is_book, is_link=is_link)
        update.message.reply_text(text=st.choose_name_to_delete_text, reply_markup=make_keyboard_to_choose(buttons=buttons))
        return cs.DELETE_STATE
    else: 
        update.message.reply_text(text=st.nothing_to_delete_text)
        context.user_data.clear()
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    if context.user_data["ext_type"] == "book":
        update.message.reply_text(text=st.put_book_text)
    elif context.user_data["ext_type"] == "link":
        update.message.reply_text(text=st.put_link_text)
    return cs.ADD_URL_STATE

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(text=st.cancel_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def add_link(update: Update, context: CallbackContext):
    url = update.message.text
    name = context.user_data["name"]
    if context.user_data["ext_type"] == "book":
        ext_res = ExternalResource(name=name, url=url, is_link_to_book=True)
    elif context.user_data["ext_type"] == "link":
        ext_res =ExternalResource(name=name, url=url, is_link_to_command=True)
    ext_res.save()
    update.message.reply_text(st.sucсessful_add_text)
    context.user_data.clear()
    return ConversationHandler.END

def url_requested(update: Update, context: CallbackContext):
    update.message.reply_text(st.url_requested_text)
    return cs.ADD_URL_STATE

def delete(update: Update, context: CallbackContext):
    chosen_name = update.message.text
    if context.user_data["ext_type"] == "book":
        ExternalResource.deleting_book_by_name(name=chosen_name)
    elif context.user_data["ext_type"] == "link":
        ExternalResource.deleting_link_by_name(name=chosen_name)
    update.message.reply_text(text=st.successful_del_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def text_requested_to_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=st.text_requested)
    return cs.DELETE_STATE

def text_requested_to_choose(update: Update, context: CallbackContext):
    update.message.reply_text(text=st.text_requested)
    return cs.SEND_STATE

def stop(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END

