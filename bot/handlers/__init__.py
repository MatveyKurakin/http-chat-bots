from bot.handlers.handler import Handler
from bot.handlers.database_logger import DatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.callback_photo import CallbackPhoto
from bot.handlers.filter_group import FilterGroup
from bot.handlers.filter import Filter
from bot.handlers.params import Params
from bot.handlers.download import Download


def get_handlers() -> list[Handler]:
    return [
        DatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        CallbackPhoto(),
        FilterGroup(),
        Filter(),
        Params(),
        Download(),
    ]
