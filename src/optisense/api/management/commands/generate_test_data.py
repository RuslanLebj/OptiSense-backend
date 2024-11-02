import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from ...models import Camera, CameraParameter, Outlet, ParameterType, Record

fake = Faker()


class Command(BaseCommand):
    help = "Generate test data for models"

    def handle(self, *args, **kwargs):
        # Generate Outlet data
        outlets = [Outlet.objects.create(address=fake.address()) for _ in range(10)]
        self.stdout.write(self.style.SUCCESS(f"Created {len(outlets)} outlets."))

        # Generate ParameterType data
        parameter_types = [
            ParameterType.objects.create(name=fake.word()) for _ in range(5)
        ]
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(parameter_types)} parameter types.")
        )

        # Generate Camera data
        cameras = []
        for _ in range(20):
            # Генерация случайного числа областей (от 1 до 3)
            num_areas = random.randint(1, 3)
            anchor_box_points = []

            for _ in range(num_areas):
                # Генерация случайного числа точек для каждой области (от 3 до 5, чтобы обеспечить многоугольник)
                num_points = random.randint(3, 5)
                area = [
                    {"x": random.randint(0, 1000), "y": random.randint(0, 1000)}
                    for _ in range(num_points)
                ]
                anchor_box_points.append(area)

            # Создание камеры с anchor_box_points в виде списка областей
            camera = Camera.objects.create(
                outlet=random.choice(outlets),
                name=fake.company(),
                preview=fake.image_url(),
                url_address=fake.url(),
                connection_login=fake.user_name(),
                connection_password=fake.password(),
                is_active=fake.boolean(),
                anchor_box_points=anchor_box_points,
            )
            cameras.append(camera)
        self.stdout.write(self.style.SUCCESS(f"Created {len(cameras)} cameras."))

        # Generate CameraParameter data
        camera_parameters = []
        for camera in cameras:
            for _ in range(
                random.randint(1, 3)
            ):  # random number of parameters per camera
                parameter = CameraParameter.objects.create(
                    camera=camera, parameter_type=random.choice(parameter_types)
                )
                camera_parameters.append(parameter)
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(camera_parameters)} camera parameters.")
        )

        # Generate Record data
        records = []
        for camera in cameras:
            for _ in range(
                random.randint(5, 10)
            ):  # random number of records per camera

                parameters = {}

                # С вероятностью 50% добавляем каждый из параметров
                if random.choice([True, False]):
                    parameters["queue_length"] = random.randint(
                        0, 20
                    )  # Random queue length between 0 and 20

                if random.choice([True, False]):
                    parameters["service_duration"] = random.randint(
                        30, 600
                    )  # Random service duration between 30 and 600 seconds

                if random.choice([True, False]):
                    parameters["has_earrings"] = random.choice(
                        [True, False]
                    )  # Randomly True or False

                # Если parameters пустой, добавляем один случайный параметр
                if not parameters:
                    parameter_to_add = random.choice(
                        ["queue_length", "service_duration", "has_earrings"]
                    )
                    if parameter_to_add == "queue_length":
                        parameters["queue_length"] = random.randint(0, 20)
                    elif parameter_to_add == "service_duration":
                        parameters["service_duration"] = random.randint(30, 600)
                    elif parameter_to_add == "has_earrings":
                        parameters["has_earrings"] = random.choice([True, False])

                # Create record with timezone-aware datetime
                record = Record.objects.create(
                    camera=camera,
                    record_time=timezone.make_aware(fake.date_time_this_year(), timezone.get_current_timezone()),
                    record_video=fake.file_path(extension="mp4"),
                    record_frame=fake.file_path(extension="jpg"),
                    parameters=parameters,
                )
                records.append(record)
        self.stdout.write(self.style.SUCCESS(f"Created {len(records)} records."))