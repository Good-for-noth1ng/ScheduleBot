"""
    Telegram event handlers
"""
import sys
import logging
from typing import Dict

import telegram.error
from telegram import Bot, Update, BotCommand
from telegram.ext import (
    Updater, Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler, BaseFilter,
    ConversationHandler, CallbackContext
)

from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG, PORT, HEROKU_APP_NAME

from tgbot.handlers.utils import error 

from tgbot.handlers.onboarding import handlers as onboarding_handlers

from tgbot.handlers.schedule import handlers as schedule_handlers
import tgbot.handlers.schedule.static_text as schedule_st
import tgbot.handlers.schedule.conversation_states as schedule_cs

from tgbot.handlers.external import handlers as ext_handlers
import tgbot.handlers.external.static_text as st
import tgbot.handlers.external.conversation_state as cs

from tgbot.handlers.internal import handlers as int_handlers
import tgbot.handlers.internal.conversation_state as int_cs
import tgbot.handlers.internal.static_text as int_st

def setup_dispatcher(dp):
    # 
    # Adding handlers for events from Telegram
    # 
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # request for sending schedule
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("schedule", schedule_handlers.choose_day),
        ], 
        states={
            schedule_cs.CHOOSE_TIME: [
                MessageHandler(Filters.text(schedule_st.DAYS_TO_CHOOSE), schedule_handlers.send_schedule),
                MessageHandler(Filters.text(schedule_st.SEND_PHOTO_BUTTON), schedule_handlers.send_file_schedule)
            ],
        }, 
        fallbacks=[
            MessageHandler(Filters.command, schedule_handlers.stop_editing)
        ]
    ))
    # add/delete schedule
    # adding time, lesson, group, teacher name
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editschedule", schedule_handlers.send_keyboard_for_editing_day),
        ],
        states={
            schedule_cs.CHOOSE_TIME_FOR_EDITING: [
                MessageHandler(Filters.text(schedule_st.DAYS_TO_EDIT), schedule_handlers.send_keyboard_for_editing_time),
                MessageHandler(Filters.text(schedule_st.SEND_PHOTO_FOR_EDITING_BUTTON), schedule_handlers.add_or_delete_file),
                MessageHandler(Filters.text(schedule_st.DELETE_PHOTO_BUTTON), schedule_handlers.add_or_delete_file),
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
            ],
            schedule_cs.SEND_SCHEDULE_FILE_FOR_ADDING: [
                MessageHandler(Filters.photo, schedule_handlers.add_schedule_photo),
                MessageHandler(Filters.document, schedule_handlers.add_schedule_file),
                MessageHandler(Filters.text(schedule_st.NO_MORE_FILES_BUTTON), schedule_handlers.end_sending_files),
                MessageHandler(Filters.text(schedule_st.MORE_FILES_BUTTON), schedule_handlers.end_sending_files)
            ],
            schedule_cs.CHOOSE_FILE_TO_DELETE: [
                MessageHandler(Filters.regex(r'^\d*$'), schedule_handlers.delete_chosen_file),
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.all, schedule_handlers.number_requested_to_delete),
            ],
            schedule_cs.EDIT_OR_DELETE: [
                MessageHandler(Filters.text(schedule_st.TIME_TO_EDIT), schedule_handlers.set_or_delete),
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(schedule_st.SET_BUTTON), schedule_handlers.send_request_for_editing),
                MessageHandler(Filters.text(schedule_st.DELETE_BUTTON), schedule_handlers.clear_chosen_time_field),
            ],
            schedule_cs.EDIT_LESSON: [
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text, schedule_handlers.change_lesson),
            ],
            schedule_cs.EDIT_PLACE: [
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(schedule_st.SKIP_BUTTON), schedule_handlers.skip_place_change),
                MessageHandler(Filters.text, schedule_handlers.change_place_lesson),
            ],
            schedule_cs.EDIT_GROUP: [
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(schedule_st.SKIP_BUTTON), schedule_handlers.skip_group_change),
                MessageHandler(Filters.text, schedule_handlers.change_group),
            ],
            schedule_cs.EDIT_TEACHER: [
                MessageHandler(Filters.text(schedule_st.CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(schedule_st.SKIP_BUTTON), schedule_handlers.skip_teacher_change),
                MessageHandler(Filters.text, schedule_handlers.change_teacher),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.command, schedule_handlers.stop_editing)
        ]
    ))

    #send links or books
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("links", ext_handlers.ask_which_link),
            CommandHandler("books", ext_handlers.ask_which_book)
        ], 
        states={
            cs.SEND_STATE: [
                MessageHandler(Filters.text(st.CANCEL_BUTTON), ext_handlers.cancel),
                MessageHandler(Filters.text, ext_handlers.send),
                MessageHandler(Filters.all, ext_handlers.text_requested_to_choose),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, ext_handlers.stop)
        ]
    ))

    #edit links or books
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editbooks", ext_handlers.ask_add_or_delete_book),
            CommandHandler("editlinks", ext_handlers.ask_add_or_delete_link), 
        ], 
        states={
            cs.ADD_OR_DELETE_STATE: [
                MessageHandler(Filters.text(st.ADD_BUTTON), ext_handlers.start_add),
                MessageHandler(Filters.text(st.DELETE_BUTTON), ext_handlers.start_delete),               
            ],
            cs.ADD_NAME_STATE: [
                MessageHandler(Filters.text, ext_handlers.add_name),
            ],
            cs.ADD_URL_STATE: [
                MessageHandler(Filters.entity('url'), ext_handlers.add_link),
                MessageHandler(Filters.text, ext_handlers.url_requested),
            ],
            cs.DELETE_STATE: [
                MessageHandler(Filters.text(st.CANCEL_BUTTON), ext_handlers.cancel),
                MessageHandler(Filters.text, ext_handlers.delete),
                MessageHandler(Filters.all, ext_handlers.text_requested_to_delete),
            ],
        }, 
        fallbacks=[
            MessageHandler(Filters.command, ext_handlers.stop)
        ]
    ))

    #send homework, requirements or solutions
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("homework", int_handlers.ask_which_homework),
            CommandHandler("solution", int_handlers.ask_which_solution),
            CommandHandler("requirements", int_handlers.ask_which_requirement)
        ], 
        states={
            int_cs.SEND_STATE: [
                MessageHandler(Filters.text(int_st.CANCEL_BUTTON), int_handlers.cancel),
                MessageHandler(Filters.text, int_handlers.send),
                MessageHandler(Filters.all, int_handlers.number_requested_to_choose),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, int_handlers.stop)
        ]
    ))
    
    #edit requirements, homework or solutions
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("edithomework", int_handlers.ask_add_or_delete_homework),
            CommandHandler("editsolution", int_handlers.ask_add_or_delete_solution),
            CommandHandler("editrequirements", int_handlers.ask_add_or_delete_requirement)
        ], 
        states={
            int_cs.ADD_OR_DELETE_STATE: [
                MessageHandler(Filters.text(int_st.ADD_BUTTON), int_handlers.start_add),
                MessageHandler(Filters.text(int_st.DELETE_BUTTON), int_handlers.start_delete)
            ],
            int_cs.ADD_NAME_STATE: [
                MessageHandler(Filters.text, int_handlers.add_name)
            ],
            int_cs.ADD_TASK_STATE: [
                MessageHandler(
                    Filters.text(int_st.NO_MORE_FILES_BUTTON), 
                    int_handlers.end_receiving_files
                ),
                MessageHandler(
                    Filters.text(int_st.MORE_FILES_BUTTON), 
                    int_handlers.end_receiving_files
                ),
                MessageHandler(Filters.text, int_handlers.add_task_text),
                MessageHandler(Filters.document, int_handlers.add_task_file),
                MessageHandler(Filters.photo, int_handlers.add_task_photo),
            ],
            int_cs.DELETE_STATE: [
                MessageHandler(Filters.text(int_st.CANCEL_BUTTON), int_handlers.cancel),
                MessageHandler(Filters.text, int_handlers.delete),
                MessageHandler(Filters.all, int_handlers.number_requested_to_delete),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, int_handlers.stop)
        ]
    ))
    
    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


def run_pooling():
    """ Run bot in pooling mode """
    updater = Updater(TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    #Run with webhook
    updater.start_webhook(
        listen="0.0.0.0", 
        port=PORT, 
        url_path=TELEGRAM_TOKEN,
        webhook_url='https://' + HEROKU_APP_NAME +'.herokuapp.com/' + TELEGRAM_TOKEN
    )
    
    #Run in pooling mode
    # bot_info = Bot(TELEGRAM_TOKEN).get_me()
    # bot_link = f"https://t.me/" + bot_info["username"]
    # print(f"Pooling of '{bot_link}' started")
    # updater.start_polling()

    updater.idle()


# Global variable - best way I found to init Telegram bot
bot = Bot(TELEGRAM_TOKEN)
try:
    TELEGRAM_BOT_USERNAME = bot.get_me()["username"]
except telegram.error.Unauthorized:
    logging.error(f"Invalid TELEGRAM_TOKEN.")
    sys.exit(1)


@app.task(ignore_result=True)
def process_telegram_event(update_json):
    update = Update.de_json(update_json, bot)
    dispatcher.process_update(update)


def set_up_commands(bot_instance: Bot) -> None:
    langs_with_commands: Dict[str, Dict[str, str]] = {
        'ru': {
            'start': 'Запустить бота 🚀',
            'schedule': 'Узнать расписание 👀',
            'editschedule': 'Изменить расписание ✏️',
            'links': 'Ссылки на команды MSTeams 🔗',
            'editlinks': '+/- ссылку 🖊️',
            'books': 'Список книг 📚',
            'editbooks': '+/- книгу 📝',
            'requirements': 'Список требований 📖',
            'editrequirements': '+/- требования 🖍️',
            'homework': 'Узнать что задано 📅',
            'edithomework': '+/- домашку ✒️',
            'solution': 'Чужие решения 🕯️',
            'editsolution': '+/- решение 🖋️',
        }
    }
    
    bot_instance.delete_my_commands()
    language_code='ru'
    bot_instance.set_my_commands(
        language_code=language_code,
        commands=[
            BotCommand(command, description) for command, description in langs_with_commands[language_code].items()
        ]
    )


# WARNING: it's better to comment the line below in DEBUG mode.
# Likely, you'll get a flood limit control error, when restarting bot too often
set_up_commands(bot)

n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
