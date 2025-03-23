from pydantic import BaseModel, Field
from typing import Optional, List


class PointSchema(BaseModel):
    """
    Схема точки с координатами x и y.

    Attributes:
        x (int): Координата по оси X.
        y (int): Координата по оси Y.
    """

    x: int = Field(..., description="Координата по оси X")
    y: int = Field(..., description="Координата по оси Y")


class PolygonSchema(BaseModel):
    """
    Схема полигона, содержащая уникальный идентификатор и список точек.

    Attributes:
        id (int): Уникальный идентификатор полигона.
        points (List[PointSchema]): Список точек полигона.
    """

    id: int = Field(..., description="Уникальный идентификатор полигона")
    points: List[PointSchema] = Field(..., description="Список точек полигона")


class ROIPolygonsSchema(BaseModel):
    """
    Схема для 'roi_polygons', представляющая список полигонов зон интереса.

    Attributes:
        polygons (List[PolygonSchema]): Список полигонов, каждый из которых содержит уникальный ID и точки.
    """

    polygons: List[PolygonSchema] = Field(
        ...,
        description="Список полигонов, каждый из которых содержит уникальный ID и точки",
    )


class IndicatorsStatusSchema(BaseModel):
    """
    Схема для `indicators_types`, указывающая какие показатели отслеживаются.

    Attributes:
        queue_length (bool): Отслеживание длины очереди.
        service_duration (bool): Отслеживание времени обслуживания клиента.
        jewelry_absent (bool): Отслеживание отсутствия украшений у сотрудника.
    """

    queue_length: bool = Field(..., description="Отслеживание длины очереди")
    service_duration: bool = Field(
        ..., description="Отслеживание времени обслуживания клиента"
    )
    jewelry_absent: bool = Field(
        ..., description="Отслеживание отсутствия украшений у сотрудника"
    )


class IndicatorsSchema(BaseModel):
    """
    Схема для `indicators`, хранящая значения отслеживаемых параметров или пороговые значения для них.

    Attributes:
        queue_length (Optional[int]): Длина очереди, если отслеживается.
        service_duration (Optional[float]): Время обслуживания клиента в секундах, если отслеживается.
        jewelry_absent (Optional[bool]): Отсутствие украшений у сотрудника, если отслеживается.
    """

    queue_length: Optional[int] = Field(
        None, description="Длина очереди, если отслеживается"
    )
    service_duration: Optional[float] = Field(
        None, description="Время обслуживания клиента в секундах, если отслеживается"
    )
    jewelry_absent: Optional[bool] = Field(
        None, description="Отсутствие украшений у сотрудника, если отслеживается"
    )
