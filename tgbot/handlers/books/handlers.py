from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from tgbot.models import Books
from tgbot.handlers.books.static_text import (
    add_or_delete_text,
    no_books_yet_text,
    put_book_name_text,
    choose_book_to_delete_text,
    nothing_to_delete_text,
    put_book_url,
    url_is_added_text,
    successful_del_text,
    number_requested_text,
    cancel_delete_text,
    url_requested_text
)
from tgbot.handlers.books.conversation_state import (
    ADD_BOOK_LINK_STATE,
    ADD_BOOK_NAME_STATE,
    ADD_OR_DELETE_BOOK_STATE,
    DELETE_BOOK_STATE
)
from tgbot.handlers.books.keyboards import make_keyboard_add_or_delete_book, make_keyboard_to_delete_book

def send_books(update:Update, context: CallbackContext):
    text = ""
    books = Books.objects.all()
    if books:
        for book in books:
            text += f'{book.name} - [  {book.url}  ]\n'
        update.message.reply_text(text=text)
    else:
        update.message.reply_text(no_books_yet_text)

def ask_add_or_delete(update:Update, context: CallbackContext):
    update.message.reply_text(text=add_or_delete_text, reply_markup=make_keyboard_add_or_delete_book())
    return ADD_OR_DELETE_BOOK_STATE

def start_add(update:Update, context: CallbackContext):
    update.message.reply_text(text=put_book_name_text, reply_markup=ReplyKeyboardRemove())
    return ADD_BOOK_NAME_STATE

def start_delete(update: Update, context: CallbackContext):
    books = Books.objects.all()
    text = ""
    if books:
        update.message.reply_text(text=choose_book_to_delete_text)
        for i in range(0, len(books)):
            text += f"<--------{i + 1}-------->\n"
            text += f"{books[i].name} - [  {books[i].url}  ]\n"
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_delete_book(len(books)))
        return DELETE_BOOK_STATE
    else: 
        update.message.reply_text(nothing_to_delete_text)
        return ConversationHandler.END

def add_name(update:Update, context: CallbackContext):
    context.user_data["book_name"] = update.message.text
    update.message.reply_text(text=put_book_url)
    return ADD_BOOK_LINK_STATE

def url_requested(update:Update, context: CallbackContext):
    update.message.reply_text(url_requested_text)
    return ADD_BOOK_LINK_STATE

def add_book_url(update:Update, context: CallbackContext):
    url = update.message.text
    name = context.user_data["book_name"]
    book = Books(name=name, url=url)
    book.save()
    update.message.reply_text(url_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def cancel_delete(update:Update, context: CallbackContext):
    update.message.reply_text(text=cancel_delete_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def delete(update:Update, context: CallbackContext):
    book_to_delete_index = int(update.message.text) - 1     
    books = Books.objects.all()
    books[book_to_delete_index].delete()
    update.message.reply_text(text=successful_del_text, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def number_requested(update:Update, context: CallbackContext):
    update.message.reply_text(number_requested_text)
    start_delete(update, context)
    return DELETE_BOOK_STATE

def stop_editing(update:Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END