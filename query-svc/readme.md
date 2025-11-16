# Query Service (query-svc)

Punto de entrada de la arquitectura RabbitLab. Recibe consultas de búsqueda de personas y las publica en el exchange `looking-for` de RabbitMQ para que otros servicios las procesen.

## Propósito

El servicio `query-svc` actúa como API REST que:
1. **Recibe** solicitudes HTTP POST con datos de la persona a buscar
2. **Valida** que al menos uno de los campos esté presente (name, id, phone)
3. **Publica** el mensaje en RabbitMQ exchange `looking-for` (fanout)
4. **Retorna** confirmación del envío

Los otros servicios (`commercialinfo-svc`, `socialmedia-svc`, `officialrecords-svc`) consumen estos mensajes de forma independiente.

## Stack Técnico

- **Framework**: Flask (Python)
- **Message Broker**: RabbitMQ
- **Protocolo**: HTTP REST
- **Puerto**: 5000

## Endpoints

### `GET /health`

Verifica el estado del servicio.

**Respuesta**: `OK`
**Código**: 200

---

### `POST /query`

Envía una consulta para buscar información de una persona.

**Content-Type**: `application/json`

**Body** (requerido):
```json
{
  "name": "Juan Perez",
  "id": "12345",
  "phone": "555-1234"
}
```

**Campos**:
- `name` (string, opcional): Nombre de la persona
- `id` (string, opcional): Identificador único
- `phone` (string, opcional): Número de teléfono

**Requerimiento**: Al menos uno de los campos debe estar presente.

**Respuesta exitosa** (200):
```json
{
  "status": "Query initiated"
}
```

---

## Ejemplos de Uso

### Con cURL

```bash
# Búsqueda combinada (recomendado)
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"name":"Juan Perez","id":"12345","phone":"555-1234"}'

# Ver estado del servicio
curl http://localhost:5000/health
```


## Flujo de Integración

```
Cliente (POST /query)
    ↓
query-svc (valida + publica en 'looking-for')
    ↓
exchange 'looking-for' (fanout)
    ├─→ commercialinfo-svc
    ├─→ socialmedia-svc
    └─→ officialrecords-svc
    
    ↓ (cada uno publica en 'results')
    
exchange 'results'
    ↓
dashboard-svc (agrega resultados)
```


---

## Notas Importantes

1. **Dependencia de RabbitMQ**: Requiere RabbitMQ accesible en host `rabbitmq`
2. **Exchange fanout**: El mensaje se publica a todos los consumidores conectados
3. **Validación mínima**: Solo valida que al menos uno de los 3 campos esté presente
4. **Reintentos**: Si RabbitMQ no está disponible, reintentar cada 5 segundos

---

