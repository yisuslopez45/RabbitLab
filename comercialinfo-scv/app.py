import logging
import time
import json

import pika


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [CommercialInfo] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Base de datos en memoria: lista de personas con su información de trabajo
DATABASE = [
    {"id": "12345", "name": "Juan Perez", "phone": "555-1234", "workplace": "Google"},
    {"id": "67890", "name": "Maria Garcia", "phone": "555-5678", "workplace": "Microsoft"},
    {"id": "11111", "name": "Carlos Lopez", "phone": "555-9999", "workplace": "Amazon"},
    {"id": "22222", "name": "Ana Martinez", "phone": "555-8888", "workplace": None},
]


def connect():
    """Intenta conectar de forma persistente a RabbitMQ."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            logging.info("Conectado a RabbitMQ")
            return connection
        except pika.exceptions.AMQPConnectionError:
            logging.warning("Esperando conexión con RabbitMQ...")
            time.sleep(5)


def search_person(name=None, person_id=None, phone=None):
    """Busca una persona en la BD por name, id o phone.
    
    Retorna el registro si encuentra coincidencia, None si no.
    """
    for record in DATABASE:
        if (person_id and record.get("id") == person_id) or \
           (name and record.get("name").lower() == name.lower()) or \
           (phone and record.get("phone") == phone):
            return record
    return None


def process_query(ch, method, properties, body):
    """Callback que procesa un mensaje de query.
    
    Espera un JSON con campos: name, id, phone.
    Busca en la BD y publica el resultado.
    """
    try:
        query_msg = json.loads(body.decode('utf-8'))
        logging.info(f"Query recibido: {query_msg}")
        
        # Extraer datos de la query
        name = query_msg.get("name")
        person_id = query_msg.get("id")
        phone = query_msg.get("phone")
        
        # Buscar en BD
        person = search_person(name=name, person_id=person_id, phone=phone)
        
        # Preparar respuesta
        if person:
            result = {
                "id": person.get("id"),
                "status": "found",
                "workplace": person.get("workplace"),
                "service": "commercialinfo"
            }
            logging.info(f"Persona encontrada: {result}")
        else:
            # Si no hay coincidencia, al menos devolvemos el id si lo tenemos
            search_id = person_id or phone or name or "unknown"
            result = {
                "id": search_id,
                "status": "not_found",
                "workplace": None,
                "service": "commercialinfo"
            }
            logging.info(f"Persona no encontrada: {result}")
        
        # Publicar resultado
        publish_result(result)
        
        # Reconocer el mensaje
        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        logging.exception("Error procesando query")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)


def publish_result(result):
    """Publica el resultado en el exchange 'results' (fanout)."""
    connection = None
    try:
        connection = connect()
        channel = connection.channel()
        
        # Declarar exchange de resultados
        channel.exchange_declare(
            exchange='results',
            exchange_type='fanout',
            durable=True
        )
        
        # Publicar
        body = json.dumps(result)
        channel.basic_publish(
            exchange='results',
            routing_key='',
            body=body.encode('utf-8')
        )
        logging.info(f"Resultado publicado en 'results': {result}")
        
    except Exception as e:
        logging.exception("Error publicando resultado en RabbitMQ")
    finally:
        try:
            if connection and connection.is_open:
                connection.close()
        except Exception:
            pass


def main():
    """Inicia el consumidor de queries."""
    connection = connect()
    channel = connection.channel()
    
    # Declarar exchange de queries
    channel.exchange_declare(
        exchange='looking-for',
        exchange_type='fanout',
        durable=True
    )
    
    # Crear cola temporal (exclusiva para este consumer)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Bindear cola al exchange
    channel.queue_bind(
        exchange='looking-for',
        queue=queue_name
    )
    
    logging.info(f"Esperando mensajes en cola: {queue_name}")
    
    # Configurar callback
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue=queue_name,
        on_message_callback=process_query,
        auto_ack=False
    )
    
    # Consumir
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.info("Deteniendo consumer...")
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
