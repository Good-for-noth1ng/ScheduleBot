from telegram import KeyboardButton, ReplyKeyboardMarkup
from tgbot.handlers.internal.static_text import (
    ADD_BUTTON, 
    DELETE_BUTTON, 
    CANCEL_BUTTON, 
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

def make_keyboard_to_choose_by_name(buttons)->ReplyKeyboardMarkup:
    menu = build_menu(buttons=buttons, n_cols=2, header_buttons=CANCEL_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True,one_time_keyboard=True)
    
def make_keyboard_add_or_delete()->ReplyKeyboardMarkup:
    buttons = []
    buttons.append(ADD_BUTTON)
    buttons.append(DELETE_BUTTON)
    menu = build_menu(buttons=buttons, n_cols=2)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True, one_time_keyboard=True)

def make_keyboard_to_choose(link_list_lenght)->ReplyKeyboardMarkup:
    buttons = []
    for n in range(0, link_list_lenght):
        buttons.append(str(n+1))
    menu = build_menu(buttons=buttons, n_cols=4, header_buttons=CANCEL_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, resize_keyboard=True,one_time_keyboard=True)

def make_keyboard_to_stop_receiving_files()->ReplyKeyboardMarkup:
    buttons = []
    buttons.append([KeyboardButton(NO_MORE_FILES_BUTTON)])
    buttons.append([KeyboardButton(MORE_FILES_BUTTON)])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True, one_time_keyboard=True)