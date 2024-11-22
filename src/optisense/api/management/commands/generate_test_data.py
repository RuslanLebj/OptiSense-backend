import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from ...models import Camera, Outlet, Record
from ...schemas import ROIPolygonsPointsSchema, ParameterTypesSchema, ParametersSchema

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
            # Генерация случайных параметров для parameter_types
            parameter_types_data = {
                "queue_length": random.choice([True, False]),
                "service_duration": random.choice([True, False]),
                "has_earrings": random.choice([True, False]),
            }
            parameter_types = ParameterTypesSchema(**parameter_types_data).model_dump()

            # Генерация случайного числа полигонов для roi_polygons_points (от 1 до 3 полигонов)
            polygons = []
            for i in range(random.randint(1, 3)):
                num_points = random.randint(3, 5)  # от 3 до 5 точек на полигон
                points = [{"x": random.randint(0, 1000), "y": random.randint(0, 1000)} for _ in range(num_points)]
                polygons.append({"id": i + 1, "points": points})
            roi_polygons_points = ROIPolygonsPointsSchema(polygons=polygons).model_dump()

            # Создание камеры с parameter_types и roi_polygons_points
            camera = Camera.objects.create(
                outlet=random.choice(outlets),
                name=fake.company(),
                preview=fake.image_url(),
                url_address=fake.url(),
                connection_login=fake.user_name(),
                connection_password=fake.password(),
                is_active=fake.boolean(),
                parameter_types=parameter_types,
                roi_polygons_points=roi_polygons_points,
            )
            cameras.append(camera)
        self.stdout.write(self.style.SUCCESS(f"Created {len(cameras)} cameras."))

        # Generate Record data
        records = []
        for camera in cameras:
            for _ in range(random.randint(100, 2000)):  # случайное число записей для каждой камеры
                parameters_data = {}

                # Если parameter_types указывает на отслеживание, генерируем значения для параметров
                if camera.parameter_types.get("queue_length"):
                    parameters_data["queue_length"] = random.randint(0, 20)  # Длина очереди от 0 до 20

                if camera.parameter_types.get("service_duration"):
                    parameters_data["service_duration"] = random.uniform(30, 600)  # Время обслуживания от 30 до 600 секунд

                if camera.parameter_types.get("has_earrings"):
                    parameters_data["has_earrings"] = random.choice([True, False])  # Случайно True или False

                # Если parameters_data пустой, добавляем один случайный параметр
                if not parameters_data:
                    parameter_to_add = random.choice(["queue_length", "service_duration", "has_earrings"])
                    if parameter_to_add == "queue_length":
                        parameters_data["queue_length"] = random.randint(0, 20)
                    elif parameter_to_add == "service_duration":
                        parameters_data["service_duration"] = random.uniform(30, 600)
                    elif parameter_to_add == "has_earrings":
                        parameters_data["has_earrings"] = random.choice([True, False])

                # Создаем запись с timezone-aware datetime
                record = Record.objects.create(
                    camera=camera,
                    record_time=timezone.make_aware(fake.date_time_this_year(), timezone.get_current_timezone()),
                    record_video=fake.file_path(extension="mp4"),
                    record_frame=fake.file_path(extension="jpg"),
                    parameters=ParametersSchema(**parameters_data).model_dump(),
                )
                records.append(record)
        self.stdout.write(self.style.SUCCESS(f"Created {len(records)} records."))
