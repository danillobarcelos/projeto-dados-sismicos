import psycopg2
from config import DATABASE_URL

def conectar():
    conexao = psycopg2.connect(DATABASE_URL)
    return conexao

def carregar_eventos():
    conexao = conectar()
    cursor = conexao.cursor()

    comando_sql = """
        INSERT INTO bronze_eventos_sismicos (
            id_evento, fonte, datahora_utc, magnitude, tipo_magnitude,
            profundidade_km, latitude, longitude, local, url_detalhe,
            duplicata_de
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id_evento) DO NOTHING;
    """

    quantidade_inserida = 0

    for evento in eventos:
        valores = (
            evento["id_evento"],
            evento["fonte"],
            evento["datahora_utc"],
            evento["magnitude"],
            evento["tipo_magnitude"],
            evento["profundidade_km"],
            evento["latitude"],
            evento["longitude"],
            evento["local"],
            evento["url_detalhe"],
            evento["duplicata_de"],
        )

    cursor.execute(comando_sql, valores)

    quantidade_inserida = quantidade_inserida + cursor.rowcount

    conexao.commit()

    cursor.close()
    conexao.close()

    print("Linhas novas inseridas no Postgres: " + str(quantidade_inserida))
    print("(as demais ja existiam e foram ignoradas)")