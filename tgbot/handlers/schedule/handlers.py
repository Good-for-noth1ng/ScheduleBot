from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import (
    CallbackContext,
    ConversationHandler
)
from tgbot.models import Schedule
from tgbot.handlers.schedule.keyboards import (
    make_keyboard_for_choosing_day, 
    make_keyboard_for_editing_day_schedule, 
    make_keyboard_for_editing_time_schedule,
    make_keyboard_set_or_delete,
    make_keyboard_for_skip_and_cancel
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
    TIME_TO_EDIT
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
# sending schedule
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
    lesson = update.message.text
    Schedule.deleting_schedule(user_data=context.user_data)
    # time = context.user_data["time"]
    # day = context.user_data["day"]
    # schedule = Schedule.objects.all().filter(day=day).filter(time=time)
    # for sched in schedule:
    #     if sched:
    #         sched.delete()
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
    Schedule.update_schedule(user_data=context.user_data)
    # schedule, created = Schedule.objects.update_or_create(
    #     day=context.user_data["day"],
    #     time=context.user_data["time"],
    #     defaults={
    #         'lesson': context.user_data["lesson"],
    #         'group': context.user_data['group'],
    #         'isOnline': context.user_data['isOnline']
    #     }
    # )
    # schedule.save()
    context.user_data.clear()
    update.message.reply_text(text=successful_editing, reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def change_teacher(update: Update, context: CallbackContext):
    context.user_data["teacher"] = update.message.text
    Schedule.update_schedule(user_data=context.user_data)
    # schedule, created = Schedule.objects.update_or_create(
    #     day=context.user_data["day"],
    #     time=context.user_data["time"],
    #     defaults={
    #         'lesson': context.user_data["lesson"],
    #         'teacher': update.message.text,
    #         'group': context.user_data['group'],
    #         'isOnline': context.user_data['isOnline']
    #     }
    # )
    # schedule.save()
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

