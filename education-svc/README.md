# Education Service (education-svc)

Microservicio que busca información educativa de una persona (universidades, títulos académicos).

## Descripción

Este servicio:
1. Escucha en el exchange `looking-for` por consultas de personas
2. Busca en su base de datos en memoria información educativa
3. Publica los resultados en el exchange `results`

## Base de Datos

La BD en memoria contiene 4 registros con:
- `id`: Identificador de la persona
- `name`: Nombre completo
- `university`: Universidad donde estudió
- `degree`: Título académico obtenido

## Formato de Resultado

```json
{
  "id": "12345",
  "status": "found",
  "university": "Universidad Nacional",
  "degree": "Ingeniería de Sistemas",
  "service": "education"
}
```

Si no se encuentra información:
```json
{
  "id": "12345",
  "status": "not_found",
  "university": null,
  "degree": null,
  "service": "education"
}
```

## Endpoints

- `GET /health`: Verifica el estado del servicio

## RabbitMQ

- **Consume de**: Exchange `looking-for` (fanout)
- **Publica en**: Exchange `results` (fanout)

## Ejecución

Este servicio se levanta automáticamente con `docker-compose up --build`