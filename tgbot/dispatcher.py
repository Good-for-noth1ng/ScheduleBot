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
    ConversationHandler
)

from dtb.celery import app  # event processing in async mode
from dtb.settings import TELEGRAM_TOKEN, DEBUG, PORT, HEROKU_APP_NAME

from tgbot.handlers.utils import files, error

from tgbot.handlers.onboarding import handlers as onboarding_handlers

from tgbot.handlers.schedule import handlers as schedule_handlers

from tgbot.handlers.schedule.static_text import (
    DAYS_TO_CHOOSE, 
    DAYS_TO_EDIT,
    TIME_TO_EDIT,
    CANCEL_BUTTON,
    SET_BUTTON,
    DELETE_BUTTON,
    SKIP_BUTTON
)
from tgbot.handlers.schedule.conversation_states import (
    CHOOSE_TIME,
    CHOOSE_TIME_FOR_EDITING,
    EDIT_OR_DELETE,
    EDIT_LESSON,
    EDIT_GROUP,
    EDIT_TEACHER,
    EDIT_PLACE
)
from tgbot.handlers.links import handlers as link_handlers
from tgbot.handlers.links.static_text import DELETE_LINK_BUTTON, ADD_BUTTON, CANCEL_DELETE_LINK_BUTTON
from tgbot.handlers.links.conversation_state import (
    ADD_NAME_STATE, 
    ADD_LINK_STATE,
    DELETE_STATE, 
    ADD_OR_DELETE_STATE,
)

from tgbot.handlers.books import handlers as book_handlers
from tgbot.handlers.books.static_text import DELETE_BOOK_BUTTON, ADD_BOOK_BUTTON, CANCEL_DELETE_BUTTON
from tgbot.handlers.books.conversation_state import (
    ADD_BOOK_NAME_STATE,
    ADD_BOOK_LINK_STATE,
    ADD_OR_DELETE_BOOK_STATE,
    DELETE_BOOK_STATE
)

from tgbot.handlers.requirements import handlers as requirement_handlers
from tgbot.handlers.requirements.static_text import DELETE_RQMNT_BUTTON, ADD_RQMNT_BUTTON, CANCEL_DELETE_RQMNT_BUTTON
from tgbot.handlers.requirements.conversation_state import (
    ADD_OR_DELETE_REQUIRE_STATE,
    ADD_REQUIR_NAME_STATE,
    ADD_REQUIRE_STATE,
    DELETE_REQUIRE_STATE
)

from tgbot.handlers.homework import handlers as homework_handlers
from tgbot.handlers.homework.static_text import DELETE_HMWRK_BUTTON, ADD_HMWRK_BUTTON, CANCEL_DELETE_HMWRK_BUTTON
from tgbot.handlers.homework.conversation_state import (
    ADD_HMWRK_NM_STATE,
    ADD_HMWRK_TSK_STATE,
    ADD_OR_DLT_STATE,
    DLT_HMWRK_STATE
)
from tgbot.handlers.solutions import handlers as solution_handlers
from tgbot.handlers.solutions.static_text import DLT_SLTN_BTN, ADD_SLTN_BTN, CNCL_DLT_SLTN_BTN
from tgbot.handlers.solutions.conversation_state import (
    ADD_OR_DLT_SLTN_STATE,
    ADD_SLTN_NM_STATE,
    ADD_SLTN_TSK_STATE,
    DLT_SLTN_STATE
)
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
            CHOOSE_TIME: [
                MessageHandler(Filters.text(DAYS_TO_CHOOSE), schedule_handlers.send_schedule),
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
            CHOOSE_TIME_FOR_EDITING: [
                MessageHandler(Filters.text(DAYS_TO_EDIT), schedule_handlers.send_keyboard_for_editing_time),
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
            ],
            EDIT_OR_DELETE: [
                MessageHandler(Filters.text(TIME_TO_EDIT), schedule_handlers.set_or_delete),
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(SET_BUTTON), schedule_handlers.send_request_for_editing),
                MessageHandler(Filters.text(DELETE_BUTTON), schedule_handlers.clear_chosen_time_field),
            ],
            EDIT_LESSON: [
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text, schedule_handlers.change_lesson),
            ],
            EDIT_PLACE: [
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(SKIP_BUTTON), schedule_handlers.skip_place_change),
                MessageHandler(Filters.text, schedule_handlers.change_place_lesson),
            ],
            EDIT_GROUP: [
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(SKIP_BUTTON), schedule_handlers.skip_group_change),
                MessageHandler(Filters.text, schedule_handlers.change_group),
            ],
            EDIT_TEACHER: [
                MessageHandler(Filters.text(CANCEL_BUTTON), schedule_handlers.cancel_editing),
                MessageHandler(Filters.text(SKIP_BUTTON), schedule_handlers.skip_teacher_change),
                MessageHandler(Filters.text, schedule_handlers.change_teacher),
            ]
        },
        fallbacks=[
            MessageHandler(Filters.command, schedule_handlers.stop_editing)
        ]
    ))

    #send links list
    dp.add_handler(
        CommandHandler("links", link_handlers.send_links)
    )

    #edit links list
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editlinks", link_handlers.ask_add_or_delete),
        ], 
        states={
            ADD_OR_DELETE_STATE: [
                MessageHandler(Filters.text(ADD_BUTTON), link_handlers.start_add),
                MessageHandler(Filters.text(DELETE_LINK_BUTTON), link_handlers.start_delete),               
            ],
            ADD_NAME_STATE: [
                MessageHandler(Filters.text, link_handlers.add_name),
            ],
            ADD_LINK_STATE: [
                MessageHandler(Filters.entity('url'), link_handlers.add_link),
                MessageHandler(Filters.text, link_handlers.url_requested),
            ],
            DELETE_STATE: [
                MessageHandler(Filters.regex(r'^\d*$'), link_handlers.delete),
                MessageHandler(Filters.text(CANCEL_DELETE_LINK_BUTTON), link_handlers.cancel_delete),
                MessageHandler(Filters.text, link_handlers.number_requested),
            ],
        }, 
        fallbacks=[
            MessageHandler(Filters.command, link_handlers.stop_editing)
        ]
    ))

    #send book list
    dp.add_handler(CommandHandler("books", book_handlers.send_books))
    
    #edit book list
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editbooks", book_handlers.ask_add_or_delete),
        ], 
        states={
            ADD_OR_DELETE_BOOK_STATE: [
                MessageHandler(Filters.text(ADD_BOOK_BUTTON), book_handlers.start_add),
                MessageHandler(Filters.text(DELETE_BOOK_BUTTON), book_handlers.start_delete),
            ],
            ADD_BOOK_NAME_STATE: [
                MessageHandler(Filters.text, book_handlers.add_name),
            ],
            ADD_BOOK_LINK_STATE: [
                MessageHandler(Filters.entity('url'), book_handlers.add_book_url),
                MessageHandler(Filters.text, book_handlers.url_requested),
            ],
            DELETE_BOOK_STATE: [
                MessageHandler(Filters.regex(r'^\d*$'), book_handlers.delete),
                MessageHandler(Filters.text(CANCEL_DELETE_BUTTON), book_handlers.cancel_delete),
                MessageHandler(Filters.text, book_handlers.number_requested),
            ],
        }, 
        fallbacks=[
            MessageHandler(Filters.command, book_handlers.stop_editing)
        ]
    ))

    #send requirements list
    #it's list of teacher's requirements
    dp.add_handler(CommandHandler("requirements", requirement_handlers.send_requirements))
    
    #edit requirements list
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editrequirements", requirement_handlers.ask_add_or_delete),
        ], 
        states={
            ADD_OR_DELETE_REQUIRE_STATE: [
                MessageHandler(Filters.text(ADD_RQMNT_BUTTON), requirement_handlers.start_add),
                MessageHandler(Filters.text(DELETE_RQMNT_BUTTON), requirement_handlers.start_delete),
            ],
            ADD_REQUIR_NAME_STATE: [
                MessageHandler(Filters.text, requirement_handlers.add_name),
            ],
            ADD_REQUIRE_STATE: [
                MessageHandler(Filters.text, requirement_handlers.add_require_text),
                MessageHandler(Filters.document, requirement_handlers.add_require_file),
                MessageHandler(Filters.photo, requirement_handlers.add_require_photo_id)
            ],
            DELETE_REQUIRE_STATE: [
                MessageHandler(Filters.regex(r'^\d*$'), requirement_handlers.delete),
                MessageHandler(Filters.text(CANCEL_DELETE_RQMNT_BUTTON), requirement_handlers.cancel_delete),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, requirement_handlers.stop_editing)
        ]
    ))

    #send homework list
    dp.add_handler(CommandHandler("homework", homework_handlers.send_homework))
    
    #edit homework
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("edithomework", homework_handlers.ask_add_or_delete),
        ], 
        states={
            ADD_OR_DLT_STATE: [
                MessageHandler(Filters.text(ADD_HMWRK_BUTTON), homework_handlers.start_add),
                MessageHandler(Filters.text(DELETE_HMWRK_BUTTON), homework_handlers.start_delete),
            ],
            ADD_HMWRK_NM_STATE:[
                MessageHandler(Filters.text, homework_handlers.add_name),
            ],
            ADD_HMWRK_TSK_STATE: [
                MessageHandler(Filters.text, homework_handlers.add_task_text),
                MessageHandler(Filters.document, homework_handlers.add_task_file),
                MessageHandler(Filters.photo, homework_handlers.add_task_file_as_photo),
            ],
            DLT_HMWRK_STATE: [
                MessageHandler(Filters.regex(r'^\d*$'), homework_handlers.delete),
                MessageHandler(Filters.text(CANCEL_DELETE_HMWRK_BUTTON), homework_handlers.cancel_delete),
                MessageHandler(Filters.text, homework_handlers.number_requested),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, homework_handlers.stop_editing)
        ]
    ))
    #send solution
    dp.add_handler(CommandHandler("solution", solution_handlers.send_solution))
    #edit solutions
    dp.add_handler(ConversationHandler(
        entry_points=[
            CommandHandler("editsolution", solution_handlers.ask_add_or_delete),
        ], 
        states={
            ADD_OR_DLT_SLTN_STATE: [
                MessageHandler(Filters.text(ADD_SLTN_BTN), solution_handlers.start_add),
                MessageHandler(Filters.text(DLT_SLTN_BTN), solution_handlers.start_delete),
            ],
            ADD_SLTN_NM_STATE: [
                MessageHandler(Filters.text, solution_handlers.add_name),
            ],
            ADD_SLTN_TSK_STATE: [
                MessageHandler(Filters.text, solution_handlers.add_task_text),
                MessageHandler(Filters.document, solution_handlers.add_task_file),
                MessageHandler(Filters.photo, solution_handlers.add_task_file_as_photo),
            ],
            DLT_SLTN_STATE: [
                MessageHandler(Filters.regex(r'^\d*$'), solution_handlers.delete),
                MessageHandler(Filters.text(CANCEL_DELETE_HMWRK_BUTTON), solution_handlers.cancel_delete),
                MessageHandler(Filters.text, solution_handlers.number_requested),
            ]
        }, 
        fallbacks=[
            MessageHandler(Filters.command, solution_handlers.stop_editing)
        ]
    ))
    
    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
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

    updater.start_webhook(
        listen="0.0.0.0", 
        port=PORT, 
        url_path=TELEGRAM_TOKEN,
        webhook_url='https://' + HEROKU_APP_NAME +'.herokuapp.com/' + TELEGRAM_TOKEN
    )
    
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
            'editlinks': 'Добавить/удалить ссылку 🖊️',
            'books': 'Список книг 📚',
            'editbooks': 'Добавить/удалить книгу 📝',
            'requirements': 'Список требований 📖',
            'editrequirements': 'Изменить требования 🖍️',
            'homework': 'Узнать что задано 📅',
            'edithomework': 'Добавить/удалить домашку ✒️',
            'solution': 'Чужие решения 🕯️',
            'editsolution': 'Добавить/удалить решение 🖋️',
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
