# RabbitLab - Arquitectura de Microservicios con RabbitMQ

Ejercicio académico que implementa una arquitectura de microservicios para contruir un software de investigacion para el rastreo de la huella diguital de una persona.

## Arquitectura

```
query-svc
   │ (POST /query con {name, id, phone})
   │
   ↓
exchange 'looking-for' (fanout)
   │
   ├─→ commercialinfo-svc (busca en BD de empleos)
   ├─→ socialmedia-svc (busca en BD de redes sociales)
   ├─→ officialrecords-svc (busca en BD de registros)
   └─→ financial-svc (busca en BD de información financiera)
   └─→ travel-svc (busca en BD de viajes)

   ↓ (cada uno publica resultados)

exchange 'results' (fanout)
   │
   ↓
dashboard-svc (Flask)
   │
   ├─→ /health (estado del servicio)
   ├─→ /viewresults (visualización HTML de resultados)
   └─→ /api/results (API JSON)
```

## Servicios

### 1. **query-svc** (Puerto 5000)

- **Propósito**: Punto de entrada para realizar consultas
- **Endpoint**: `POST /query`
- **Body**:
  ```json
  {
    "name": "Juan Perez",
    "id": "12345",
    "phone": "555-1234"
  }
  ```
- **Acción**: Publica en exchange `looking-for`

### 2. **commercialinfo-svc**

- **Propósito**: Busca información de empleos/trabajo
- **BD en memoria**: 4 registros con id, name, workplace
- **Resultado**: `{id, status, workplace, service}`

### 3. **socialmedia-svc**

- **Propósito**: Busca perfiles en redes sociales
- **BD en memoria**: 3 registros con id, name, profile, platform
- **Resultado**: `{id, status, profile, platform, service}`

### 4. **officialrecords-svc**

- **Propósito**: Busca registros oficiales (cédula, pasaporte, etc)
- **BD en memoria**: 3 registros con id, name, record, status_record
- **Resultado**: `{id, status, record, record_status, service}`

### 5. **financial-svc**

- **Propósito**: Busca información financiera (cuentas bancarias, créditos)
- **BD en memoria**: 4 registros con id, name, bank, account_type, credit_score, status
- **Resultado**: `{id, status, bank, account_type, credit_score, account_status, service}`


### 5. **travel-svc** ✈️ NUEVO
- **Propósito**: Busca historial de viajes y visas
- **BD en memoria**: 4 registros con id, name, destination, visa_type, visa_status, last_travel_date, entry_count
- **Resultado**: `{id, status, destination, visa_type, visa_status, last_travel, entry_count, service}`

### 6. **dashboard-svc** (Puerto 5001)
- **Propósito**: Agrega resultados y visualiza
- **Endpoints**:
  - `GET /health`: Estado
  - `GET /viewresults`: HTML con resultados (recarga dinámica)
  - `GET /api/results`: JSON con todos los resultados
  - `GET /api/results/<query_id>`: JSON de una query específica

## Inicio Rápido

### Con Docker Compose (recomendado)

```bash
cd /home/morfeo/Documentos/Semestre/Desarollo/RabbitLab

# Construir todas las imágenes y levantar servicios
docker-compose up --build

# En otra terminal:
# 1. Consultar una persona
curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d '{"name":"Juan Perez","id":"12345","phone":"555-1234"}'

# 2. Esperar 2-3 segundos y ver resultados en:
#    - HTML: http://localhost:5001/viewresults
#    - JSON: http://localhost:5001/api/results

# Ver RabbitMQ Management (opcional):
#    http://localhost:15672 (user: guest, pass: guest)

# Detener servicios
docker-compose down
```

## Flujo de Ejecución

1. **Enviar consulta** → `POST /query` en query-svc
2. **Publicación** → Query se publica en exchange `looking-for`
3. **Consumo** → Los cuatro servicios (commercialinfo, socialmedia, officialrecords, financial) reciben el mensaje
4. **Búsqueda** → Cada servicio busca en su BD en memoria
5. **Publicación de resultados** → Cada servicio publica su resultado en exchange `results`
6. **Agregación** → Dashboard consume y almacena resultados en diccionario
7. **Visualización** → Acceder a `/viewresults` para ver HTML o `/api/results` para JSON

## Ejemplo de Datos

### Entrada (query-svc POST)

```json
{
  "name": "Juan Perez",
  "id": "12345",
  "phone": "555-1234"
}
```

### Salidas (cada servicio)

**commercialinfo-svc**:

```json
{
  "id": "12345",
  "status": "found",
  "workplace": "Google",
  "service": "commercialinfo"
}
```

**socialmedia-svc**:

```json
{
  "id": "12345",
  "status": "found",
  "profile": "@juanperez",
  "platform": "Twitter",
  "service": "socialmedia"
}
```

**officialrecords-svc**:

```json
{
  "id": "12345",
  "status": "found",
  "record": "Cédula #12345-678",
  "record_status": "Activo",
  "service": "officialrecords"
}
```
**travel-svc**:
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

**financial-svc**:

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

### En Dashboard (/viewresults)

Se agrupa por query_id y se muestran los 4 servicios con sus resultados.

## Estructura de Directorios

```
RabbitLab/
├── query-svc/
│   ├── app.py
│   ├── Dockerfile
│   └── readme.md
├── comercialinfo-scv/
│   ├── app.py
│   ├── Dockerfile
│   └── readme.md
├── socialmedia-svc/
│   ├── app.py
│   ├── Dockerfile
│   └── readme.md
├── officialrecords-svc/
│   ├── app.py
│   ├── Dockerfile
│   └── readme.md
├── financial-svc/
├── travel-svc/
│   ├── app.py
│   ├── Dockerfile
│   └── readme.md
├── dashboard-svc/
│   ├── app.py
│   ├── templates/
│   │   └── results.html
│   ├── Dockerfile
│   └── readme.md
├── docker-compose.yml
└── README.md (este archivo)
```

## Notas Importantes

- Todos los servicios usan **exchanges fanout** (cada consumer recibe todas las publicaciones)
- Las colas son **exclusivas** por cada consumer (se crean temporalmente)
- Las BD están **en memoria** (se pierden al reiniciar)
- El dashboard usa **diccionario en memoria** (resultados se pierden al reiniciar)
- El access a `results_dict` es **thread-safe** (usa locks)
- Cada servicio identifica su origen con el campo `service` en el JSON publicado

**Autor**: Bayron Jojoa - RabbitLab
