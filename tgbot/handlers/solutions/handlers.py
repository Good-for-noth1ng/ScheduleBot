from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
import os
from pathlib import Path
from tgbot.models import Solution
from tgbot.handlers.solutions.static_text import (
    no_solution_yet_text,
    add_or_delete_text,
    put_solution_name_text,
    put_solution_task_text,
    solution_is_added_text,
    choose_solution_to_delete_text,
    successful_del_text,
    nothing_to_delete_text,
    number_requested_text,
    cancel_delete_text,
    which_solution_text,

    ADD_SLTN_BTN,
    DLT_SLTN_BTN,
    CNCL_DLT_SLTN_BTN,
)
from tgbot.handlers.solutions.keyboards import make_keyboard_add_or_delete_solution, make_keyboard_to_choose_or_delete
from tgbot.handlers.solutions.conversation_state import (
    SEND_SOLUTION_STATE,
    ADD_OR_DLT_SLTN_STATE,
    ADD_SLTN_NM_STATE,
    ADD_SLTN_TSK_STATE,
    DLT_SLTN_STATE
)
from dtb.settings import MEDIA_ROOT

def ask_which_solution(update: Update, context: CallbackContext):
    solution_num = Solution.get_num_of_solutions()
    if solution_num > 0:
        update.message.reply_text(text=which_solution_text)
        text = Solution.make_string_for_choosing_solution()
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose_or_delete(link_list_lenght=solution_num))
        return SEND_SOLUTION_STATE
    else:
        update.message.reply_text(no_solution_yet_text)
        return ConversationHandler.END

def send_solution(update: Update, context: CallbackContext):
    chosed_solution_index = int(update.message.text) - 1
    Solution.sending_chosed_solution(index=chosed_solution_index, update=update)
    return ConversationHandler.END
    
def ask_add_or_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=add_or_delete_text, reply_markup=make_keyboard_add_or_delete_solution())
    return ADD_OR_DLT_SLTN_STATE

def start_add(update: Update, context: CallbackContext):
    update.message.reply_text(text=put_solution_name_text, reply_markup=ReplyKeyboardRemove())
    return ADD_SLTN_NM_STATE

def start_delete(update: Update, context: CallbackContext):
    solution_num = Solution.objects.count()
    if solution_num > 0:
        update.message.reply_text(text=choose_solution_to_delete_text)
        text = Solution.make_string_for_choosing_solution()
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose_or_delete(solution_num))
        return DLT_SLTN_STATE
    else: 
        update.message.reply_text(nothing_to_delete_text)
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["solution_name"] = update.message.text
    update.message.reply_text(text=put_solution_task_text)
    return ADD_SLTN_TSK_STATE

def cancel_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=cancel_delete_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def add_task_text(update: Update, context: CallbackContext):
    task = update.message.text
    name = context.user_data["solution_name"]
    solution = Solution(name=name, text=task)
    solution.save()
    update.message.reply_text(solution_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def add_task_file(update: Update, context: CallbackContext):
    name = context.user_data["solution_name"]
    file_id = update.message.document.file_id
    solution = Solution(name=name,file_id=file_id)
    solution.save()
    update.message.reply_text(solution_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END
    #Code for saving file in local dir
    # document = update.message.document
    # download_path = os.path.join(MEDIA_ROOT, document.file_name)
    # task = document.get_file().download(custom_path=download_path)     
    # solution = Solution(name=name)
    # solution.file_field = task
    # solution.save()

def add_task_file_as_photo(update: Update, context: CallbackContext):
    name = context.user_data["solution_name"]
    photo_id = update.message.photo[-1].file_id
    solution = Solution(name=name, photo_id=photo_id)
    solution.save()
    update.message.reply_text(solution_is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def delete(update: Update, context: CallbackContext):
    solution_to_delete_index = int(update.message.text) - 1
    Solution.deleting_solution(index=solution_to_delete_index)     
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