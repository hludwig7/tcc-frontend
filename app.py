import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from services.mock_api import get_mock_data


# ========================================
# CONFIGURAÇÃO
# ========================================

st.set_page_config(
    page_title="Smart Trash Dashboard",
    layout="wide",
    page_icon="🗑️"
)

st.title("🗑️ Dashboard de Lixeira Inteligente")


# ========================================
# CONSUMO DA API
# ========================================

payload = get_mock_data()


# ========================================
# EXTRAÇÃO DOS DADOS
# ========================================

# Coordenadas da rota em ordem
route_coordinates = payload.get("orderedNodeCoordinates", [])

# Dados de paradas
stops_data = payload.get("stops", [])

# Dados de sensores com fill level
sensors_data = payload.get("selectedSensors", [])

# Criar DataFrames
df_sensors = pd.DataFrame(sensors_data)
df_stops = pd.DataFrame(stops_data)

# Mapear stopIndex para cada sensor pelo nodeId
sensor_order_map = {stop["nodeId"]: stop["stopIndex"] for stop in stops_data}
df_sensors["collectOrder"] = df_sensors["nodeId"].map(sensor_order_map) + 1
df_sensors["fillLevel"] = df_sensors["fillLevel"] * 100

# Extrair latitude e longitude das posições
df_sensors[["latitude", "longitude"]] = pd.json_normalize(df_sensors["position"])[["latitude", "longitude"]]
df_stops[["latitude", "longitude"]] = pd.json_normalize(df_stops["position"])[["latitude", "longitude"]]

df_sensors = df_sensors.sort_values("collectOrder")


# ========================================
# KPIs
# ========================================

st.subheader("📊 Indicadores Operacionais")

critical_bins = df_sensors[df_sensors["fillLevel"] >= 90].shape[0]
avg_fill = round(df_sensors["fillLevel"].mean(), 2)
total_bins = df_sensors.shape[0]

col1, col2, col3 = st.columns(3)

col1.metric("Lixeiras Monitoradas", total_bins)
col2.metric("Lixeiras Críticas", critical_bins)
col3.metric("Média de Ocupação", f"{avg_fill}%")


# ========================================
# GRÁFICO DE BARRAS
# ========================================

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

st.plotly_chart(fig_bar, use_container_width=True)


# ========================================
# GRÁFICOS COMPLEMENTARES
# ========================================

col_left, col_right = st.columns(2)

# Gráfico de Pizza - Distribuição por Status
with col_left:
    st.subheader("📊 Distribuição por Status")
    
    critical = df_sensors[df_sensors["fillLevel"] >= 90].shape[0]
    warning = df_sensors[(df_sensors["fillLevel"] >= 70) & (df_sensors["fillLevel"] < 90)].shape[0]
    normal = df_sensors[df_sensors["fillLevel"] < 70].shape[0]
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=["Crítica (≥90%)", "Alerta (70-89%)", "Normal (<70%)"],
        values=[critical, warning, normal],
        marker=dict(colors=["#d62728", "#ff7f0e", "#2ca02c"]),
        textposition="auto",
        hovertemplate="<b>%{label}</b><br>Quantidade: %{value}<br>Percentual: %{percent}<extra></extra>"
    )])
    
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)


# Gráfico de Gauge - Ocupação Média
with col_right:
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
                {"range": [70, 90], "color": "#ff7f0e"},
                {"range": [90, 100], "color": "#d62728"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.75,
                "value": 90
            }
        }
    )])
    
    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True)


# Gráfico de Histograma - Distribuição de Ocupação
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

st.plotly_chart(fig_hist, use_container_width=True)


# Gráfico de Caixa - Box Plot
st.subheader("📊 Análise Estatística da Ocupação")

fig_box = go.Figure(data=[
    go.Box(y=df_sensors["fillLevel"], name="Ocupação", marker_color="#9b59b6")
])

fig_box.update_layout(
    yaxis_title="Nível de Ocupação (%)",
    height=400
)

st.plotly_chart(fig_box, use_container_width=True)



st.subheader("🗺️ Mapa dos Pontos de Coleta")

fig_map_bins = go.Figure()

# Sensores com destaque em cores
fig_map_bins.add_trace(go.Scattermapbox(
    mode="markers+text",
    lon=df_sensors["longitude"],
    lat=df_sensors["latitude"],
    marker={
        "size": 18,
        "color": df_sensors["fillLevel"],
        "colorscale": "RdYlGn_r",
        "showscale": True,
        "opacity": 0.95
    },
    text=[f"{order}" 
          for order in zip(df_stops["stopIndex"])],
    textposition="top center",
    textfont={"size": 16, "color": "white"},
    hovertemplate="<b>%{text}</b><extra></extra>",
    name="Lixeiras"
))

fig_map_bins.update_layout(
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

st.plotly_chart(fig_map_bins, use_container_width=True)


# ========================================
# MAPA DA ROTA DE COLETA
# ========================================

st.subheader("🚚 Rota de Coleta")

# Extrair coordenadas da rota
route_lons = [coord["longitude"] for coord in route_coordinates]
route_lats = [coord["latitude"] for coord in route_coordinates]

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

st.plotly_chart(fig_map_route, use_container_width=True)


# ========================================
# TABELA OPERACIONAL
# ========================================

st.subheader("📋 Dados Recebidos da API")

st.dataframe(df_sensors, use_container_width=True)