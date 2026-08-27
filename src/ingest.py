from fetch_usgs import fetch_usgs_events
from fetch_usp import fetch_usp_events
from datetime import datetime
import csv

def validar_eventos(evento_a, evento_b):

    tempo_a = datetime.fromisoformat(evento_a["datahora_utc"])
    tempo_b = datetime.fromisoformat(evento_b["datahora_utc"])

    diferenca_tempo = abs((tempo_a - tempo_b).total_seconds())
    diferenca_latitude = abs(evento_a["latitude"] - evento_b["latitude"])
    diferenca_longitude = abs(evento_a["longitude"] - evento_b["longitude"])

    LIMITES_SEGUNDOS = 30
    LIMITES_GRAUS = 0.5

    if diferenca_tempo <= LIMITES_SEGUNDOS and diferenca_latitude <= LIMITES_GRAUS and diferenca_longitude <= LIMITES_GRAUS:
        return True

    return False

def marcar_duplicatas(eventos_usgs, eventos_usp):
    eventos_finais = []

    quantidade_duplicatas = 0

    for evento_usp in eventos_usp:
        evento_usp["duplicata_de"] = None
        eventos_finais.append(evento_usp)

    for evento_usgs in eventos_usgs:
        id_evento_usp_correspondente = None
 
        for evento_usp in eventos_usp:
            if validar_eventos(evento_usgs, evento_usp):
                id_evento_usp_correspondente = evento_usp["id_evento"]
                break
 
        evento_usgs["duplicata_de"] = id_evento_usp_correspondente
 
        if id_evento_usp_correspondente is not None:
            quantidade_duplicatas = quantidade_duplicatas + 1
 
        eventos_finais.append(evento_usgs)
 
    return eventos_finais, quantidade_duplicatas


def salvar_csv(eventos, caminho_arquivo):
    if len(eventos) == 0:
        print("Nâo há eventos para salvar.")
        return

    nome_dos_campos = list(eventos[0].keys())

    arquivo = open(caminho_arquivo, mode = "w", newline= "", encoding = "utf-8")

    escritor = csv.DictWriter(arquivo, fieldnames=nome_dos_campos)
    escritor.writeheader()

    for evento in eventos:
        escritor.writerow(evento)

    arquivo.close

    print("Arquivo salvo em: " + caminho_arquivo)

if __name__ == "__main__":
    data_inicio = "2026-08-01"
    data_fim = "2026-08-24"
 
    eventos_usgs = fetch_usgs_events(start_time=data_inicio, end_time=data_fim, min_magnitude=2.5)
    eventos_usp = fetch_usp_events(start_time=data_inicio, end_time=data_fim)
 
    eventos_combinados, quantidade_duplicatas = marcar_duplicatas(eventos_usgs, eventos_usp)
 
    print("")
    print("Resumo da ingestao:")
    print("  USGS: " + str(len(eventos_usgs)) + " eventos")
    print("  USP: " + str(len(eventos_usp)) + " eventos")
    print("  Marcados como duplicata: " + str(quantidade_duplicatas))
    print("  Total combinado (todas as linhas, incluindo duplicatas marcadas): " + str(len(eventos_combinados)) + " eventos")
    print("")
 
    salvar_csv(eventos_combinados, "eventos_sismicos.csv")