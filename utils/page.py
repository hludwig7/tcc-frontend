import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dataclasses import dataclass
from pandas import DataFrame
from services.backend_api_service import RouteDto, SensorDto
from statistics import mean


@dataclass
class PageRouteData:
    route: RouteDto
    df_sensors: DataFrame
    df_stops: DataFrame

    @staticmethod
    def from_route(route : RouteDto) -> PageRouteData:
        sensor_order_map = {stop["nodeId"]: stop["stopIndex"] for stop in route.stops}

        df_sensors = DataFrame(route.orderedSelectedSensors)
        df_sensors["collectOrder"] = df_sensors["nodeId"].map(sensor_order_map) + 1
        df_sensors["fillLevel"] = df_sensors["fillLevel"] * 100
        df_sensors[["latitude", "longitude"]] = pd.json_normalize(df_sensors["position"])[["latitude", "longitude"]]
        df_sensors = df_sensors.sort_values("collectOrder")

        df_stops = DataFrame(route.stops)
        df_stops[["latitude", "longitude"]] = pd.json_normalize(df_stops["position"])[["latitude", "longitude"]]

        return PageRouteData(route, df_sensors, df_stops)


@dataclass
class PageSensorData:
    sensors : list[SensorDto]
    avg_fill : float

    @staticmethod
    def from_sensors(sensors : list[SensorDto]) -> PageSensorData:
        avg_fill = sum([sensor.health.latestFillLevel * 100 for sensor in sensors if sensor.health.latestFillLevel is not None]) / len(sensors)
        return PageSensorData(sensors, avg_fill)


@dataclass
class PageData:
    route_data : PageRouteData
    sensor_data: PageSensorData

    @staticmethod
    def from_route(route : RouteDto) -> PageData:

        pageRouteData = PageRouteData.from_route(route)

        return PageData(pageRouteData)


class Page:

    @staticmethod
    def render(data : PageData) -> None:
        Page.init_page()
        Page._add_title()
        # Page._add_indicators_section(data.df_sensors, data.avg_fill)
        # Page._add_fill_level_bar_chart_section(data.df_sensors)
        # Page._add_fill_metrics_section(data.avg_fill, data.df_sensors)
        # Page._add_fill_level_histogram_section(data.df_sensors)
        # Page._add_fill_level_box_plot_section(data.df_sensors)
        Page._add_route_plot_section(data.route_data.route, data.route_data.df_sensors, data.route_data.df_stops)
        Page._add_sensors_plot_section(data.sensor_data)
        # Page._add_api_data_section(data.df_sensors)


    @staticmethod
    def init_page() -> None:
        st.set_page_config(
            page_title="Smart Trash Dashboard",
            layout="wide",
            page_icon="🗑️"
        )


    @staticmethod
    def _add_title() -> None:
        st.title("Dashboard")


    @staticmethod
    def _add_indicators_section(df_sensors : DataFrame, avg_fill : float) -> None:
        st.subheader("📊 Indicadores Operacionais")

        critical_bins = df_sensors[df_sensors["fillLevel"] >= 80].shape[0]
        total_bins = df_sensors.shape[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Lixeiras Monitoradas", total_bins)
        col2.metric("Lixeiras Críticas", critical_bins)
        col3.metric("Média de Ocupação", f"{avg_fill}%")
        return avg_fill


    @staticmethod
    def _add_fill_level_bar_chart_section(df_sensors : DataFrame) -> None:
        st.subheader("📈 Nível de Ocupação das Lixeiras")

        fig_bar = px.bar(
            df_sensors,
            x="sensorId",
            y="fillLevel",
            color="fillLevel",
            text="fillLevel",
            labels={
                "sensorId": "Sensor",
                "fillLevel": "Nível (%)"
            },
        )

        st.plotly_chart(fig_bar, width="stretch")


    @staticmethod
    def _add_fill_metrics_section(avg_fill : float, df_sensors : DataFrame) -> None:
        col_left, col_right = st.columns(2)

        with col_left:
            Page.add_fill_status_distribution_pie_chart_section(df_sensors)

        with col_right:
            Page.add_avg_fill_gauge_chart_section(avg_fill)


    @staticmethod
    def add_fill_status_distribution_pie_chart_section(df_sensors : DataFrame) -> None:
        st.subheader("📊 Distribuição por Status")
        
        critical = df_sensors[df_sensors["fillLevel"] >= 80].shape[0]
        warning = df_sensors[(df_sensors["fillLevel"] >= 70) & (df_sensors["fillLevel"] < 90)].shape[0]
        normal = df_sensors[df_sensors["fillLevel"] < 70].shape[0]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=["Crítica (≥80%)", "Alerta (70-79%)", "Normal (<70%)"],
            values=[critical, warning, normal],
            marker=dict(colors=["#d62728", "#ff7f0e", "#2ca02c"]),
            textposition="auto",
            hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>"
        )])
        
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, width="stretch")


    @staticmethod
    def add_avg_fill_gauge_chart_section(avg_fill : float) -> None:
        st.subheader("🎯 Ocupação Média Geral")
        
        fig_gauge = go.Figure(data=[go.Indicator(
            mode="gauge+number+delta",
            value=avg_fill,
            title={"text": "Ocupação (%)"},
            delta={"reference": 80},
            domain={"x": [0, 1], "y": [0, 1]},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "darkblue"},
                "steps": [
                    {"range": [0, 70], "color": "#2ca02c"},
                    {"range": [70, 80], "color": "#ff7f0e"},
                    {"range": [80, 100], "color": "#d62728"}
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 80
                }
            }
        )])
        
        fig_gauge.update_layout(height=400)
        st.plotly_chart(fig_gauge, width="stretch")


    @staticmethod
    def _add_fill_level_histogram_section(df_sensors : DataFrame) -> None:
        st.subheader("📈 Distribuição de Ocupação")

        fig_hist = px.histogram(
        df_sensors,
        x="fillLevel",
        nbins=20,
        title="Frequência dos Níveis de Ocupação",
        labels={"fillLevel": "Nível de Ocupação (%)"},
        color_discrete_sequence=["#3498db"]
    )

        fig_hist.update_xaxes(title_text="Nível de Ocupação (%)")
        fig_hist.update_yaxes(title_text="Quantidade de Lixeiras")

        st.plotly_chart(fig_hist, width="stretch")


    def _add_fill_level_box_plot_section(df_sensors : DataFrame) -> None:
        st.subheader("📊 Análise Estatística da Ocupação")

        fig_box = go.Figure(data=[
            go.Box(y=df_sensors["fillLevel"], name="Ocupação", marker_color="#9b59b6")
        ])

        fig_box.update_layout(
            yaxis_title="Nível de Ocupação (%)",
            height=400
        )

        st.plotly_chart(fig_box, width="stretch")


    @staticmethod
    def _add_route_plot_section(route : RouteDto, df_sensors : DataFrame, df_stops : DataFrame) -> None:
        st.subheader("Rota de Coleta")

        # Extrair coordenadas da rota
        route_lons = [coord["longitude"] for coord in route.orderedNodeCoordinates]
        route_lats = [coord["latitude"] for coord in route.orderedNodeCoordinates]

        fig_map_route = go.Figure()

        # linha da rota
        fig_map_route.add_trace(go.Scattermapbox(
            mode="lines",
            lon=route_lons,
            lat=route_lats,
            line=dict(width=3, color="red"),
            name="Rota",
            hovertemplate="<b>Rota</b><extra></extra>"
        ))

        # Preparar dados dos stops ordenados por stopIndex
        df_stops_sorted = df_stops.sort_values("stopIndex").reset_index(drop=True)

        # Criar mapa nodeId -> fillLevel dos sensores
        sensor_fill_map = {row["nodeId"]: row["fillLevel"] for _, row in df_sensors.iterrows()}

        # Determinar nível de ocupação para cada stop (50 para início/fim sem sensor)
        fill_levels_stops = [sensor_fill_map.get(nodeId, 50) for nodeId in df_stops_sorted["nodeId"]]

        # Separar pontos em dois grupos para textposition alternado
        even_indices = [i for i in range(len(df_stops_sorted)) if i % 2 == 0]
        odd_indices = [i for i in range(len(df_stops_sorted)) if i % 2 != 0]

        # Trace para índices pares (top center)
        if even_indices:
            df_even = df_stops_sorted.iloc[even_indices].reset_index(drop=True)
            fill_even = [fill_levels_stops[i] for i in even_indices]
            fig_map_route.add_trace(go.Scattermapbox(
            mode="markers+text",
            lon=df_even["longitude"],
            lat=df_even["latitude"],
            marker={
                "size": 16,
                "color": fill_even,
                "colorscale": "RdYlGn_r",
                "showscale": False,
                "opacity": 0.95
            },
            text="Stop " + (df_even["stopIndex"] + 1).astype(str),
            textposition="top center",
            textfont={"size": 11, "color": "black"},
            hovertemplate="<b>Parada %{text}</b><extra></extra>",
            name="Paradas (Top)",
            showlegend=False
        ))

        # Trace para índices ímpares (bottom center)
        if odd_indices:
            df_odd = df_stops_sorted.iloc[odd_indices].reset_index(drop=True)
            fill_odd = [fill_levels_stops[i] for i in odd_indices]
            fig_map_route.add_trace(go.Scattermapbox(
                mode="markers+text",
                lon=df_odd["longitude"],
                lat=df_odd["latitude"],
                marker={
                    "size": 16,
                    "color": fill_odd,
                    "colorscale": "RdYlGn_r",
                    "showscale": True,
                    "colorbar": {
                        "title": "Fill Level (%)",
                        "thickness": 15,
                        "len": 0.7
                    },
                    "opacity": 0.95
                },
                text="Stop " + (df_odd["stopIndex"] + 1).astype(str),
                textposition="bottom center",
                textfont={"size": 11, "color": "black"},
                hovertemplate="<b>Parada %{text}</b><extra></extra>",
                name="Paradas"
            ))

        fig_map_route.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=15,
            mapbox_center={
                "lat": df_sensors["latitude"].mean(),
                "lon": df_sensors["longitude"].mean(),
            },  
            height=600,
            margin={"r":0,"t":0,"l":0,"b":0},
            hovermode="closest"
        )

        st.plotly_chart(fig_map_route, width="stretch")


    @staticmethod
    def _add_sensors_plot_section(sensorData : PageSensorData) -> None:
        st.subheader("Mapa dos Pontos de Coleta")

        fig_map_bins = go.Figure()

        active_sensors = [
            sensor
            for sensor
            in sensorData.sensors
            if
                sensor.isActive and
                sensor.health is not None and sensor.health.isAlive
        ] 

        fig_map_bins.add_trace(go.Scattermapbox(
            mode="markers+text",
            lon=[ sensor.nodeLongitude for sensor in active_sensors ],
            lat=[ sensor.nodeLatitude for sensor in active_sensors ],
            marker={
                "size": 18,
                "color": [
                    sensor.health.latestFillLevel
                    if (
                        (sensor.health is not None) and
                        (sensor.health.latestFillLevel is not None)
                    )
                    else -1
                    for sensor
                    in active_sensors
                ],
                "colorscale": "RdYlGn_r",
                "showscale": True,
                "opacity": 0.95
            },
            text=[ f"{sensor.id}" for sensor in active_sensors ],
            textposition="top center",
            textfont={"size": 16, "color": "white"},
            hovertemplate="<b>%{text}</b><extra></extra>",
            name="Lixeiras Monitoradas"
        ))

        fig_map_bins.update_layout(
            mapbox_style="open-street-map",
            mapbox_zoom=15,
            mapbox_center={
                "lat": mean([ sensor.nodeLatitude for sensor in active_sensors if sensor.nodeLatitude is not None ]),
                "lon": mean([ sensor.nodeLongitude for sensor in active_sensors if sensor.nodeLongitude is not None ]),
            },  
            height=600,
            margin={"r":0,"t":0,"l":0,"b":0},
            hovermode="closest"
        )

        st.plotly_chart(fig_map_bins, width="stretch")


    @staticmethod
    def _add_api_data_section(df_sensors : DataFrame) -> None:
        st.subheader("📋 Dados Recebidos da API")

        st.dataframe(df_sensors, width="stretch")