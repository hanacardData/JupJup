from enum import Enum


class BotStatus(str, Enum):
    NO_COMMAND = "no_command"
    COMMAND_PROCESSED = "command_processed"
    ERROR = "error"
    IGNORED = "ignored"
    PRIVATE_REPLY_SENT = "private_reply_sent"
    MISSING_ARGUMENT = "missing_argument"
    GREETED = "greeted"
