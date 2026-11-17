from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class RouteDto:
    depotCoordinates : PositionDto
    orderedNodeCoordinates : list[PositionDto]
    stops : list[RouteStopDto]
    orderedSelectedSensors : list[RouteSensorDto]
    totalDistanceMeters : float
    routeGenerationMs : float


@dataclass
class PositionDto:
    latitude : float
    longitude : float


@dataclass
class RouteStopDto:
    stopIndex : int
    nodeId : int
    position : PositionDto


@dataclass
class RouteSensorDto:
    sensorId : int
    nodeId : int
    position : PositionDto
    fillLevel : float
    fillTimestamp : datetime


@dataclass
class PagedResponse[T]:
    currentPageNumber : int
    pageSize : int
    totalPages : int
    totalCount : int
    items : list[T]


@dataclass
class SensorHealthDto:
    isAlive : bool
    healthState: str
    latestFillLevel: Optional[float]
    latestReadingTimestamp : Optional[datetime]


@dataclass
class SensorDto:
    id : int
    isActive : bool
    nodeId : Optional[int]
    createdAt : datetime
    activatedAt : Optional[datetime]
    emptyDistanceMm : Optional[int]
    calibratedAtUtc : Optional[datetime]
    calibrationSampleCount : Optional[int]
    calibrationMethod : Optional[str]
    nodeLatitude : Optional[float]
    nodeLongitude : Optional[float]
    health : SensorHealthDto


class BackendApiService(ABC):
    
    @staticmethod
    @abstractmethod
    def get_route() -> RouteDto:
        pass


    @staticmethod
    @abstractmethod
    def get_sensors() -> list[SensorDto]:
        pass
