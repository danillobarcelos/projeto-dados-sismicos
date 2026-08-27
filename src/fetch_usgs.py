import requests
from datetime import datetime, timezone

USGS_BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

def fetch_usgs_events(start_time, end_time, min_magnitude=None, bbox=None, limit=20000):

    params = {
        "format":"geojson",
        "starttime": start_time,
        "endtime": end_time,
        "orderby": "time",
        "limit": limit,
    }

    if min_magnitude is not None:
        params["minmagnitude"] = min_magnitude

    if bbox is not None:
        params["minlatitude"] = bbox["minlatitude"]
        params["maxlatitude"] = bbox["maxlatitude"]
        params["minlongitude"] = bbox["minlongitude"]
        params["maxlongitude"] = bbox["maxlongitude"]


    response = requests.get(USGS_BASE_URL, params=params, timeout=30)

#   print("Status code:", response.status_code)
#    print("Resposta: ", response.text)

    response.raise_for_status()

    dados = response.json()

    total_eventos = dados["metadata"]["offset"]

    print("[USGS] " + str(total_eventos) + " eventos retornados (" + start_time + " a " + end_time + ")")

    lista_eventos = []
    for feature in dados["features"]:
        evento_normalizado = normalizar_evento(feature)
        lista_eventos.append(evento_normalizado)

    return lista_eventos


def normalizar_evento(feature):

    propriedades = feature["properties"]
    coordenadas = feature["geometry"]["coordinates"]

    longitude = coordenadas[0]
    latitude = coordenadas[1]
    profundidade_km = coordenadas[2]

##usgs retorna o campo time em ms, sendo necessário a conversão para segundos

    tempo_ms = propriedades["time"]
    tempo_s = tempo_ms / 1000
    datahora_utc = datetime.fromtimestamp(tempo_s, tz=timezone.utc)

    evento_normalizado = {
        "id_evento" : "usgs_" + feature["id"],
        "fonte":"USGS",
        "datahora_utc": datahora_utc.isoformat(),
        "magnitude": propriedades.get("mag"),
        "tipo_magnitude": propriedades.get("magType"),
        "profundidade_km": profundidade_km,
        "latitude": latitude,
        "longitude": longitude,
        "local": propriedades.get("place"),
        "url_detalhe": propriedades.get("url"),
    }

    return evento_normalizado

if __name__ == "__main__":

        bbox_brasil = {
        "minlatitude": -34,
        "maxlatitude": 6,
        "minlongitude": -74,
        "maxlongitude": -32,
    }

        eventos = fetch_usgs_events(
        start_time="2026-08-01",
        end_time="2026-08-23",
        bbox=bbox_brasil,
    )

        print("")
        print(str(len(eventos)) + " eventos normalizados. Amostra:")
        print("")

        for evento in eventos[:5]:
            print(evento)