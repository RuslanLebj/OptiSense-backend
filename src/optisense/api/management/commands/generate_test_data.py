import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from ...models import Camera, Outlet, Record
from ...schemas import ROIPolygonsSchema, IndicatorsStatusSchema, IndicatorsSchema

fake = Faker()


class Command(BaseCommand):
    help = "Generate test data for models"

    def handle(self, *args, **kwargs):
        # Generate Outlet data
        outlets = [Outlet.objects.create(address=fake.address()) for _ in range(10)]
        self.stdout.write(self.style.SUCCESS(f"Created {len(outlets)} outlets."))

        # Generate Camera data
        cameras = []
        for _ in range(20):
            # Генерация случайных параметров для indicators_status
            indicators_status_data = {
                "queue_length": random.choice([True, False]),
                "service_duration": random.choice([True, False]),
            }
            indicators_status = IndicatorsStatusSchema(**indicators_status_data).model_dump()

            # Генерация случайного числа полигонов для roi_polygons (от 1 до 3 полигонов)
            polygons = []
            for i in range(random.randint(1, 3)):
                num_points = random.randint(3, 5)  # от 3 до 5 точек на полигон
                points = [{"x": random.randint(0, 1000), "y": random.randint(0, 1000)} for _ in range(num_points)]
                polygons.append({"id": i + 1, "points": points})
            roi_polygons = ROIPolygonsSchema(polygons=polygons).model_dump()


            # Генерация start_time и end_time
            start_time = fake.time()  # Random start time
            end_time = fake.time()  # Random end time
            # Ensure end_time is later than start_time
            if start_time > end_time:
                start_time, end_time = end_time, start_time


            # Генерация indicators_threshold с максимальными значениями
            indicators_threshold = {}
            if indicators_status_data.get("queue_length"):
                indicators_threshold["queue_length"] = random.randint(5, 20)  # max queue length from 5 to 20
            else:
                indicators_threshold["queue_length"] = None

            if indicators_status_data.get("service_duration"):
                indicators_threshold["service_duration"] = random.uniform(120, 600)  # max service duration from 120 to 600 seconds
            else:
                indicators_threshold["service_duration"] = None


            # Создание камеры
            camera = Camera.objects.create(
                outlet=random.choice(outlets),
                name=fake.company(),
                preview=fake.image_url(),
                url_address=fake.url(),
                connection_login=fake.user_name(),
                connection_password=fake.password(),
                is_active=fake.boolean(),
                indicators_status=indicators_status,
                roi_polygons=roi_polygons,
                start_time=start_time,
                end_time=end_time,
                indicators_threshold=indicators_threshold
            )
            cameras.append(camera)
        self.stdout.write(self.style.SUCCESS(f"Created {len(cameras)} cameras."))

        # Generate Record data
        records = []
        for camera in cameras:
            for _ in range(random.randint(100, 2000)):  # случайное число записей для каждой камеры
                indicators_value = {}

                # Если indicators_status указывает на отслеживание, генерируем значения для параметров
                if camera.indicators_status.get("queue_length"):
                    indicators_value["queue_length"] = random.randint(0, 20)  # Длина очереди от 0 до 20

                if camera.indicators_status.get("service_duration"):
                    indicators_value["service_duration"] = random.uniform(30, 600)  # Время обслуживания от 30 до 600 секунд

                # Если indicators_value пустой, добавляем один случайный параметр
                if not indicators_value:
                    indicators_to_add = random.choice(["queue_length", "service_duration"])
                    if indicators_to_add == "queue_length":
                        indicators_value["queue_length"] = random.randint(0, 20)
                    elif indicators_to_add == "service_duration":
                        indicators_value["service_duration"] = random.uniform(30, 600)

                # Создаем запись с timezone-aware datetime
                record = Record.objects.create(
                    camera=camera,
                    record_time=timezone.make_aware(fake.date_time_this_year(), timezone.get_current_timezone()),
                    record_video=fake.file_path(extension="mp4"),
                    record_frame=fake.file_path(extension="jpg"),
                    indicators_value=IndicatorsSchema(**indicators_value).model_dump(),
                )
                records.append(record)
        self.stdout.write(self.style.SUCCESS(f"Created {len(records)} records."))
