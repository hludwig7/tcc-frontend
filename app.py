from services.backend_api_service import BackendApiService
from services.backend_api_service_impl import BackendApiServiceImpl
from utils.page import Page, PageData

import streamlit

@streamlit.fragment(run_every="5s")
def app_main(apiService: BackendApiService):
    route = apiService.get_route()
    page_data = PageData.from_route(route)
    Page.render(page_data)

app_main(BackendApiServiceImpl())