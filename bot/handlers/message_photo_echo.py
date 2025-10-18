import json
import bot.telegram_client

from bot.handler import Handler


class MessagePhotoEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        return "message" in update and "photo" in update["message"]

    def handle(self, update: dict) -> bool:
        photo = max(update["message"]["photo"], key=lambda x: x["file_size"])["file_id"]
        if "caption" in update["message"]:
            bot.telegram_client.send_photo(
                chat_id=update["message"]["chat"]["id"],
                photo=photo,
                caption=update["message"]["caption"],
            )
        else:
            bot.telegram_client.send_photo(
                chat_id=update["message"]["chat"]["id"],
                photo=photo,
            )
        return False
