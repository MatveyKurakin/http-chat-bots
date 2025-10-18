import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()


def make_request(method: str, **params) -> dict:
    json_data = json.dumps(params).encode("utf-8")
    request = urllib.request.Request(
        method="POST",
        url=f"{os.getenv('TELEGRAM_BASE_URI')}/{method}",
        data=json_data,
        headers={"Content-Type": "application/json"},
    )

    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        response_json = json.loads(response_body)
        assert response_json["ok"] == True
        return response_json["result"]


def make_photo_request(
    chat_id: str, file_name: str, file_data: bytes, **params
) -> dict:
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

    body_parts = []

    body_parts.append(f"--{boundary}")
    body_parts.append('Content-Disposition: form-data; name="chat_id"')
    body_parts.append("")
    body_parts.append(str(chat_id))

    for key, value in params.items():
        if value is not None:
            body_parts.append(f"--{boundary}")
            body_parts.append(f'Content-Disposition: form-data; name="{key}"')
            body_parts.append("")
            body_parts.append(str(value))

    body_parts.append(f"--{boundary}")
    body_parts.append(
        f'Content-Disposition: form-data; name="photo"; filename="{file_name}"'
    )
    body_parts.append("Content-Type: image/jpeg")
    body_parts.append("")
    body_parts.append("")

    body_parts.append(f"--{boundary}--")
    body_parts.append("")

    body_text = "\r\n".join(body_parts)
    body_bytes = body_text.encode("utf-8")

    placeholder_pos = body_bytes.find(b"\r\n\r\n", body_bytes.find(b"image/jpeg"))
    if placeholder_pos != -1:
        placeholder_pos += 4
        final_body = (
            body_bytes[:placeholder_pos] + file_data + body_bytes[placeholder_pos:]
        )
    else:
        final_body = body_bytes

    request = urllib.request.Request(
        method="POST",
        url=f"{os.getenv('TELEGRAM_BASE_URI')}/sendPhoto",
        data=final_body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(final_body)),
        },
    )

    with urllib.request.urlopen(request) as response:
        response_body = response.read().decode("utf-8")
        response_json = json.loads(response_body)
        assert response_json["ok"] == True
        return response_json["result"]


def file_download(file_path: str) -> bytes:
    request = urllib.request.Request(
        method="GET",
        url=f"{os.getenv('TELEGRAM_FILE_URI')}/{file_path}",
    )
    with urllib.request.urlopen(request) as response:
        return response.read()


def get_updates(**params) -> dict:
    return make_request("getUpdates", **params)


def send_message(chat_id: int, text: str, **params) -> dict:
    return make_request("sendMessage", chat_id=chat_id, text=text, **params)


def send_photo(chat_id: int, photo: str, **params) -> dict:
    return make_request("sendPhoto", chat_id=chat_id, photo=photo, **params)


def answer_callback_query(callback_query_id: str) -> dict:
    return make_request("answerCallbackQuery", callback_query_id=callback_query_id)


def get_file(file_id: str) -> dict:
    return make_request("getFile", file_id=file_id)


def get_me() -> dict:
    return make_request("getMme")
