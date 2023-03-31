import random
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext
from telegram.error import BadRequest

from constants import MODE_AUTOMATIC, MODE_MANUAL
from manual_settings import ManualSettings

from server import Server


def get_keyboard_using_instance(instance):
    if instance.mode == MODE_MANUAL:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Обновить 🔄", callback_data="update")],
            [
                InlineKeyboardButton(
                    "Автоматический режим 🤖",
                    callback_data="change_mode"
                )
            ],
            [
                InlineKeyboardButton(
                    "Закрыть форточку ❌" if instance.settings.is_servo_on else "Открыть форточку ✅", callback_data="change_servo"
                ),
                InlineKeyboardButton("Вентилятор 🍃", callback_data="ventil")
            ]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Обновить 🔄", callback_data="update")],
            [InlineKeyboardButton(
                "Ручной режим 🕹️", callback_data="change_mode")]
        ])


def format_text_using_instance(instance):
    servo = instance.is_servo_on
    mode_text = "Ручной" if instance.mode == MODE_MANUAL else "Умный"
    if instance.temperature_outside is None:
        temp_outside_text = 'Еще не измерена'
    else:
        temp_outside_text = f'{instance.get_outside_temp()}°C'
    if instance.temperature_inside is None:
        temp_inside_text = 'Еще не измерена'
    else:
        temp_inside_text = f"{instance.get_inside_temp()}°C"

    if instance.ventil_power is None:
        ventilator_text = "Еще не измерен..."
    else:
        ventilator_text = f'{instance.ventil_power}%'
        if instance.settings.ventil_power != instance.ventil_power:
            ventilator_text += " (вот-вот поменяется!)"

    if servo:
        servo_text = 'Открыта'
        if instance.settings and not instance.settings.is_servo_on:
            servo_text = "Вот-вот закроется!"
    else:
        servo_text = "Закрыта"
        if instance.settings and instance.settings.is_servo_on:
            servo_text = "Вот-вот откроется!"
    text = f"""🌱<b>Теплица Спартана</b>
<i>Режим</i>: {mode_text}

🌡️ <i>Температура снаружи</i>: {temp_outside_text}
🌡️ <i>Температура внутри</i>: {temp_inside_text}
💨 <i>Вентилятор</i>: {ventilator_text}
🪟 <i>Форточка</i>: {servo_text}
"""
    return text


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    # send data about teplica: temperature, is ventilator on, is servo on
    instance = Server.get_instance()
    text = format_text_using_instance(instance)
    keyboard = get_keyboard_using_instance(instance)

    update.message.reply_text(
        text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    text = """Этот бот позволяет вам управлять теплицей человека, по имени <b>Спартак</b> 😊

Напиши /start, чтобы увидеть текущие данные теплицы.
<i>Нажимай на кнопки, чтобы управлять ей.</i>
"""
    update.message.reply_text(text, parse_mode=ParseMode.HTML)


def change_mode_callback(update: Update, context: CallbackContext) -> None:
    instance = Server.get_instance()
    if instance.get_mode() == MODE_MANUAL:
        instance.set_mode(MODE_AUTOMATIC)
    else:
        instance.set_mode(MODE_MANUAL)
        instance.set_settings()
        instance.settings.ventil_power = 100
    update.callback_query.answer()
    text = format_text_using_instance(instance)
    keyboard = get_keyboard_using_instance(instance)
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


def ventil_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    query.message.reply_html(
        "<b>Окей!</b>\nВведи силу (0-100)🔌, с которым ты хочешь крутить вентилятор."
    )


def ventil_text(update: Update, context: CallbackContext) -> None:
    # let's set 10 buttons here or something idk yet
    text = update.message.text
    if not text.isdigit():
        update.message.reply_html("Это не число!")
        return
    power = int(text)
    if power < 0 or power > 100:
        update.message.reply_html("Число должно быть от 0 до 100!")
        return
    instance = Server.get_instance()
    instance.settings.ventil_power = power
    text = format_text_using_instance(instance)
    keyboard = get_keyboard_using_instance(instance)
    update.message.reply_html(
        text=text,
        reply_markup=keyboard
    )


def change_servo_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    instance = Server.get_instance()
    instance.settings.is_servo_on = not instance.settings.is_servo_on
    text = format_text_using_instance(instance)
    keyboard = get_keyboard_using_instance(instance)
    query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )


def update_data_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    instance = Server.get_instance()
    text = format_text_using_instance(instance)
    keyboard = get_keyboard_using_instance(instance)
    try:
        query.edit_message_text(
            text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML
        )
    except BadRequest:
        pass


def picture_handler(update: Update, context: CallbackContext) -> None:
    instance = Server.get_instance()
    pic_name = str(random.randint(10000, 99999))
    instance.create_picture(pic_name)
    update.message.reply_photo(
        photo=open(f'{pic_name}.png', 'rb')
    )

    # delete picture
    os.remove(f'{pic_name}.png')

    
    
