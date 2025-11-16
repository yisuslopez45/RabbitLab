# Dashboard Service

Servicio Flask que agrega y visualiza resultados de búsqueda desde múltiples servicios.

## Características

- **Consumer de RabbitMQ**: Escucha en el exchange `results` (fanout)
- **Almacenamiento en memoria**: Diccionario que agrupa resultados por query_id
- **Thread-safe**: Usa locks para acceso concurrente
- **HTML dinámico**: Renderiza resultados con plantilla Jinja2
- **API JSON**: Endpoints para obtener resultados en JSON

## Endpoints

### `/health`
Estado del servicio.

### `/viewresults`
Página HTML que muestra todas las consultas y sus resultados de cada servicio (comercialinfo, socialmedia, officialrecords).

### `/api/results`
Retorna todos los resultados en JSON.

### `/api/results/<query_id>`
Retorna resultados de una query específica en JSON.

## Flujo

```
commercialinfo-svc   ┐
socialmedia-svc      ├─→ exchange 'results' (fanout) ─→ dashboard-svc
officialrecords-svc  ┘
                          ↓
                    (en memoria: diccionario)
                          ↓
                    GET /viewresults
                          ↓
                    HTML renderizado
```

## Estructura de datos en memoria

```python
{
  "12345": {
    "commercialinfo": {
      "id": "12345",
      "status": "found",
      "workplace": "Google",
      "service": "commercialinfo"
    },
    "socialmedia": {
      "id": "12345",
      "status": "found",
      "profile": "@juanperez",
      "service": "socialmedia"
    },
    "officialrecords": {
      "id": "12345",
      "status": "found",
      "record": "Registro Civil #XYZ",
      "service": "officialrecords"
    }
  }
}
```

## Ejecución

```bash
docker build -t dashboard-svc .
docker run -p 5001:5001 --network <docker-network> dashboard-svc
```

Luego accede a `http://localhost:5001/viewresults`

## Notas

- Los resultados se almacenan en memoria (se pierden al reiniciar)
- Los servicios deben incluir el campo `service` en el JSON que publican para identificarse
- El campo `id` debe estar presente para agrupar resultados por query
