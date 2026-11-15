from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class RouteDto:
    depotCoordinates : PositionDto
    orderedNodeCoordinates : list[PositionDto]
    stops : list[RouteStopDto]
    selectedSensors : list[RouteSensorDto]
    totalDistance : float
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

class BackendApiService(ABC):
    
    @staticmethod
    @abstractmethod
    def get_route() -> RouteDto:
        pass