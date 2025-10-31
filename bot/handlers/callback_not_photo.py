import json
import bot.telegram_client
import bot.database_client

from bot.handlers.handler import HandlerStatus, Handler
from bot.filter_config import filter_config


class CallbackNotPhoto(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return True

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:        
        try:
            telegram_id = update["message"]["from"]["id"]

            bot.database_client.clear_user_state_and_order(telegram_id)

            bot.telegram_client.send_message(
                chat_id=update["message"]["chat"]["id"],
                text="Your message is not supported!\nSend the image via Paperclip -> Photo",
                reply_markup=json.dumps({"remove_keyboard": True}),
            )
        except:
            pass

        return HandlerStatus.STOP
