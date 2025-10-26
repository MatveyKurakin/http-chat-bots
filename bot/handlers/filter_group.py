import json
import bot.telegram_client
import bot.database_client

from bot.handlers.handler import HandlerStatus, Handler
from bot.filter_config import filter_config


class FilterGroup(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_FILTER_GROUP":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("filter_group_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        filter_group_name = callback_data.replace("filter_group_", "")
        order_json["filter_group_name"] = filter_group_name
        bot.database_client.update_user_order_json(telegram_id, order_json)

        bot.database_client.update_user_state(telegram_id, f"WAIT_FOR_FILTER")

        try:
            bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
            bot.telegram_client.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            )
        except:
            return HandlerStatus.STOP

        filters = filter_config.get_group_filters(filter_group_name)

        inline_keyboard = []
        line = []
        for filter in filters:
            line.append(
                {
                    "text": filter["show_name"],
                    "callback_data": f"filter_{filter["name"]}",
                }
            )
            if len(line) == 3:
                inline_keyboard.append(line)
                line = []
        inline_keyboard.append(line)

        bot.telegram_client.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Please choose filter:",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": inline_keyboard,
                },
            ),
        )

        return HandlerStatus.STOP
