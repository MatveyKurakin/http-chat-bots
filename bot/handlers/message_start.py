import json
import bot.telegram_client
import bot.database_client

from bot.handlers.handler import HandlerStatus, Handler


class MessageStart(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        bot.database_client.clear_user_state_and_order(telegram_id)

        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Welcome to Image Filters Telegram Bot!",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Send the image you want to apply the filter to.",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        return HandlerStatus.STOP
