import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

#static text consts
from tgbot.handlers.onboarding import static_text
#getting info about registred user
from tgbot.handlers.utils.info import extract_user_data_from_update
#creating new user
from tgbot.models import User

def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created.format(first_name=u.first_name)

    update.message.reply_text(text=text)

