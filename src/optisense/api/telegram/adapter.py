import logging
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)

class TelegramAdapter:
    """
    Асинхронный адаптер для отправки сообщений в Telegram через Bot API.
    """
    def __init__(self, token: str = None, chat_id: str = None):
        self.token   = token   or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text: str, parse_mode: str = "Markdown") -> bool:
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
            with httpx.Client(timeout=1.0) as client:
                resp = client.post(url, data=payload)
                resp.raise_for_status()
            return True
        except Exception as e:
            logger.exception(f"Ошибка при отправке Telegram-сообщения (sync): {e}")
            return False
