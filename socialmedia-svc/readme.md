# SocialMedia Service

Servicio que busca información de redes sociales de personas en una base de datos en memoria.

## Flujo

1. **Consume** mensajes desde el exchange `looking-for` (publicados por `query-svc`)
2. **Busca** la persona en la BD de perfiles de redes sociales
3. **Publica** el resultado en el exchange `results` con:
   - `id`: identificador de la persona
   - `status`: `"found"` o `"not_found"`
   - `profile`: nombre de usuario / perfil
   - `platform`: plataforma (Twitter, Instagram, Facebook)
   - `service`: `"socialmedia"`

## Base de datos en memoria

```json
[
  {"id": "12345", "name": "Juan Perez", "phone": "555-1234", "profile": "@juanperez", "platform": "Twitter"},
  {"id": "67890", "name": "Maria Garcia", "phone": "555-5678", "profile": "maria.garcia", "platform": "Instagram"},
  {"id": "11111", "name": "Carlos Lopez", "phone": "555-9999", "profile": "clopez88", "platform": "Facebook"},
]
```

## Ejemplo de mensaje enviado (para dashboard)

Si encontrado:
```json
{
  "id": "12345",
  "status": "found",
  "profile": "@juanperez",
  "platform": "Twitter",
  "service": "socialmedia"
}
```

Si no encontrado:
```json
{
  "id": "12345",
  "status": "not_found",
  "profile": null,
  "platform": null,
  "service": "socialmedia"
}
```

## Ejecución

```bash
docker build -t socialmedia-svc .
docker run --network <docker-network> socialmedia-svc
```

Asegúrate de que está en la misma red que `rabbitmq` y otros servicios.
