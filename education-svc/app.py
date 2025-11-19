from flask import Flask
import pika
import json
import time

app = Flask(__name__)

# Información educativa
education_db = [
    {"id": "12345", "name": "Juan Perez", "university": "Universidad Nacional", "degree": "Ingeniería de Sistemas"},
    {"id": "67890", "name": "Maria Garcia", "university": "Universidad de los Andes", "degree": "Medicina"},
    {"id": "11111", "name": "Carlos Lopez", "university": "Universidad Javeriana", "degree": "Derecho"},
    {"id": "22222", "name": "Ana Martinez", "university": "Universidad del Valle", "degree": "Administración"}
]

def get_rabbitmq_connection():
    """Establece conexión con RabbitMQ con reintentos"""
    max_retries = 30
    retry_delay = 10
    
    for attempt in range(max_retries):
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq', heartbeat=600)
            )
            print(f"Conectado a RabbitMQ (intento {attempt + 1})")
            return connection
        except pika.exceptions.AMQPConnectionError as e:
            print(f"Error conectando a RabbitMQ (intento {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                raise

def search_education(person_id, name):
    """Busca información educativa en la base de datos"""
    for record in education_db:
        if record['id'] == person_id or record['name'].lower() == name.lower():
            return {
                "id": person_id,
                "status": "found",
                "university": record['university'],
                "degree": record['degree'],
                "service": "education"
            }
    
    # Si no se encuentra
    return {
        "id": person_id,
        "status": "not_found",
        "university": None,
        "degree": None,
        "service": "education"
    }

def callback(ch, method, properties, body):
    """Procesa mensajes del exchange 'looking-for'"""
    try:
        query = json.loads(body)
        print(f"Recibida consulta: {query}")
        
        # Buscar en la base de datos
        result = search_education(query.get('id'), query.get('name'))
        print(f"Resultado: {result}")
        
        # Publicar resultado en exchange 'results'
        ch.basic_publish(
            exchange='results',
            routing_key='',
            body=json.dumps(result)
        )
        print(f" Resultado publicado en 'results'")
        
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

def start_consumer():
    """Inicia el consumidor de RabbitMQ"""
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    # Declarar exchanges
    channel.exchange_declare(exchange='looking-for', exchange_type='fanout', durable=True)
    channel.exchange_declare(exchange='results', exchange_type='fanout', durable=True)
    
    # Crear cola exclusiva y temporal
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    
    # Vincular cola al exchange 'looking-for'
    channel.queue_bind(exchange='looking-for', queue=queue_name)
    
    print(f"Esperando mensajes en exchange 'looking-for'...")
    print(f"Cola: {queue_name}")
    
    # Consumir mensajes
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Deteniendo consumidor...")
        channel.stop_consuming()
    
    connection.close()

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de salud"""
    return {"status": "healthy", "service": "education-svc"}, 200

if __name__ == '__main__':
    # Iniciar consumidor en un thread separado
    import threading
    consumer_thread = threading.Thread(target=start_consumer, daemon=True)
    consumer_thread.start()
    
    # Iniciar Flask
    app.run(host='0.0.0.0', port=5000, debug=False)