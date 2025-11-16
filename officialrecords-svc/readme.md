# OfficialRecords Service

Servicio que busca información de registros oficiales de personas en una base de datos en memoria.

## Flujo

1. **Consume** mensajes desde el exchange `looking-for` (publicados por `query-svc`)
2. **Busca** la persona en la BD de registros oficiales
3. **Publica** el resultado en el exchange `results` con:
   - `id`: identificador de la persona
   - `status`: `"found"` o `"not_found"`
   - `record`: número / descripción del registro
   - `record_status`: estado del registro (Activo, Válido, etc)
   - `service`: `"officialrecords"`

## Base de datos en memoria

```json
[
  {"id": "12345", "name": "Juan Perez", "phone": "555-1234", "record": "Cédula #12345-678", "status_record": "Activo"},
  {"id": "67890", "name": "Maria Garcia", "phone": "555-5678", "record": "Pasaporte #PE-9876543", "status_record": "Válido"},
  {"id": "11111", "name": "Carlos Lopez", "phone": "555-9999", "record": "Licencia de conducir #LIC-11111", "status_record": "Válido"},
]
```

## Ejemplo de mensaje enviado (para dashboard)

Si encontrado:
```json
{
  "id": "12345",
  "status": "found",
  "record": "Cédula #12345-678",
  "record_status": "Activo",
  "service": "officialrecords"
}
```

Si no encontrado:
```json
{
  "id": "12345",
  "status": "not_found",
  "record": null,
  "record_status": null,
  "service": "officialrecords"
}
```

## Ejecución

```bash
docker build -t officialrecords-svc .
docker run --network <docker-network> officialrecords-svc
```

Asegúrate de que está en la misma red que `rabbitmq` y otros servicios.
