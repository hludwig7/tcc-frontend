from pandas import DataFrame


def optimize_route(df : DataFrame) -> DataFrame:
    """
    Ordena as lixeiras mais críticas.
    MVP simples:
    Ordena por nível de ocupação.
    """

    route_df = df.sort_values(by="nivel", ascending=False)

    return route_df