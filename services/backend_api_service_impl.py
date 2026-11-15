from .backend_api_service import BackendApiService, RouteDto
from requests import get

class BackendApiServiceImpl(BackendApiService):

    BACKEND_API_URI_BASE : str = "http://localhost:8081/api";

    @staticmethod
    def get_route() -> RouteDto:
        response = get(f"{BackendApiServiceImpl.BACKEND_API_URI_BASE}/routes/collection")
        return RouteDto(**response.json())
    