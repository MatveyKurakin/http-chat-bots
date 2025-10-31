import json
import bot.telegram_client
import bot.database_client
import bot.image_filters

from bot.handlers.handler import HandlerStatus, Handler
from bot.filter_config import filter_config, filter_functions


class Params(Handler):
    def can_handle(self, update: dict, state: str, order_json: dict) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_PARAMS":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("params_")

    def handle(self, update: dict, state: str, order_json: dict) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        if "download" in callback_data:
            return HandlerStatus.CONTINUE

        try:
            bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
            bot.telegram_client.delete_message(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            )
        except:
            return HandlerStatus.STOP

        params_name = (
            callback_data.replace("params_", "").replace("_up", "").replace("_down", "")
        )

        filter_name = order_json["filter_name"]
        params = filter_config.get_filter(filter_name)["parameters"]
        for param in params:
            if param["name"] == params_name:
                params_min = param["min"]
                params_max = param["max"]

        if (
            "up" in callback_data
            and order_json["filter_params"][params_name] + 20 <= params_max
        ):
            order_json["filter_params"][params_name] += 20
        elif (
            "down" in callback_data
            and order_json["filter_params"][params_name] - 20 >= params_min
        ):
            order_json["filter_params"][params_name] -= 20

        text = ""
        inline_keyboard = []

        file_id = order_json.get("file_id", "")
        file_name = bot.telegram_client.get_file(file_id=file_id)["file_path"]
        data = bot.telegram_client.file_download(file_name)
        img = bot.image_filters.data_to_img(data)

        text += "Change the settings and download.\n"
        filter_params = {}
        for param in params:
            text += f"{param["sign"]} {param["show_name"]}: {order_json["filter_params"][param["name"]]}% [{param["min"]} - {param["max"]}]\n"
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
            filter_params[param["name"]] = order_json["filter_params"][param["name"]]
        img = filter_functions[filter_name](img, **filter_params)
        bot.database_client.update_user_order_json(telegram_id, order_json)

        inline_keyboard.append(
            [
                {"text": "Download", "callback_data": "params_download"},
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
