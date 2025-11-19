# Financial Service

Microservicio que busca información financiera de personas en el sistema RabbitLab.

## Propósito

Busca información de cuentas bancarias, puntaje crediticio y estado financiero de las personas consultadas.

## Base de Datos en Memoria

Contiene 4 registros de ejemplo con la siguiente estructura:

- `id`: Identificación de la persona
- `name`: Nombre completo
- `bank`: Nombre del banco
- `account_type`: Tipo de cuenta (Ahorros/Corriente)
- `credit_score`: Puntaje crediticio (0-850)
- `status`: Estado de la cuenta (Activo/Suspendido)

## Funcionamiento

1. **Escucha** el exchange `looking-for` (fanout)
2. **Busca** en la BD en memoria por el campo `id`
3. **Publica** resultado en exchange `results` (fanout)

## Formato de Respuesta

### Cuando encuentra información:

```json
{
  "id": "12345",
  "status": "found",
  "bank": "Banco de Bogotá",
  "account_type": "Cuenta de Ahorros",
  "credit_score": 750,
  "account_status": "Activo",
  "service": "financial"
}
```

### Cuando NO encuentra información:

```json
{
  "id": "99999",
  "status": "not_found",
  "bank": null,
  "account_type": null,
  "credit_score": null,
  "account_status": null,
  "service": "financial"
}
```

## Ejecución

### Con Docker Compose (Recomendado)

El servicio se levanta automáticamente con:

```bash
docker-compose up --build
```

### Standalone (sin Docker)

```bash
cd financial-svc
pip install pika
python app.py
```

**Nota**: Asegúrate de que RabbitMQ esté corriendo en `localhost:5672`

## Logs

El servicio genera logs con formato:

```
[2025-11-18 10:30:45] [INFO] [Financial] Financial service conectado a RabbitMQ
[2025-11-18 10:31:12] [INFO] [Financial] Query recibida: {'id': '12345', 'name': 'Juan Perez'}
[2025-11-18 10:31:12] [INFO] [Financial] Información financiera encontrada para ID=12345: Banco de Bogotá
```

## Integración

Este servicio se integra automáticamente con:

- **query-svc**: Recibe queries de búsqueda
- **dashboard-svc**: Envía resultados para visualización
- **RabbitMQ**: Usa exchanges `looking-for` y `results`
