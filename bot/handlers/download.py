import json
import bot.telegram_client
import bot.database_client

from bot.handlers.handler import HandlerStatus, Handler


class Download(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_DOWNLOAD" and state != "WAIT_FOR_PARAMS":
            return False

        callback_data = update["callback_query"]["data"]
        return "download" in callback_data

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        try:
            bot.telegram_client.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            )
        except:
            return HandlerStatus.STOP

        photo = max(
            update["callback_query"]["message"]["photo"], key=lambda x: x["file_size"]
        )
        file_id = photo["file_id"]
        file_name = bot.telegram_client.get_file(file_id=file_id)["file_path"]
        data = bot.telegram_client.file_download(file_name)

        bot.telegram_client.make_file_request(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            file_name=file_name,
            file_data=data,
            file_type="document",
            caption="Your filtered photo in document",
        )

        return HandlerStatus.STOP
