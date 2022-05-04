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
from tgbot.handlers.schedule.static_text import (
    choose_day_text, 
    no_lessons_text, 
    what_needs_change_text, 
    alarm_emojie, 
    punship_emojie,
    cancel_editing_text,
    set_or_delete_text,
    put_lesson_name,
    successful_editing,
    sucessful_deleting,
    put_group_name,
    put_teacher_name,
    group_emojie,
    teacher_emojie,
    train_emojie,
    put_format_of_learning,
    file_is_added,
    send_your_files_text,
    number_requested_text,
    sucessful_file_deletion,
    no_files_yet,
    nothing_to_delete_text,
    TIME_TO_EDIT,
    NO_MORE_FILES_BUTTON,
    MORE_FILES_BUTTON,
    DELETE_PHOTO_BUTTON,
    SEND_PHOTO_FOR_EDITING_BUTTON
)

from tgbot.handlers.schedule.conversation_states import ( 
    CHOOSE_TIME,
    CHOOSE_TIME_FOR_EDITING,
    EDIT_OR_DELETE,
    EDIT_LESSON,
    EDIT_GROUP,
    EDIT_TEACHER,
    EDIT_PLACE,
    SEND_SCHEDULE_FILE_FOR_ADDING,
    CHOOSE_FILE_TO_DELETE,
    DELETE_FILE
)

def choose_day(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(text=choose_day_text, reply_markup=make_keyboard_for_choosing_day())
    return CHOOSE_TIME

def make_string_schedule(sched):
    text = f'{alarm_emojie}  {sched.time}\n'
    if sched.group:
        text += f'{group_emojie}  {sched.group}\n'
    text += f' {punship_emojie}  {sched.lesson}\n'
    if sched.isOnline:
        text += f'{train_emojie}  {sched.isOnline}\n'
    if sched.teacher:
        text += f'{teacher_emojie}  {sched.teacher}\n'
    return text

#sending file schedule
def send_file_schedule(update: Update, context: CallbackContext):
    internal_resource = InternalResource.get_schedule()
    if internal_resource:
        internal_files = InternalResourceFile.get_files(internal_resource=internal_resource[0])
        internal_files_num = len(internal_files)
    else:
        update.message.reply_text(text=no_files_yet, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    if internal_files_num > 0:
        for internal_file in internal_files:
            if internal_file.photo_id:    
                update.message.reply_photo(photo=internal_file.photo_id)
            elif internal_file.file_id:
                update.message.reply_document(document=internal_file.file_id)
    else:
        update.message.reply_text(text=no_files_yet, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

#sending text schedule
def send_schedule(update: Update, context: CallbackContext):
    day = update.message.text
    schedule_in_chosen_day = Schedule.objects.all().filter(day=day)
    if schedule_in_chosen_day:
        update.message.reply_text('--' + day + '--', reply_markup=ReplyKeyboardRemove())
        for time in TIME_TO_EDIT:
            for sched in schedule_in_chosen_day:
                if sched.time == time:
                    text = make_string_schedule(sched)
                    update.message.reply_text(text=text)
        return ConversationHandler.END
    else:
        update.message.reply_text(text=no_lessons_text)
        return ConversationHandler.END

def cancel_sending_schedule(update: Update, context: CallbackContext):
    context.user_data.clear()
    update.message.reply_markup(ReplyKeyboardRemove())
    return ConversationHandler.END

# editing time in schedule
def send_keyboard_for_editing_day(update: Update, context: CallbackContext):
    update.message.reply_text(text=choose_day_text, reply_markup=make_keyboard_for_editing_day_schedule())
    return CHOOSE_TIME_FOR_EDITING

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
    if update.message.text == SEND_PHOTO_FOR_EDITING_BUTTON:
        update.message.reply_text(text=send_your_files_text, reply_markup=ReplyKeyboardRemove())
        return SEND_SCHEDULE_FILE_FOR_ADDING
    else:
        internal_resource = InternalResource.get_schedule()
        if internal_resource:
            internal_files = InternalResourceFile.get_files(internal_resource=internal_resource[0])
            internal_files_num = len(internal_files)
        else:
            update.message.reply_text(text=nothing_to_delete_text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END
        if internal_files_num > 0:
            update.message.reply_text(
                text="Выбери файл для удаления", 
                reply_markup=make_keyboard_for_deleting_file(file_num=internal_files_num)
            )
            for i in range(internal_files_num):
                text = f"{i + 1}"
                update.message.reply_text(text=text)
                if internal_files[i].photo_id:    
                    update.message.reply_photo(photo=internal_files[i].photo_id)
                elif internal_files[i].file_id:
                    update.message.reply_document(document=internal_files[i].file_id)
            return CHOOSE_FILE_TO_DELETE
        else:
            update.message.reply_text(text=nothing_to_delete_text, reply_markup=ReplyKeyboardRemove())
            return ConversationHandler.END

#user send his photos and files
def add_schedule_photo(update: Update, context: CallbackContext):
    update.message.reply_text(text="Фото принято...", reply_markup=make_keyboard_to_stop_receiving_files())
    photo_id = update.message.photo[-1].file_id
    internal_resource = InternalResource.update_int_res(name="schedule_files", is_schedule=True)
    internal_file = InternalResourceFile(internal_resource=internal_resource, photo_id=photo_id)
    internal_file.save()
    return SEND_SCHEDULE_FILE_FOR_ADDING
    
def add_schedule_file(update: Update, context: CallbackContext):
    update.message.reply_text(text="Файл принят...", reply_markup=make_keyboard_to_stop_receiving_files())
    file_id = update.message.document.file_id
    internal_resource = InternalResource.update_int_res(name="schedule_files", is_schedule=True)
    internal_file = InternalResourceFile(internal_resource=internal_resource, file_id=file_id)
    internal_file.save()
    return SEND_SCHEDULE_FILE_FOR_ADDING

def end_sending_files(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer == NO_MORE_FILES_BUTTON:
        update.message.reply_text(text=successful_editing, reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()
        return ConversationHandler.END
    else:
        update.message.reply_text(text=send_your_files_text, reply_markup=ReplyKeyboardRemove())
        return SEND_SCHEDULE_FILE_FOR_ADDING

def delete_chosen_file(update: Update, context: CallbackContext):
    index_to_delete = int(update.message.text) - 1
    InternalResourceFile.delete_chosen_file(index=index_to_delete)
    update.message.reply_text(text=sucessful_file_deletion, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def number_requested_to_delete(update: Update, context: CallbackContext):
    update.message.reply_text(text=number_requested_text)
    return CHOOSE_FILE_TO_DELETE

def send_keyboard_for_editing_time(update: Update, context: CallbackContext):
    day = update.message.text.split()[1]
    context.user_data["day"] = day
    schedule_in_chosen_day = Schedule.objects.all().filter(day=day)
    update.message.reply_text(text=what_needs_change_text, reply_markup=make_keyboard_for_editing_time_schedule())
    if schedule_in_chosen_day:
        update.message.reply_text('--' + schedule_in_chosen_day[0].day + '--')
    else:
        update.message.reply_text(text=no_lessons_text)
    for time in TIME_TO_EDIT:
        for sched in schedule_in_chosen_day:
            if sched.time == time:
                text = make_string_schedule_to_edit(sched)
                update.message.reply_text(text=text)
    return EDIT_OR_DELETE

def cancel_editing(update:Update, context: CallbackContext):
    update.message.reply_text(text=cancel_editing_text, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def set_or_delete(update: Update, context: CallbackContext):
    context.user_data["time"] = update.message.text
    update.message.reply_text(text=set_or_delete_text, reply_markup=make_keyboard_set_or_delete())
    
def send_request_for_editing(update: Update, context: CallbackContext):
    update.message.reply_text(text=put_lesson_name, reply_markup=ReplyKeyboardRemove())
    return EDIT_LESSON
    
def clear_chosen_time_field(update: Update, context: CallbackContext):
    Schedule.deleting_schedule(context=context)
    update.message.reply_text(text=sucessful_deleting)
    context.user_data.clear()
    return ConversationHandler.END

def change_lesson(update: Update, context: CallbackContext):
    context.user_data["lesson"] = update.message.text
    update.message.reply_text(text=put_format_of_learning, reply_markup=make_keyboard_for_skip_and_cancel())
    return EDIT_PLACE

def change_place_lesson(update: Update, context: CallbackContext):
    context.user_data["isOnline"] = update.message.text
    update.message.reply_text(text=put_group_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return EDIT_GROUP

def skip_place_change(update: Update, context: CallbackContext):
    context.user_data["isOnline"] = ""
    update.message.reply_text(text=put_group_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return EDIT_GROUP

def skip_group_change(update: Update, context: CallbackContext):
    context.user_data["group"] = ""
    update.message.reply_text(text=put_teacher_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return EDIT_TEACHER

def change_group(update: Update, context: CallbackContext):
    context.user_data["group"] = update.message.text
    update.message.reply_text(text=put_teacher_name, reply_markup=make_keyboard_for_skip_and_cancel())
    return EDIT_TEACHER

def skip_teacher_change(update: Update, context: CallbackContext):
    context.user_data["teacher"] = ""
    Schedule.update_schedule(context=context)
    context.user_data.clear()
    update.message.reply_text(text=successful_editing, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def change_teacher(update: Update, context: CallbackContext):
    context.user_data["teacher"] = update.message.text
    Schedule.update_schedule(context=context)
    update.message.reply_text(text=successful_editing, reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def stop_editing(update: Update, context: CallbackContext):
    context.user_data.clear()
    try:
        update.message.reply_markup(ReplyKeyboardRemove())
        return ConversationHandler.END
    except TypeError:
        return ConversationHandler.END

