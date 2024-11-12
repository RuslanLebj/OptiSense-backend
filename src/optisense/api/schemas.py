from pydantic import BaseModel, Field
from typing import Optional, List


class Point(BaseModel):
    """
    Схема точки с координатами x и y.

    Attributes:
        x (int): Координата по оси X.
        y (int): Координата по оси Y.
    """
    x: int = Field(..., description="Координата по оси X")
    y: int = Field(..., description="Координата по оси Y")


class Polygon(BaseModel):
    """
    Схема полигона, содержащая уникальный идентификатор и список точек.

    Attributes:
        id (int): Уникальный идентификатор полигона.
        points (List[Point]): Список точек полигона.
    """
    id: int = Field(..., description="Уникальный идентификатор полигона")
    points: List[Point] = Field(..., description="Список точек полигона")


class ROIPolygonsPointsSchema(BaseModel):
    """
    Схема для `roi_polygons_points`, представляющая массив полигонов.

    Attributes:
        polygons (List[Polygon]): Список полигонов, каждый из которых содержит уникальный ID и точки.
    """
    polygons: List[Polygon] = Field(...,
                                    description="Список полигонов, каждый из которых содержит уникальный ID и точки")


class ParameterTypesSchema(BaseModel):
    """
    Схема для `parameter_types`, указывающая, отслеживается ли каждый параметр.

    Attributes:
        queue_length (bool): Отслеживание длины очереди.
        service_duration (bool): Отслеживание времени обслуживания клиента.
        has_earrings (bool): Отслеживание наличия украшений у сотрудника.
    """
    queue_length: bool = Field(..., description="Отслеживание длины очереди")
    service_duration: bool = Field(..., description="Отслеживание времени обслуживания клиента")
    has_earrings: bool = Field(..., description="Отслеживание наличия украшений у сотрудника")


class ParametersSchema(BaseModel):
    """
    Схема для `parameters`, хранящая значения отслеживаемых параметров.

    Attributes:
        queue_length (Optional[int]): Длина очереди, если отслеживается.
        service_duration (Optional[float]): Время обслуживания клиента в секундах, если отслеживается.
        has_earrings (Optional[bool]): Наличие украшений у сотрудника, если отслеживается.
    """
    queue_length: Optional[int] = Field(None, description="Длина очереди, если отслеживается")
    service_duration: Optional[float] = Field(None,
                                              description="Время обслуживания клиента в секундах, если отслеживается")
    has_earrings: Optional[bool] = Field(None, description="Наличие украшений у сотрудника, если отслеживается")
