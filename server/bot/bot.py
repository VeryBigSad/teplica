from threading import Thread

from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackQueryHandler, ConversationHandler

from bot.handlers import change_servo_callback, change_mode_callback, start, help_command, update_data_callback, ventil_callback, ventil_text, picture_handler


class TeplicaBot:
    def __init__(self, token) -> None:
        self.updater = Updater(token)

        self.dispatcher = self.updater.dispatcher

        self.dispatcher.add_handler(CommandHandler("start", start))
        self.dispatcher.add_handler(CommandHandler("help", help_command))
        self.dispatcher.add_handler(CallbackQueryHandler(update_data_callback, pattern="update"))
        self.dispatcher.add_handler(CallbackQueryHandler(change_mode_callback, pattern="change_mode"))
        self.dispatcher.add_handler(CallbackQueryHandler(change_servo_callback, pattern="change_servo"))
        self.dispatcher.add_handler(CommandHandler("pic", picture_handler))
        self.dispatcher.add_handler(MessageHandler(Filters.text, ventil_text))
        self.dispatcher.add_handler(CallbackQueryHandler(ventil_callback, pattern="ventil"))

    def start_polling(self) -> None:
        """Starts polling the telegram bot"""
        self.updater.start_polling()
        self.updater.idle()
    
    def start_polling_in_a_thread(self) -> None:
        """Starts polling the telegram bot in a thread"""
        # create a new thread and call self.start_polling()
        thread = Thread(target=self.start_polling)
        thread.start()




