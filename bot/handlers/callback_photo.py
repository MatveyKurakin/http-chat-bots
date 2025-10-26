import json
import bot.telegram_client
import bot.database_client

from bot.handlers.handler import HandlerStatus, Handler
from bot.filter_config import filter_config


class CallbackPhoto(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        return "message" in update and "photo" in update["message"]

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        photo = max(update["message"]["photo"], key=lambda x: x["file_size"])
        file_id = photo["file_id"]

        bot.database_client.update_user_order_json(telegram_id, {"file_id": file_id})

        bot.database_client.update_user_state(telegram_id, "WAIT_FOR_FILTER_GROUP")

        inline_keyboard = []
        line = []
        for key, value in filter_config.filter_groups.items():
            line.append({"text": value, "callback_data": f"filter_group_{key}"})
            if len(line) == 3:
                inline_keyboard.append(line)
                line = []
        inline_keyboard.append(line)

        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text="Please choose filters group:",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": inline_keyboard,
                },
            ),
        )

        return HandlerStatus.STOP
