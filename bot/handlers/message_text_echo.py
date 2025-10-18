import bot.telegram_client

from bot.handler import Handler


class MessageTextEcho(Handler):
    def can_handle(self, update: dict) -> bool:
        return "message" in update and "text" in update["message"]

    def handle(self, update: dict) -> bool:
        bot.telegram_client.send_message(
            chat_id=update["message"]["chat"]["id"],
            text=update["message"]["text"],
        )
        return False
