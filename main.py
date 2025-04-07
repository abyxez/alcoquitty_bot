import os
from dataclasses import dataclass

import telebot
from dotenv import load_dotenv
from telebot import types

from alco_logic import drink_timer, next_drink_day
from database import get_initialization, get_user, update_user
from services import get_right_ending

load_dotenv()

bot = telebot.TeleBot(os.getenv("TELEGRAM_KEY"))


HELP_TEXT = "/help \n/drank \n/rules \n/info"
RULES = (
    "1) Стартовые показатели: 1 день штрафа, +1 день за каждый приём алкоголя."
    "\n2) Суть эксперимента в том, чтобы накопить наименьший"
    " общий штраф за год, потому что новый год - новая жизнь, и штраф обнуляется."
    "\n3) Если ты просто ожидаешь возможность выпить, "
    "то ты пьешь 1+2+3+4..., где каждая цифра между плюсами означает "
    "твой обыденный перерыв между употреблениями алкоголя."
    "\n4) Если нарушаешь график, то появляются дополнительные штрафы. "
    "Например, текущий штраф 5 дней, но уже через 2 полных дня был алкоголь. Штраф "
    "становится 5+2( с округлением 3-его неполного дня в пользу участника. )"
    "При этом будущие штрафы растут как обычно, но пауза в этот раз будет дольше."
    "\n5) Бонусы. Если ты выдержал при штрафе в 5 дней, например, 10 и больше, "
    "то ты получаешь бонусную возможность, которая игнорирует текущий штраф. "
    "Ты всё так же трезв для бота, но только следующий "
    "такой бонус доступен уже через 20 дней ( 5, 10, 20, 40 и тд), а раннее выпивание "
    "даёт обычный штраф."
    "\n6) Период выпивания ( 1 раз) для бота 24 часа."
)


@dataclass
class Message:
    text: str

    def __init__(self, text):
        self.text = text


@bot.message_handler(
    commands=[
        "start",
    ]
)
def message_handler_start(message):
    button_drank = types.InlineKeyboardButton("🥴ВЫПИЛ!", callback_data="ВЫПИЛ!")
    button_rules = types.InlineKeyboardButton("🤖Правила", callback_data="Правила")
    button_help = types.InlineKeyboardButton("🆘Помощь", callback_data="Помощь")
    button_info = types.InlineKeyboardButton("🟢Обо мне", callback_data="Инфо")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_info)
    keyboard.add(button_drank)
    keyboard.add(button_rules)
    keyboard.add(button_help)

    get_initialization(message.from_user.username, message.from_user.first_name)
    bot.send_message(
        message.chat.id,
        f"{message.from_user.first_name}, "
        "тебя приветствует алкобот! "
        "Со мной ты бросишь пить =)",
        reply_markup=keyboard,
    )


def message_handler_rules_drank_help(message):
    """
    Основной обработчик бота для текстовых команд
    """
    rule_list = ["Правила", "/rules"]
    drank_list = ["ВЫПИЛ!", "/drank"]
    help_list = ["Помощь", "/help"]
    info_list = ["Инфо", "/info"]

    if message.data in info_list:
        user = get_user(message.from_user.username)
        current_penalty = user[3]
        last_drank = user[5]
        next_day = next_drink_day(
            last_drank=last_drank, current_penalty=current_penalty - 1
        )
        clear_time = get_right_ending(days=current_penalty - 1)
        wait_time = get_right_ending(days=current_penalty)
        time_check = drink_timer(last_drank)

        bot.send_message(
            message.from_user.id,
            f'\nТекущий штраф {clear_time or "отсутствует"}.'
            f'\nВ следующий раз можно выпить {next_day or "сейчас"}.'
            f"\nСледующий штраф {wait_time}."
            f'\nОстаток таймера {time_check[0] or "отсутствует"}.',
        )

    if message.data in rule_list:
        bot.send_message(message.from_user.id, f"Правила работы бота: \n{RULES}")

    elif message.data in drank_list:
        user = get_user(message.from_user.username)
        last_drank = user[5]  # last_drank
        time_check = drink_timer(last_drank)

        if time_check[1]:  # True / False
            update_user(message.from_user.username)
            user = get_user(message.from_user.username)
            last_drank = user[5]  # last_drank
            current_penalty = user[3]  # current_penalty

            time_check = drink_timer(last_drank)
            next_day = next_drink_day(
                last_drank=last_drank, current_penalty=current_penalty - 1
            )
            clear_time = get_right_ending(days=(current_penalty - 1))
            wait_time = get_right_ending(days=current_penalty)

            bot.send_message(
                message.from_user.id,
                "Неплохо, тогда развлекайся, " "а я поставил тебе таймер на 24 часа!",
            )

            bot.send_message(
                message.from_user.id,
                f"\nНужно подождать {clear_time}."
                f"\nМожно выпить {next_day}."
                f"\nСледующий штраф {wait_time}."
                f"\nОстаток таймера {time_check[0]}.",
            )
        else:
            bot.send_message(
                message.from_user.id,
                "Таймер уже поставлен!" f"\nОсталось {time_check[0]}.",
            )

    elif message.data in help_list:
        bot.send_message(message.from_user.id, f"Доступные команды: \n" f"{HELP_TEXT}")


@bot.message_handler(commands=["help", "rules", "drank", "info"])
def command_handler(message):
    """
    Дублирует функционал message_handler_rules_drank_help для команд,
    начинающихся с /
    """
    if message.text == "/info":
        user = get_user(message.from_user.username)
        current_penalty = user[3]
        last_drank = user[5]
        next_day = next_drink_day(
            last_drank=last_drank, current_penalty=current_penalty - 1
        )
        clear_time = get_right_ending(days=current_penalty - 1)
        wait_time = get_right_ending(days=current_penalty)
        time_check = drink_timer(last_drank)

        bot.send_message(
            message.from_user.id,
            f'\nТекущий штраф {clear_time or "отсутствует"}.'
            f'\nМожно выпить {next_day or "сейчас"}.'
            f"\nСледующий штраф {wait_time}."
            f'\nОстаток таймера {time_check[0] or "отсутствует"}.',
        )
    elif message.text == "/help":
        bot.send_message(message.chat.id, f"Доступные команды: \n" f"{HELP_TEXT}")
    elif message.text == "/rules":
        bot.send_message(message.chat.id, f"{RULES}")

    elif message.text == "/drank":
        user = get_user(message.from_user.username)
        last_drank = user[5]  # last_drank
        time_check = drink_timer(last_drank)

        if time_check[1]:  # True / False
            update_user(message.from_user.username)
            user = get_user(message.from_user.username)
            last_drank = user[5]  # last_drank
            time_check = drink_timer(last_drank)
            current_penalty = user[3]  # current_penalty
            next_day = next_drink_day(
                last_drank=last_drank, current_penalty=current_penalty - 1
            )
            clear_time = get_right_ending(days=(current_penalty - 1))
            wait_time = get_right_ending(days=current_penalty)

            bot.send_message(
                message.from_user.id,
                "Неплохо, тогда развлекайся, " "а я поставил тебе таймер на 24 часа!",
            )

            bot.send_message(
                message.from_user.id,
                f"\nНужно подождать {clear_time}."
                f"\nМожно выпить {next_day}."
                f"\nСледующий штраф {wait_time}."
                f"\nОстаток таймера: {time_check[0]}.",
            )
        else:
            bot.send_message(
                message.from_user.id,
                "Таймер уже поставлен!" f"\nОсталось {time_check[0]}.",
            )


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    """
    Обрабатывает входящие callback для кнопочных команд
    """
    if call.data == "Инфо":
        message_handler_rules_drank_help(message=call)
    elif call.data == "ВЫПИЛ!":
        message_handler_rules_drank_help(message=call)
    elif call.data == "Помощь":
        bot.send_message(call.message.chat.id, f"Доступные команды: \n" f"{HELP_TEXT}")
    elif call.data == "Правила":
        bot.send_message(call.message.chat.id, f"{RULES}")


bot.polling(non_stop=True)
