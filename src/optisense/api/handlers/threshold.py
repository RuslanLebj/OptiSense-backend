import logging
import time
from collections import defaultdict

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
    COOLDOWN_SECONDS = 300

    def __init__(
        self, telegram_adapter: TelegramAdapter = None,
    ):
        self.telegram = telegram_adapter or TelegramAdapter()
        self.last_sent_per_camera = defaultdict(lambda: 0)

    def handle(self, record: Record) -> None:
        camera = record.camera
        camera_id = camera.id
        now = time.time()

        last_sent = self.last_sent_per_camera[camera_id]
        if now - last_sent < self.COOLDOWN_SECONDS:
            logger.info(
                f"[Throttle] Пропущено уведомление для камеры {camera_id}: cooldown ещё не прошёл ({int(now - last_sent)} сек)"
            )
            return

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

        success = self.telegram.send_message(text)
        if success:
            self.last_sent_per_camera[camera_id] = now
            logger.info(f"[Throttle] Уведомление отправлено для камеры {camera_id}")
        else:
            logger.error(
                f"[Throttle] Не удалось отправить уведомление для камеры {camera_id}"
            )
