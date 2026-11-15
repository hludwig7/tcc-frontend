from .backend_api_service import BackendApiService, RouteDto
from requests import get

class BackendApiServiceImpl(BackendApiService):

    BACKEND_API_URI_BASE : str = "http://localhost:8081/api";

    @staticmethod
    def get_route() -> RouteDto:
        response = get(f"{BackendApiServiceImpl.BACKEND_API_URI_BASE}/routes/collection?depotLatitude=-23.5624815&depotLongitude=-47.4632536")
        return RouteDto(**response.json())
    