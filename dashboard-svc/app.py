import logging
import threading
import time
import json
from collections import defaultdict

import pika
from flask import Flask, render_template, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [Dashboard] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Diccionario en memoria para almacenar resultados
# Estructura: {query_id: {service_name: result_data}}
results_dict = defaultdict(dict)

# Lock para acceso thread-safe
results_lock = threading.Lock()


def connect():
    """Intenta conectar de forma persistente a RabbitMQ."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            logging.info("Dashboard conectado a RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.warning("Dashboard esperando conexión con RabbitMQ...")
            time.sleep(5)


def process_result(ch, method, properties, body):
    """Callback que procesa resultados de los servicios.
    
    Espera un JSON con: id, status, y datos específicos del servicio.
    """
    try:
        result_msg = json.loads(body.decode('utf-8'))
        logging.info(f"Resultado recibido: {result_msg}")
        
        # Extraer identificador y servicio origen (del header o del cuerpo)
        query_id = result_msg.get("id", "unknown")
        service_name = result_msg.get("service", "unknown")
        
        # Almacenar resultado con thread-safety
        with results_lock:
            results_dict[query_id][service_name] = result_msg
            logging.info(f"Resultado almacenado para query_id={query_id}, service={service_name}")
        
        # Reconocer mensaje
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logging.exception("Error procesando resultado")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def consumer_thread():
    """Función que corre en un thread separado para consumir resultados."""
    try:
        connection = connect()
        channel = connection.channel()
        
        # Declarar exchange de resultados
        channel.exchange_declare(
            exchange='results',
            exchange_type='fanout',
            durable=True
        )
        
        # Crear cola temporal (exclusiva para este consumer)
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        
        # Bindear cola al exchange
        channel.queue_bind(
            exchange='results',
            queue=queue_name
        )
        
        logging.info(f"Dashboard escuchando en cola: {queue_name}")
        
        # Configurar callback
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(
            queue=queue_name,
            on_message_callback=process_result,
            auto_ack=False
        )
        
        # Consumir
        channel.start_consuming()
        
    except Exception as e:
        logging.exception("Error en consumer thread")


@app.route("/health")
def health():
    return "OK"


@app.route("/viewresults")
def view_results():
    """Renderiza HTML con todas las consultas y resultados almacenados."""
    with results_lock:
        # Convertir defaultdict a dict normal para pasar a template
        results_data = dict(results_dict)
    
    logging.info(f"Mostrando {len(results_data)} consultas")
    return render_template('results.html', results=results_data)


@app.route("/api/results")
def get_results_json():
    """Endpoint API que retorna los resultados en JSON."""
    with results_lock:
        results_data = dict(results_dict)
    return jsonify(results_data)


@app.route("/api/results/<query_id>")
def get_result_by_id(query_id):
    """Endpoint API que retorna resultados de una query específica."""
    with results_lock:
        result = results_dict.get(query_id, {})
    return jsonify(result)


if __name__ == "__main__":
    # Iniciar thread consumer en background
    consumer = threading.Thread(target=consumer_thread, daemon=True)
    consumer.start()
    logging.info("Thread consumer iniciado")
    
    # Esperar un momento para que el consumer se conecte
    time.sleep(2)
    
    # Iniciar Flask
    app.run(host="0.0.0.0", port=5001)
