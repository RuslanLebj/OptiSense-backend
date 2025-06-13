import logging
import httpx

logger = logging.getLogger(__name__)


class TelegramAdapter:
    """
    Адаптер для отправки сообщений в Telegram через Bot API.
    """

    def __init__(self, token: str = None, chat_id: str = None, timeout: int = 2.0):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.timeout = timeout

    def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
    ) -> bool:
        """
        Отправляет асинхронное сообщение в Telegram.

        Args:
            text (str): Текст сообщения.
            parse_mode (str): Тип разметки.

        Returns:
            bool: True, если успешно, False — при ошибке.
        """
        if not self.token or not self.chat_id:
            logger.error("Не задан TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
            return False

        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, data=payload)
                resp.raise_for_status()
            return True
        except Exception as e:
            logger.exception(f"Ошибка при отправке Telegram-сообщения (sync): {e}")
            return False

    def send_photo(
        self,
        photo_url: str,
        caption: str = None,
        parse_mode: str = "Markdown",
        disable_web_page_preview: bool = False,
    ) -> bool:
        """
        Отправляет фото в Telegram.

        Args:
            photo_url (str): URL изображения.
            caption (str): Подпись к изображению.
            parse_mode (str): Тип разметки подписи.
            disable_web_page_preview (bool): Отключить превью для ссылок в подписи.

        Returns:
            bool: True, если отправлено успешно, False — при ошибке.
        """
        if not self.token or not self.chat_id:
            logger.error("Не задан TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID")
            return False

        url = f"{self.base_url}/sendPhoto"
        payload = {
            "chat_id": self.chat_id,
            "photo": photo_url,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if caption:
            payload["caption"] = caption

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, data=payload)
                resp.raise_for_status()
            return True
        except Exception as e:
            logger.exception(f"Ошибка при отправке Telegram-изображения (sync): {e}")
            return False