import time

import bot.database_client
import bot.telegram_client


def main() -> None:
    next_update_offset = 0
    try:
        while True:
            updates = bot.telegram_client.get_updates(next_update_offset)
            bot.database_client.persist_updates(updates)
            for update in updates:
                if "text" not in update["message"]:
                    bot.telegram_client.send_message(
                        chat_id=update["message"]["chat"]["id"],
                        text="I don't know how to reply to messages with files.",
                    )
                else:
                    bot.telegram_client.send_message(
                        chat_id=update["message"]["chat"]["id"],
                        text=update["message"]["text"],
                    )
                print(".", end="", flush=True)
                next_update_offset = max(next_update_offset, update["update_id"] + 1)
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nBye!")


if __name__ == "__main__":
    main()
