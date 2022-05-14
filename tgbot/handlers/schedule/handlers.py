from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from tgbot.models import Schedule, InternalResource, InternalResourceFile
from tgbot.handlers.schedule.keyboards import (
    make_keyboard_for_choosing_day, 
    make_keyboard_for_editing_day_schedule, 
    make_keyboard_for_editing_time_schedule,
    make_keyboard_set_or_delete,
    make_keyboard_for_skip_and_cancel,
    make_keyboard_for_deleting_file,
    make_keyboard_to_stop_receiving_files
)
import tgbot.handlers.schedule.static_text as sched_st
import tgbot.handlers.schedule.conversation_states as sched_cs

def choose_day(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text=sched_st.choose_day_text, reply_markup=make_keyboard_for_choosing_day())
    return sched_cs.CHOOSE_TIME

def make_string_schedule(sched):
    text = f'{sched_st.alarm_emojie}  {sched.time}\n'
    if sched.group:
        text += f'{sched_st.group_emojie}  {sched.group}\n'
    text += f' {sched_st.punship_emojie}  {sched.lesson}\n'
    if sched.isOnline:
        text += f'{sched_st.train_emojie}  {sched.isOnline}\n'
    if sched.teacher:
        text += f'{sched_st.teacher_emojie}  {sched.teacher}\n'
    return text

#sending file schedule
def send_file_schedule(update: Update, context: CallbackContext):
    internal_resource = InternalResource.get_schedule()
    if internal_resource:
        internal_files = InternalResourceFile.get_files(internal_resource=internal_resource[0])
        internal_files_num = len(internal_files)
    else:
        update.message.reply_text(text=sched_st.no_files_yet, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if internal_files_num > 0:
        for internal_file in internal_files:
            if internal_file.photo_id:    
                update.message.reply_photo(photo=internal_file.photo_id, reply_markup=ReplyKeyboardRemove())
            elif internal_file.file_id:
                update.message.reply_document(document=internal_file.file_id, reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text(text=sched_st.no_files_yet, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

#sending text schedule
def send_schedule(update: Update, context: CallbackContext):
    day = update.message.text
    schedule_in_chosen_day = Schedule.objects.all().filter(day=day)
    if schedule_in_chosen_day:
        update.message.reply_text('--' + day + '--', reply_markup=ReplyKeyboardRemove())
        for time in sched_st.TIME_TO_EDIT:
            for sched in schedule_in_chosen_day:
                if sched.time == time:
                    text = make_string_schedule(sched)
                    update.message.reply_text(text=text)
        return ConversationHandler.END
    else:
        update.message.reply_text(text=sched_st.no_lessons_text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

# editing time in schedule
def send_keyboard_for_editing_day(update: Update, context: CallbackContext):
    update.message.reply_text(text=sched_st.choose_day_text, reply_markup=make_keyboard_for_editing_day_schedule())
    return sched_cs.CHOOSE_TIME_FOR_EDITING

def make_string_schedule_to_edit(sched):
    text = f'[{sched.time}]'
    if sched.group:
        text += f'  [{sched.group}]'
    text += f' [{sched.lesson}]'
    if sched.isOnline:
        text += f'  [{sched.isOnline}]'
    if sched.teacher:
        text += f'  [{sched.teacher}]'
    return text

#asking user add or delete files
def add_or_delete_file(update: Update, context: CallbackContext):
    if update.message.text == sched_st.SEND_PHOTO_FOR_EDITING_BUTTON:
        update.message.reply_text(text=sched_st.send_your_files_text, reply_markup=ReplyKeyboardRemove())
        return sched_cs.SEND_SCHEDULE_FILE_FOR_ADDING
    else:
        internal_resource = InternalResource.get_schedule()
        if internal_resource:
            internal_files = InternalResourceFile.get_files(internal_resource=internal_resource[0])
            internal_files_num = len(internal_files)
        else:
            update.message.reply_text(text=sched_st.nothing_to_delete_text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        
        if internal_files_num > 0:
            update.message.reply_text(
                text=sched_st.choose_file_to_delete_text, 
                reply_markup=make_keyboard_for_deleting_file(file_num=internal_files_num)
            )

            file_list_for_deletion = []
            
            for i in range(internal_files_num):
                text = f"{i + 1}"
                update.message.reply_text(text=text)
                if internal_files[i].photo_id:
                    file_list_for_deletion.append(internal_files[i].photo_id)    
                    update.message.reply_photo(photo=internal_files[i].photo_id)
                elif internal_files[i].file_id:
                    file_list_for_deletion.append(internal_files[i].file_id)
                    update.message.reply_document(document=internal_files[i].file_id)
                context.user_data["file_list_for_deletion"] = file_list_for_deletion

            return sched_cs.CHOOSE_FILE_TO_DELETE
        else:
            update.message.reply_text(text=sched_st.nothing_to_delete_text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

#user send his photos and files
def add_schedule_photo(update: Update, context: CallbackContext):
    update.message.reply_text(text="Фото принято...", reply_markup=make_keyboard_to_stop_receiving_files())
    photo_id = update.message.photo[-1].file_id
    internal_resource = InternalResource.update_int_res(name="schedule_files", is_schedule=True)
    internal_file = InternalResourceFile(internal_resource=internal_resource, photo_id=photo_id)
    internal_file.save()
    return sched_cs.SEND_SCHEDULE_FILE_FOR_ADDING
    
def add_schedule_file(update: Update, context: CallbackContext):
    update.message.reply_text(text="Файл принят...", reply_markup=make_keyboard_to_stop_receiving_files())
    file_id = update.message.document.file_id
    internal_resource = InternalResource.update_int_res(name="schedule_files", is_schedule=True)
    internal_file = InternalResourceFile(internal_resource=internal_resource, file_id=file_id)
    internal_file.save()
    return sched_cs.SEND_SCHEDULE_FILE_FOR_ADDING

def end_sending_files(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer == sched_st.NO_MORE_FILES_BUTTON:
        update.message.reply_text(text=sched_st.successful_editing, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(text=sched_st.send_your_files_text, reply_markup=ReplyKeyboardRemove())
        return sched_cs.SEND_SCHEDULE_FILE_FOR_ADDING

def delete_chosen_file(update: Update, context: CallbackContext):
    index_to_delete = int(update.message.text) - 1
    file_list_for_deleltion = context.user_data["file_list_for_deletion"]
    file_id = file_list_for_deleltion[index_to_delete]
    InternalResourceFile.delete_chosen_file_by_id(file_id=file_id)
    update.message.reply_text(text=sched_st.successful_editing, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def number_requested_to_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=sched_st.number_requested_text)
    return sched_cs.CHOOSE_FILE_TO_DELETE

def send_keyboard_for_editing_time(update: Update, context: CallbackContext):
    day = update.message.text.split()[1]
    context.user_data["day"] = day
    schedule_in_chosen_day = Schedule.objects.all().filter(day=day)
    update.message.reply_text(
        text=sched_st.what_needs_change_text, 
        reply_markup=make_keyboard_for_editing_time_schedule()
    )
    if schedule_in_chosen_day:
        update.message.reply_text('--' + schedule_in_chosen_day[0].day + '--')
    else:
        update.message.reply_text(text=sched_st.no_lessons_text)
    for time in sched_st.TIME_TO_EDIT:
        for sched in schedule_in_chosen_day:
            if sched.time == time:
                text = make_string_schedule_to_edit(sched)
                update.message.reply_text(text=text)
    return sched_cs.EDIT_OR_DELETE

def cancel_editing(update:Update, context: CallbackContext):
    update.message.reply_text(text=sched_st.cancel_editing_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def set_or_delete(update: Update, context: CallbackContext):
    context.user_data["time"] = update.message.text
    update.message.reply_text(text=sched_st.set_or_delete_text, reply_markup=make_keyboard_set_or_delete())
    
def send_request_for_editing(update: Update, context: CallbackContext):
    update.message.reply_text(text=sched_st.put_lesson_name, reply_markup=ReplyKeyboardRemove())
    return sched_cs.EDIT_LESSON
    
def clear_chosen_time_field(update: Update, context: CallbackContext):
    Schedule.deleting_schedule(context=context)
    update.message.reply_text(text=sched_st.sucessful_deleting, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def change_lesson(update: Update, context: CallbackContext):
    context.user_data["lesson"] = update.message.text
    update.message.reply_text(text=sched_st.put_format_of_learning, reply_markup=make_keyboard_for_skip_and_cancel())
    return sched_cs.EDIT_PLACE

def change_place_lesson(update: Update, context: CallbackContext):
    context.user_data["isOnline"] = update.message.text
    update.message.reply_text(
        text=sched_st.put_group_name, 
        reply_markup=make_keyboard_for_skip_and_cancel()
    )
    return sched_cs.EDIT_GROUP

def skip_place_change(update: Update, context: CallbackContext):
    context.user_data["isOnline"] = ""
    update.message.reply_text(text=sched_st.put_group_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return sched_cs.EDIT_GROUP

def skip_group_change(update: Update, context: CallbackContext):
    context.user_data["group"] = ""
    update.message.reply_text(text=sched_st.put_teacher_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return sched_cs.EDIT_TEACHER

def change_group(update: Update, context: CallbackContext):
    context.user_data["group"] = update.message.text
    update.message.reply_text(text=sched_st.put_teacher_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return sched_cs.EDIT_TEACHER

def skip_teacher_change(update: Update, context: CallbackContext):
    context.user_data["teacher"] = ""
    Schedule.update_schedule(context=context)
    context.user_data.clear()
    update.message.reply_text(text=sched_st.successful_editing, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def change_teacher(update: Update, context: CallbackContext):
    context.user_data["teacher"] = update.message.text
    Schedule.update_schedule(context=context)
    update.message.reply_text(text=sched_st.successful_editing, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def stop_editing(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END

