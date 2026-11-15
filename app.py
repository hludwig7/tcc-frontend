from services.backend_api_service import BackendApiService
from services.backend_api_service_impl import BackendApiServiceImpl
from utils.page import Page, PageData


apiService : BackendApiService = BackendApiServiceImpl()

route = apiService.get_route()

page_data = PageData.from_route(route)

Page.render(page_data)
