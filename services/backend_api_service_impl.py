from .backend_api_service import BackendApiService, RouteDto, SensorDto, PagedResponse
from requests import get
from dacite import from_dict, Config
from datetime import datetime

_datetime_parser_hook_config = Config(type_hooks = { datetime: datetime.fromisoformat })

class BackendApiServiceImpl(BackendApiService):

    BACKEND_API_URI_BASE : str = "http://backend-api:8081/api";


    @staticmethod
    def get_route() -> RouteDto:
        response = get(f"{BackendApiServiceImpl.BACKEND_API_URI_BASE}/routes/collection")
        return RouteDto(**response.json())


    @staticmethod
    def get_sensors() -> list[SensorDto]:
        sensors : list[SensorDto] = []

        page_number = 1
        while True:
            response = get(f"{BackendApiServiceImpl.BACKEND_API_URI_BASE}/sensor-nodes?CurrentPageNumber={page_number}")
            page_number += 1

            deserialized_response = from_dict(
                PagedResponse[SensorDto],
                response.json(),
                config=_datetime_parser_hook_config
            )

            sensors.extend(deserialized_response.items)

            if (deserialized_response.currentPageNumber >= deserialized_response.totalPages):
                break;

        return sensors
    