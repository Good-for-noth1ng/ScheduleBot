from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from tgbot.models import ExternalResource
import tgbot.handlers.external.static_text as st
from tgbot.handlers.external.keyboards import make_keyboard_add_or_delete, make_keyboard_to_choose
import tgbot.handlers.external.conversation_state as cs

def setting_answer_string(ext_num, is_book=False, is_link=False):
    if ext_num > 0:
        text = ExternalResource.make_string_for_choosing(is_link_to_book=is_book, is_link_to_command=is_link)
    else:
        text = False
    return text

def ask_which_book(update: Update, context: CallbackContext):
    ext_num = ExternalResource.get_books_num()
    context.user_data["ext_type"] = "book"
    is_book = True
    text = setting_answer_string(ext_num=ext_num, is_book=is_book)
    if text:
        update.message.reply_text(text=st.which_book_text)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=ext_num))
        return cs.CHOOSE_CATEGORY_STATE
    else:
        update.message.reply_text(text=st.nothing_yet_text)
        return ConversationHandler.END 

def ask_which_link(update: Update, context: CallbackContext):
    ext_num = ExternalResource.get_urls_num()
    context.user_data["ext_type"] = "link"
    is_link = True
    text = setting_answer_string(ext_num=ext_num, is_link=is_link)
    if text:
        update.message.reply_text(text=st.which_link_text)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=ext_num))
        return cs.CHOOSE_CATEGORY_STATE
    else:
        update.message.reply_text(text=st.nothing_yet_text)
        return ConversationHandler.END

def ask_which_category(update: Update, context: CallbackContext):
    if context.user_data["ext_type"] == "book":
        ExternalResource.sending_chosen_ext_res(index=chosen_index, update=update, is_link_to_book=True)
    elif context.user_data["ext_type"] == "link":
        ExternalResource.sending_chosen_ext_res(index=chosen_index, update=update, is_link_to_command=True)

def send(update: Update, context: CallbackContext):
    chosen_index = int(update.message.text) - 1
    if context.user_data["ext_type"] == "book":
        ExternalResource.sending_chosen_ext_res(index=chosen_index, update=update, is_link_to_book=True)
    elif context.user_data["ext_type"] == "link":
        ExternalResource.sending_chosen_ext_res(index=chosen_index, update=update, is_link_to_command=True)
    context.user_data.clear()
    return ConversationHandler.END

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
        text = ExternalResource.make_string_for_choosing(is_link_to_book=is_book, is_link_to_command=is_link)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=ext_num))
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
    deletion_index = int(update.message.text) - 1
    if context.user_data["ext_type"] == "book":
        ExternalResource.deleting_by_index(index=deletion_index, is_link_to_book=True)
    elif context.user_data["ext_type"] == "link":
        ExternalResource.deleting_by_index(index=deletion_index, is_link_to_command=True)
    update.message.reply_text(text=st.successful_del_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def number_requested_to_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=st.number_requested_text)
    return cs.DELETE_STATE

def number_requested_to_choose(update: Update, context: CallbackContext):
    update.message.reply_text(text=st.number_requested_text)
    return cs.SEND_STATE

def stop(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END

