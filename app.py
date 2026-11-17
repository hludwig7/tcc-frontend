from services.backend_api_service import BackendApiService
from services.backend_api_service_impl import BackendApiServiceImpl
from utils.page import Page, PageData, PageRouteData, PageSensorData
import streamlit



@streamlit.fragment(run_every="5s")
def app_main(apiService: BackendApiService):
    
    route = apiService.get_route()
    route_data = PageRouteData.from_route(route)

    sensors = apiService.get_sensors()
    sensor_data = PageSensorData.from_sensors(sensors)
    
    page_data = PageData(route_data, sensor_data)

    Page.render(page_data)

app_main(BackendApiServiceImpl())