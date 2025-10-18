import json
import bot.telegram_client

from bot.handler import Handler


class MessagePhotoEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        return "message" in update and "photo" in update["message"]

    def handle(self, update: dict) -> bool:
        photo = max(update["message"]["photo"], key=lambda x: x["file_size"])
        file_id = photo["file_id"]
        bot.telegram_client.send_photo(
            chat_id=update["message"]["chat"]["id"],
            photo=file_id,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {"text": "Grey", "callback_data": "grey"},
                            {"text": "Blur", "callback_data": "blur"},
                            {"text": "Sepia", "callback_data": "sepia"},
                        ],
                    ],
                    "resize_keyboard": True,
                },
            ),
        )
        return False
