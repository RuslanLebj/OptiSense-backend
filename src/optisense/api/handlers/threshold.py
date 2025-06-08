import logging

from ..models import Record
from ..telegram.adapter import TelegramAdapter

logger = logging.getLogger(__name__)


class ThresholdHandler:
    """
    Хэндлер для отправки уведомлений при превышении порогового значения
    """

    INDICATORS_NAMES_MAP = {
        "queue_length": "длина очереди",
        "service_duration": "время обслуживания",
    }

    def __init__(self, telegram_adapter: TelegramAdapter = None):
        self.telegram = telegram_adapter

    def handle(self, record: Record) -> None:
        """
        Проверяем record.indicators_value против
        camera.indicators_threshold и indicators_status.
        Если есть срабатывания — шлём сообщение в Telegram.
        """
        camera = record.camera
        status_cfg = camera.indicators_status or {}
        thresh_cfg = camera.indicators_threshold or {}
        values = record.indicators_value or {}

        if isinstance(status_cfg, dict):
            keys = [k for k, v in status_cfg.items() if v]
        else:
            keys = list(status_cfg)

        alerts = []
        for key in keys:
            if key not in thresh_cfg or key not in values:
                continue
            try:
                curr = values[key]
                thresh = thresh_cfg[key]
            except (TypeError, ValueError):
                continue
            if curr >= thresh:
                alerts.append((key, curr, thresh))

        if not alerts:
            return


        date_str = record.record_time.strftime("%d-%m-%Y")
        time_str = record.record_time.strftime("%H:%M:%S")

        lines = [
            "🚨 *Пороговые значения превышены!* 🚨",
            f"📍 *Адрес*: {camera.outlet.address}",
            f"🎥 *Камера*: {camera.name}",
            f"🗓️ *Дата*: {date_str}",
            f"⏰ *Время*: {time_str}",
            "",
            "📊 *Показатели*, вышедшие за порог:",
        ]
        for key, curr, thresh in alerts:
            name = self.INDICATORS_NAMES_MAP.get(key, key)
            lines.append(f"• *{name}*: {curr} (пороговое: {thresh})")

        text = "\n".join(lines)

        self.telegram.send_message(text)
