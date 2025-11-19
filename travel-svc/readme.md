# Travel Service 🛫

Microservicio que busca información de historial de viajes y visas de una persona.

## Descripción

Este servicio forma parte de la arquitectura de microservicios de RabbitLab y se encarga de:
- Buscar registros de viajes internacionales
- Consultar información de visas
- Registrar el historial de entradas a diferentes países

## Flujo de trabajo

1. **Recibe** consultas del exchange `looking-for`
2. **Busca** en la base de datos en memoria usando el ID de la persona
3. **Publica** resultados en el exchange `results`

## Base de datos en memoria

Contiene 4 registros de prueba con la siguiente estructura:

```python
{
    "id": "12345",
    "name": "Juan Perez",
    "destination": "Estados Unidos",
    "visa_type": "Turista B2",
    "visa_status": "Activa",
    "last_travel_date": "2024-08-15",
    "entry_count": 3
}
```

### Datos de prueba disponibles:

- **ID: 12345** - Juan Perez → Visa USA Turista B2 (Activa)
- **ID: 67890** - Maria Garcia → Visa Schengen España (Vigente)
- **ID: 11111** - Carlos Lopez → Visa Canadá (Expirada)
- **ID: 22222** - Ana Martinez → México - No requiere visa

## Formato de respuesta

### Cuando se encuentra información:
```json
{
    "id": "12345",
    "status": "found",
    "destination": "Estados Unidos",
    "visa_type": "Turista B2",
    "visa_status": "Activa",
    "last_travel": "2024-08-15",
    "entry_count": 3,
    "service": "travel"
}
```

### Cuando NO se encuentra información:
```json
{
    "id": "99999",
    "status": "not_found",
    "message": "No travel records found",
    "service": "travel"
}
```

## Ejecución

```bash
docker build -t socialmedia-svc .
docker run --network <docker-network> socialmedia-svc
```

Asegúrate de que está en la misma red que `rabbitmq` y otros servicios.
