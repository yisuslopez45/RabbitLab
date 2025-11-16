# CommercialInfo Service

Servicio que busca información de empleados en una base de datos en memoria.

## Flujo

1. **Consume** mensajes desde el exchange `looking-for` (publicados por `query-svc`)
2. **Busca** la persona en una base de datos en memoria (array JSON)
3. **Publica** el resultado en el exchange `results` con:
   - `id`: identificador de la persona
   - `status`: `"found"` o `"not_found"`
   - `workplace`: sitio de trabajo (o `null` si no encontrado)

## Base de datos en memoria

```json
[
  {"id": "12345", "name": "Juan Perez", "phone": "555-1234", "workplace": "Google"},
  {"id": "67890", "name": "Maria Garcia", "phone": "555-5678", "workplace": "Microsoft"},
  {"id": "11111", "name": "Carlos Lopez", "phone": "555-9999", "workplace": "Amazon"},
  {"id": "22222", "name": "Ana Martinez", "phone": "555-8888", "workplace": null}
]
```

## Ejemplo de mensaje recibido (desde query-svc)

```json
{
  "name": "Juan Perez",
  "id": "12345",
  "phone": "555-1234"
}
```

## Ejemplo de mensaje enviado (para dashboard)

Si encontrado:
```json
{
  "id": "12345",
  "status": "found",
  "workplace": "Google"
}
```

Si no encontrado:
```json
{
  "id": "12345",
  "status": "not_found",
  "workplace": null
}
```


