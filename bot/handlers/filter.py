import json
import bot.telegram_client
import bot.database_client
import bot.image_filters

from bot.handlers.handler import HandlerStatus, Handler
from bot.filter_config import filter_config, filter_functions


class Filter(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_FILTER":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("filter_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        filter_name = callback_data.replace("filter_", "")
        order_json["filter_name"] = filter_name
        bot.database_client.update_user_order_json(telegram_id, order_json)

        try:
            bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
            bot.telegram_client.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            )
        except:
            return HandlerStatus.STOP

        if filter_config.get_filter(filter_name)["has_parameters"]:
            bot.database_client.update_user_state(telegram_id, "WAIT_FOR_PARAMS")
        else:
            bot.database_client.update_user_state(telegram_id, "WAIT_FOR_DOWNLOAD")

        text = ""
        inline_keyboard = []

        file_id = order_json.get("file_id", "")
        file_name = bot.telegram_client.get_file(file_id=file_id)["file_path"]
        data = bot.telegram_client.file_download(file_name)
        img = bot.image_filters.data_to_img(data)

        if filter_config.get_filter(filter_name)["has_parameters"]:
            text += "Change the settings and download.\n"
            params = filter_config.get_filter(filter_name)["parameters"]
            filter_params = {}
            for param in params:
                text += f"{param["sign"]} {param["show_name"]}: {param["default"]}% [{param["min"]} - {param["max"]}]\n"
                inline_keyboard.append(
                    [
                        {
                            "text": f"{param["sign"]} - {param["step"]} %",
                            "callback_data": f"params_{param["name"]}_down",
                        },
                        {
                            "text": f"{param["sign"]} + {param["step"]} %",
                            "callback_data": f"params_{param["name"]}_up",
                        },
                    ]
                )
                filter_params[param["name"]] = param["default"]
            img = filter_functions[filter_name](img, **filter_params)
            order_json["filter_params"] = filter_params
            bot.database_client.update_user_order_json(telegram_id, order_json)

            inline_keyboard.append(
                [
                    {"text": "Download", "callback_data": "params_download"},
                ]
            )
        else:
            text += "Your filtered photo"
            img = filter_functions[filter_name](img)

            inline_keyboard.append(
                [
                    {"text": "Download", "callback_data": "download"},
                ]
            )

        data = bot.image_filters.img_to_data(img)

        bot.telegram_client.make_file_request(
            chat_id=telegram_id,
            file_name=f"{file_name.split(".")[0]}_{filter_name}.jpg",
            file_data=data,
            file_type="photo",
            caption=text,
            reply_markup=json.dumps(
                {
                    "inline_keyboard": inline_keyboard,
                },
            ),
        )

        return HandlerStatus.STOP
