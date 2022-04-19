from telegram import KeyboardButton, ReplyKeyboardMarkup

from tgbot.handlers.links.static_text import DELETE_LINK_BUTTON, ADD_BUTTON, CANCEL_DELETE_LINK_BUTTON


def build_menu(buttons, n_cols, header_buttons=None, bottom_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if bottom_buttons:
        menu.append([bottom_buttons])
    return menu

def make_keyboard_add_or_delete_link()->ReplyKeyboardMarkup:
    buttons = []
    buttons.append([KeyboardButton(ADD_BUTTON)])
    buttons.append([KeyboardButton(DELETE_LINK_BUTTON)])
    return ReplyKeyboardMarkup(keyboard=buttons, one_time_keyboard=True)

def make_keyboard_to_delete(link_list_lenght)->ReplyKeyboardMarkup:
    buttons = []
    for n in range(0, link_list_lenght):
        buttons.append(str(n+1))
    menu = build_menu(buttons=buttons, n_cols=4, header_buttons=CANCEL_DELETE_LINK_BUTTON)
    return ReplyKeyboardMarkup(keyboard=menu, one_time_keyboard=True)