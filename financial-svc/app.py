import logging
import threading
import time
import json

import pika

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [Financial] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Base de datos en memoria con información financiera
financial_db = [
    {
        "id": "12345",
        "name": "Juan Perez",
        "bank": "Banco de Bogotá",
        "account_type": "Cuenta de Ahorros",
        "credit_score": 750,
        "status": "Activo",
    },
    {
        "id": "67890",
        "name": "Maria Lopez",
        "bank": "Bancolombia",
        "account_type": "Cuenta Corriente",
        "credit_score": 820,
        "status": "Activo",
    },
    {
        "id": "11111",
        "name": "Carlos Ruiz",
        "bank": "Davivienda",
        "account_type": "Cuenta de Ahorros",
        "credit_score": 680,
        "status": "Suspendido",
    },
    {
        "id": "22222",
        "name": "Ana Torres",
        "bank": "BBVA Colombia",
        "account_type": "Cuenta Corriente",
        "credit_score": 795,
        "status": "Activo",
    },
]


def connect():
    """Intenta conectar de forma persistente a RabbitMQ."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
            logging.info("Financial service conectado a RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.warning("Financial service esperando conexión con RabbitMQ...")
            time.sleep(5)


def search_financial_info(person_id):
    """Busca información financiera en la BD en memoria por ID."""
    for record in financial_db:
        if record["id"] == person_id:
            return record
    return None


def process_query(ch, method, properties, body):
    """Callback que procesa queries del exchange 'looking-for'."""
    try:
        query_msg = json.loads(body.decode("utf-8"))
        logging.info(f"Query recibida: {query_msg}")

        person_id = query_msg.get("id")
        name = query_msg.get("name")

        if not person_id:
            logging.warning("Query sin ID, ignorando")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        # Buscar en BD
        result = search_financial_info(person_id)

        if result:
            response = {
                "id": person_id,
                "status": "found",
                "bank": result["bank"],
                "account_type": result["account_type"],
                "credit_score": result["credit_score"],
                "account_status": result["status"],
                "service": "financial",
            }
            logging.info(
                f"Información financiera encontrada para ID={person_id}: {result['bank']}"
            )
        else:
            response = {
                "id": person_id,
                "status": "not_found",
                "bank": None,
                "account_type": None,
                "credit_score": None,
                "account_status": None,
                "service": "financial",
            }
            logging.info(f"No se encontró información financiera para ID={person_id}")

        # Publicar resultado en exchange 'results'
        result_body = json.dumps(response)
        ch.basic_publish(
            exchange="results", routing_key="", body=result_body.encode("utf-8")
        )
        logging.info(f"Resultado publicado para ID={person_id}")

        # Reconocer mensaje
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        logging.exception("Error procesando query")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def start_consumer():
    """Inicia el consumer que escucha queries."""
    try:
        connection = connect()
        channel = connection.channel()

        # Declarar exchanges
        channel.exchange_declare(
            exchange="looking-for", exchange_type="fanout", durable=True
        )

        channel.exchange_declare(
            exchange="results", exchange_type="fanout", durable=True
        )

        # Crear cola exclusiva para este consumer
        result = channel.queue_declare(queue="", exclusive=True)
        queue_name = result.method.queue

        # Bindear al exchange 'looking-for'
        channel.queue_bind(exchange="looking-for", queue=queue_name)

        logging.info(f"Financial service escuchando en cola: {queue_name}")

        # Configurar callback
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name, on_message_callback=process_query, auto_ack=False
        )

        # Consumir
        logging.info("Iniciando consumo de mensajes...")
        channel.start_consuming()

    except KeyboardInterrupt:
        logging.info("Interrumpido por usuario")
        channel.stop_consuming()
        connection.close()
    except Exception as e:
        logging.exception("Error en consumer")


if __name__ == "__main__":
    start_consumer()
