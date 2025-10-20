import json
import cv2
import numpy as np
import bot.telegram_client

from bot.handler import Handler


class CallbackPhoto(Handler):
    def can_handle(self, update: dict) -> bool:
        return "callback_query" in update and update["callback_query"]["data"] in [
            "grey",
            "blur",
            "sepia",
        ]

    def handle(self, update: dict) -> bool:
        bot.telegram_client.answer_callback_query(update["callback_query"]["id"])
        bot.telegram_client.delete_message(
            update["callback_query"]["message"]["chat"]["id"],
            update["callback_query"]["message"]["message_id"],
        )

        filter_type = update["callback_query"]["data"]
        photo = max(
            update["callback_query"]["message"]["photo"], key=lambda x: x["file_size"]
        )
        file_id = photo["file_id"]
        file_path = bot.telegram_client.get_file(file_id=file_id)["file_path"]
        data = bot.telegram_client.file_download(file_path)
        filtered_data = apply_image_filter(data, filter_type)
        bot.telegram_client.make_photo_request(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            file_name=f"{filter_type}_{file_path}",
            file_data=filtered_data,
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


def apply_image_filter(data: bytes, filter_type: str) -> bytes:

    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    assert not image is None

    if filter_type == "grey":
        filtered_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        filtered_image = cv2.cvtColor(filtered_image, cv2.COLOR_GRAY2BGR)

    elif filter_type == "blur":
        filtered_image = cv2.GaussianBlur(image, (15, 15), 0)

    elif filter_type == "sepia":
        kernel = np.array(
            [[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]]
        )
        filtered_image = cv2.transform(image, kernel)
        filtered_image = np.clip(filtered_image, 0, 255)

    else:
        filtered_image = image

    success, encoded_image = cv2.imencode(
        ".jpg", filtered_image, [cv2.IMWRITE_JPEG_QUALITY, 85]
    )
    assert success

    return encoded_image.tobytes()
