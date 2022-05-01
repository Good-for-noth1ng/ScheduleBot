from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)

from tgbot.models import InternalResource, InternalResourceFile
import tgbot.handlers.internal.conversation_state as int_cs
import tgbot.handlers.internal.static_text as int_st
from tgbot.handlers.internal.keyboards import make_keyboard_add_or_delete, make_keyboard_to_choose, make_keyboard_to_stop_receiving_files

def setting_answer_string(int_num, is_homework=False, is_requirement=False, is_solution=False):
    if int_num > 0:
        text = InternalResource.make_string_for_choosing(
            is_homework=is_homework, 
            is_solution=is_solution, 
            is_requirement=is_requirement
        )
    else: 
        text = False
    return text

def ask_which_homework(update: Update, context: CallbackContext):
    int_num = InternalResource.get_num_of_homeworks()
    context.user_data["int_type"] = "homework"
    text = setting_answer_string(int_num=int_num, is_homework=True)
    if text:
        update.message.reply_text(text=int_st.which_homework_text)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=int_num))
        return int_cs.SEND_STATE
    else:
        update.message.reply_text(text=int_st.no_homework_yet_text)
        return ConversationHandler.END

def ask_which_solution(update: Update, context: CallbackContext):
    int_num = InternalResource.get_num_of_solutions()
    context.user_data["int_type"] = "solution"
    text = setting_answer_string(int_num=int_num, is_solution=True)
    if text:
        update.message.reply_text(text=int_st.which_solution_text)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=int_num))
        return int_cs.SEND_STATE
    else:
        update.message.reply_text(text=int_st.no_solution_yet_text)
        return ConversationHandler.END

def ask_which_requirement(update: Update, context: CallbackContext):
    int_num = InternalResource.get_num_of_requirements()
    context.user_data["int_type"] = "requirement"
    text = setting_answer_string(int_num=int_num, is_requirement=True)
    if text:
        update.message.reply_text(text=int_st.which_requirement_text)
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=int_num))
        return int_cs.SEND_STATE
    else:
        update.message.reply_text(text=int_st.no_requirements_yet_text)
        return ConversationHandler.END

def send(update: Update, context: CallbackContext):
    chosen_index = int(update.message.text) - 1
    if context.user_data["int_type"] == "homework":
        int_res = InternalResource.get_homeworks()
    elif context.user_data["int_type"] == "solution":
        int_res = InternalResource.get_solutions()
    elif context.user_data["int_type"] == "requirement":
        int_res = InternalResource.get_requirements()

    int_res_files = InternalResourceFile.get_files(internal_resource=int_res[chosen_index])
    
    text = f"🧭 {int_res[chosen_index].name}\n"
    if int_res[chosen_index].text:
        text += f"{int_res[chosen_index].text}"
        update.message.reply_text(text=text)
    elif int_res_files:
        update.message.reply_text(text=text)
        for int_res_file in int_res_files:
            if int_res_file.photo_id:
                update.message.reply_photo(photo=int_res_file.photo_id, reply_markup=ReplyKeyboardRemove())
            elif int_res_file.file_id:
                update.message.reply_document(document=int_res_file.file_id, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def ask_add_or_delete_homework(update: Update, context: CallbackContext):
    context.user_data["int_type"] = "homework"
    update.message.reply_text(text=int_st.add_or_delete_text, reply_markup=make_keyboard_add_or_delete())
    return int_cs.ADD_OR_DELETE_STATE

def ask_add_or_delete_solution(update: Update, context: CallbackContext):
    context.user_data["int_type"] = "solution"
    update.message.reply_text(text=int_st.add_or_delete_text, reply_markup=make_keyboard_add_or_delete())
    return int_cs.ADD_OR_DELETE_STATE

def ask_add_or_delete_requirement(update: Update, context: CallbackContext):
    context.user_data["int_type"] = "requirement"
    update.message.reply_text(text=int_st.add_or_delete_text, reply_markup=make_keyboard_add_or_delete())
    return int_cs.ADD_OR_DELETE_STATE

def start_add(update: Update, context: CallbackContext):
    if context.user_data["int_type"] == "homework":
        update.message.reply_text(text=int_st.put_name_text, reply_markup=ReplyKeyboardRemove())
    elif context.user_data["int_type"] == "solution":
        update.message.reply_text(text=int_st.put_name_text, reply_markup=ReplyKeyboardRemove())
    elif context.user_data["int_type"] == "requirement":
        update.message.reply_text(text=int_st.put_name_text, reply_markup=ReplyKeyboardRemove())
    return int_cs.ADD_NAME_STATE

def start_delete(update: Update, context: CallbackContext):
    is_homework = False
    is_solution = False
    is_requirement = False
    if context.user_data["int_type"] == "homework":
        int_num = InternalResource.get_num_of_homeworks()
        is_homework = True
    elif context.user_data["int_type"] == "solution":
        int_num = InternalResource.get_num_of_solutions()
        is_solution = True
    elif context.user_data["int_type"] == "requirement":
        int_num = InternalResource.get_num_of_requirements()
        is_requirement = True
    if int_num > 0:
        text = InternalResource.make_string_for_choosing(
            is_requirement=is_requirement, 
            is_homework=is_homework, 
            is_solution=is_solution
        )
        update.message.reply_text(text=text, reply_markup=make_keyboard_to_choose(link_list_lenght=int_num))
        return int_cs.DELETE_STATE
    else:
        update.message.reply_text(text=int_st.nothing_to_delete_text)
        context.user_data.clear()
        return ConversationHandler.END

def add_name(update: Update, context: CallbackContext):
    context.user_data["name"] = update.message.text
    if context.user_data["int_type"] == "homework":
        does_exist = InternalResource.does_exist(name=context.user_data["name"], is_homework=True)
        if not does_exist:
            update.message.reply_text(text=int_st.put_homework_task_text)
        else:
            update.message.reply_text(text=int_st.isnt_unique_name_text)
            return int_cs.ADD_NAME_STATE
    elif context.user_data["int_type"] == "solution":
        does_exist = InternalResource.does_exist(name=context.user_data["name"], is_solution=True)
        if not does_exist:
            update.message.reply_text(text=int_st.put_solution_task_text)
        else:
            update.message.reply_text(text=int_st.isnt_unique_name_text)
            return int_cs.ADD_NAME_STATE
    elif context.user_data["int_type"] == "requirement":
        does_exist = InternalResource.does_exist(name=context.user_data["name"], is_requirement=True)
        if not does_exist:
            update.message.reply_text(text=int_st.put_requirement_task_text)
        else:
            update.message.reply_text(text=int_st.isnt_unique_name_text)
            return int_cs.ADD_NAME_STATE
    return int_cs.ADD_TASK_STATE

def add_task_file(update: Update, context: CallbackContext):
    update.message.reply_text(text="Файл принят...", reply_markup=make_keyboard_to_stop_receiving_files())
    name = context.user_data["name"]
    file_id = update.message.document.file_id
    if context.user_data["int_type"] == "homework":
        int_res = InternalResource.update_int_res(name=name, is_homework=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, file_id=file_id)
    elif context.user_data["int_type"] == "solution":
        int_res = InternalResource.update_int_res(name=name, is_solution=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, file_id=file_id)
    elif context.user_data["int_type"] == "requirement":
        int_res = InternalResource.update_int_res(name=name, is_requirement=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, file_id=file_id)
    int_res_file.save()
    return int_cs.ADD_TASK_STATE
    ##################################################
    # if context.user_data["int_type"] == "homework":
    #     int_res = InternalResource(name=name, file_id=file_id, is_homework=True)
    # elif context.user_data["int_type"] == "solution":
    #     int_res = InternalResource(name=name, file_id=file_id, is_solution=True)
    # elif context.user_data["int_type"] == "requirement":
    #     int_res = InternalResource(name=name, file_id=file_id, is_requirement=True)
    # int_res.save()
    ############################################
    # update.message.reply_text(int_st.is_added_text)
    # context.user_data.clear()
    # return ConversationHandler.END
    
    
    #Code for saving file in local dir
    # document = update.message.document
    # download_path = os.path.join(MEDIA_ROOT, document.file_name)
    # task = document.get_file().download(custom_path=download_path)     
    # solution = Solution(name=name)
    # solution.file_field = task
    # solution.save()

def add_task_photo(update: Update, context: CallbackContext):
    update.message.reply_text(text="Фото принято...", reply_markup=make_keyboard_to_stop_receiving_files())
    name = context.user_data["name"]
    photo_id = update.message.photo[-1].file_id
    if context.user_data["int_type"] == "homework":
        int_res = InternalResource.update_int_res(name=name, is_homework=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, photo_id=photo_id)
    elif context.user_data["int_type"] == "solution":
        int_res = InternalResource.update_int_res(name=name, is_solution=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, photo_id=photo_id)
    elif context.user_data["int_type"] == "requirement":
        int_res = InternalResource.update_int_res(name=name, is_requirement=True)
        int_res_file = InternalResourceFile(internal_resource=int_res, photo_id=photo_id)
    int_res_file.save()
    return int_cs.ADD_TASK_STATE
    # update.message.reply_text(int_st.is_added_text)
    # context.user_data.clear()
    # return ConversationHandler.END

def end_receiving_files(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer == int_st.NO_MORE_FILES_BUTTON:
        update.message.reply_text(text=int_st.is_added_text, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(text=int_st.send_your_files_text, reply_markup=ReplyKeyboardRemove())
        return int_cs.ADD_TASK_STATE

def add_task_text(update: Update, context: CallbackContext):
    name = context.user_data["name"]
    text = update.message.text
    if context.user_data["int_type"] == "homework":
        int_res = InternalResource(name=name, text=text, is_homework=True)
    elif context.user_data["int_type"] == "solution":
        int_res = InternalResource(name=name, text=text, is_solution=True)
    elif context.user_data["int_type"] == "requirement":
        int_res = InternalResource(name=name, text=text, is_requirement=True)
    int_res.save()
    update.message.reply_text(int_st.is_added_text)
    context.user_data.clear()
    return ConversationHandler.END

def delete(update: Update, context: CallbackContext):
    deletion_index = int(update.message.text) - 1
    if context.user_data["int_type"] == "homework":
        InternalResource.deleting_homework_by_index(index=deletion_index)
    elif context.user_data["int_type"] == "solution":
        InternalResource.deleting_solutions_by_index(index=deletion_index)
    elif context.user_data["int_type"] == "requirement":
        InternalResource.deleting_requirements_by_index(index=deletion_index)
    update.message.reply_text(text=int_st.successful_del_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text(text=int_st.cancel_text,reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def number_requested_to_choose(update: Update, context: CallbackContext):
    update.message.reply_text(text=int_st.number_requested_text)
    return int_cs.SEND_STATE

def number_requested_to_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=int_st.number_requested_text)
    return int_cs.DELETE_STATE

def stop(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END
