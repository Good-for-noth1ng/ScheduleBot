from telegram import KeyboardButton, ReplyKeyboardMarkup

from tgbot.handlers.schedule.static_text import (
    DAYS_TO_CHOOSE, 
    DAYS_TO_EDIT, 
    TIME_TO_EDIT,
    CANCEL_BUTTON,
    BACK_BUTTON,
    SET_BUTTON,
    DELETE_BUTTON,
    SKIP_BUTTON,
    SEND_PHOTO_BUTTON,
    SEND_PHOTO_FOR_EDITING_BUTTON,
    DELETE_PHOTO_BUTTON,
    NO_MORE_FILES_BUTTON,
    MORE_FILES_BUTTON
)

def build_menu(buttons, n_cols, header_buttons=None, bottom_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if bottom_buttons:
        menu.append([bottom_buttons])
    return menu

def make_keyboard_to_stop_receiving_files()->ReplyKeyboardMarkup:
    buttons = []
    buttons.append([KeyboardButton(NO_MORE_FILES_BUTTON)])
    buttons.append([KeyboardButton(MORE_FILES_BUTTON)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_for_choosing_day() -> ReplyKeyboardMarkup:
    buttons = []
    for day in DAYS_TO_CHOOSE:
        buttons.append(day)
    menu = build_menu(buttons=buttons, n_cols=3, bottom_buttons=SEND_PHOTO_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_for_deleting_file(file_num) ->  ReplyKeyboardMarkup:
    buttons = []
    for i in range(file_num):
        buttons.append(i + 1)
    menu = build_menu(buttons=buttons, n_cols=4, header_buttons=CANCEL_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_for_editing_day_schedule() -> ReplyKeyboardMarkup:
    buttons = []
    for day in DAYS_TO_EDIT:
        buttons.append(day)
    menu = build_menu(buttons=buttons, n_cols=3, bottom_buttons=SEND_PHOTO_FOR_EDITING_BUTTON)
    menu.append([DELETE_PHOTO_BUTTON])
    menu.append([CANCEL_BUTTON])
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_for_editing_time_schedule() -> ReplyKeyboardMarkup:
    buttons = []
    for time in TIME_TO_EDIT:
        buttons.append(time)
    menu = build_menu(buttons=buttons, n_cols=4, header_buttons=CANCEL_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_set_or_delete() -> ReplyKeyboardMarkup:
    buttons = []
    buttons.append([KeyboardButton(SET_BUTTON)])
    buttons.append([KeyboardButton(DELETE_BUTTON)])
    buttons.append([KeyboardButton(CANCEL_BUTTON)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_for_skip_and_cancel() -> ReplyKeyboardMarkup:
    buttons = []
    row = []
    row.append(KeyboardButton(SKIP_BUTTON))
    row.append(KeyboardButton(CANCEL_BUTTON))
    buttons.append(row)
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)