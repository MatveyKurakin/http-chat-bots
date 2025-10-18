from bot.dispatcher import Dispatcher
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.message_text_echo import MessageTextEcho
from bot.handlers.message_photo_echo import MessagePhotoEcho
from bot.long_polling import start_long_polling


def main() -> None:
    try:
        dispatcher = Dispatcher()
        dispatcher.add_handler(DatabaseLogger())
        dispatcher.add_handler(MessageTextEcho())
        dispatcher.add_handler(MessagePhotoEcho())
        start_long_polling(dispatcher)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
