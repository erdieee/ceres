import logging
from typing import Any, Dict

from telegram import ParseMode, Update
from telegram.error import NetworkError, TelegramError
from telegram.ext import CallbackContext, CommandHandler, Updater


logger = logging.getLogger(__name__)


class Telegram:
    """
    This class handles all telegram communication
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """
        Init the Telegram call
        :param config: Configuration object as dictionary
        :return: None
        """
        self._config = config
        self.token = self._config["telegram"]["token"]
        self.chat_id = self._config["telegram"]["chat_id"]
        self._updater = Updater(token=self.token, use_context=True)
        self._init()

    def _init(self) -> None:
        """
        Define all commands the bot can use
        :return: None
        """
        handles = [
            CommandHandler("start", self._start),
            CommandHandler("help", self._help),
            CommandHandler("version", self._version),
        ]

        for handle in handles:
            self._updater.dispatcher.add_handler(handle)

        self._updater.start_polling()

        logger.info(
            "telegram is listening for following commands: %s",
            [h.command for h in handles],
        )

    def _start(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /start.
        Sends start up message
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        self._send_message("Started bot")

    def _help(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /help.
        Send helper message
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        help_msg = (
            "*Bot usage:* \n"
            "*/start:* `Starts the bot`\n"
            "*/version:* `Show version of the bot`\n"
            "*/help:* `Show this help message`\n"
        )
        self._send_message(help_msg, parse_mode=ParseMode.MARKDOWN)

    def _version(self, update: Update, context: CallbackContext) -> None:
        """
        Handler for /version.
        Send current bot version
        :param bot: telegram bot
        :param update: message update
        :return: None
        """
        self._send_message(f"*Ceres version:* {0.1}")

    def send_message(self,msg) -> None:
        
        self._send_message(msg) 

    def _send_message(self, message: str, parse_mode: str = ParseMode.MARKDOWN) -> None:
        """
        Send given message
        :param message: message
        :param parse_mode: telegram parse mode
        :return: None
        """
        try:
            try:
                self._updater.bot.send_message(
                    chat_id=self.chat_id, text=message, parse_mode=parse_mode
                )
            except NetworkError as network_err:
                # Sometimes the telegram server resets the current connection,
                # if this is the case we send the message again.
                logger.warning(
                    f"TelegramError: {network_err.message}! Trying one more time."
                )
                self._updater.bot.send_message(
                    chat_id=self.chat_id, text=message, parse_mode=parse_mode
                )
        except TelegramError as telegram_err:
            logger.warning(
                f"TelegramError: {telegram_err.message}! Giving up on that message."
            )
