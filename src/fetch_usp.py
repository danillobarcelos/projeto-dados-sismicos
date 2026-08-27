import requests
from datetime import datetime, timezone

USP_MOHO_URL_BASE = "https://www.moho.iag.usp.br/fdsnws/event/1/query"

def fetch_usp_events(start_time, end_time, min_magnitude=None, max_magnitude=None, bbox = None, limit = 20000):

    params = {
        "format": "text",
        "starttime": start_time,
        "endtime": end_time,
        "orderby": "time",
        "limit": limit,
    }

    if min_magnitude is not None:
        params["minmagnitude"] = min_magnitude

    if max_magnitude is not None:
        params["maxmagnitude"] = max_magnitude

    if bbox is not None:
        params["minlatitude"] = bbox["minlatitude"]
        params["maxlatitude"] = bbox["maxlatitude"]
        params["minlongitude"] = bbox["minlongitude"]
        params["maxlongitude"] = bbox["maxlongitude"]

    response = requests.get(USP_MOHO_URL_BASE, params=params, timeout=30)
    response.raise_for_status()

    #testando resultado da response
    #print("Status code:", response.status_code)
    #print("Resposta: ", response.text)

    texto_resposta = response.text
    linhas = texto_resposta.strip().split("\n")

    print("[USP] " + str(len(linhas) - 1) + " eventos retornados (" + start_time + " a " + end_time + ")")

    lista_eventos = []
    for linha in linhas:
        if linha.startswith("#") or linha.strip() == "":
            continue

        evento_normalizado = normalizar_evento_usp(linha)
        lista_eventos.append(evento_normalizado)

    return lista_eventos

def normalizar_evento_usp(linha):

    campos = linha.split("|")

    event_id = campos[0]
    tempo_texto = campos[1]
    latitude = float(campos[2])
    longitude = float(campos[3])
    profundidade_km = float(campos[4])
    tipo_magnitude = campos[9]
    magnitude = float(campos[10])
    local = campos[12]

    datahora_sem_fuso = datetime.fromisoformat(tempo_texto)
    datahora_utc = datahora_sem_fuso.replace(tzinfo=timezone.utc)

    evento_normalizado = {
        "id_evento": "usp_" + event_id,
        "fonte": "USP",
        "datahora_utc": datahora_utc.isoformat(),
        "magnitude": magnitude,
        "tipo_magnitude": tipo_magnitude,
        "profundidade_km": profundidade_km,
        "latitude": latitude,
        "longitude": longitude,
        "local": local,
        "url_detalhe": None, 
    }

    return evento_normalizado


if __name__ == "__main__":
    eventos = fetch_usp_events(
        start_time="2026-08-01",
        end_time="2026-08-23",
    )
 
    print("")
    print(str(len(eventos)) + " eventos normalizados. Amostra:")
    print("")
 
    for evento in eventos[:5]:
        print(evento)