import logging
import time
import json

import pika
from flask import Flask, request, jsonify

app = Flask(__name__)


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [Query] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def connect():
    """Intenta conectar de forma persistente a RabbitMQ (host 'rabbitmq').

    Devuelve una pika.BlockingConnection cuando esté disponible.
    """
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.warning("Esperando conexión con RabbitMQ...")
            time.sleep(5)


@app.route("/health")
def health():
    return "OK"


@app.route("/query", methods=["POST"])
def index():
    """Recibe un JSON por POST con alguno de los campos: name, id, phone.

    Publica el payload (como JSON) en el exchange 'looking-for' (fanout).
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request, expected JSON body"}), 400

    name = data.get("name")
    person_id = data.get("id")
    phone = data.get("phone")

    if not (name or person_id or phone):
        return jsonify({"error": "At least one of 'name', 'id' or 'phone' must be provided"}), 400

    msg = {
        "name": name,
        "id": person_id,
        "phone": phone,
    }

    body = json.dumps(msg)

    connection = None
    try:
        connection = connect()
        channel = connection.channel()
        # declaramos exchange (fanout) de forma idempotente
        channel.exchange_declare(exchange='looking-for', exchange_type='fanout', durable=True)
        channel.basic_publish(
            exchange='looking-for',
            routing_key='',
            body=body.encode('utf-8'),
        )
        logging.info(f"query notificó que se debe buscar información de: {name}")
    except Exception:
        logging.exception("Error publicando en RabbitMQ")
        return jsonify({"error": "Failed to publish message"}), 500
    finally:
        try:
            if connection and connection.is_open:
                connection.close()
        except Exception:
            pass

    return jsonify({"status": "Query initiated"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
