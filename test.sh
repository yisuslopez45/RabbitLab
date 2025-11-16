#!/bin/bash

# Script de prueba rápida del sistema RabbitLab

echo "🚀 RabbitLab - Script de Prueba"
echo "================================"
echo ""

# Verificar que los servicios están levantados
echo "1️⃣ Verificando salud de servicios..."
echo ""

echo "   ➜ query-svc..."
curl -s http://localhost:5000/health && echo " ✓" || echo " ✗"

echo "   ➜ dashboard-svc..."
curl -s http://localhost:5001/health && echo " ✓" || echo " ✗"

echo ""
echo "2️⃣ Enviando consulta de prueba..."
echo ""

QUERY=$(cat <<EOF
{
  "name": "Juan Perez",
  "id": "12345",
  "phone": "555-1234"
}
EOF
)

echo "   Enviando: $QUERY"
echo ""

curl -X POST http://localhost:5000/query \
  -H "Content-Type: application/json" \
  -d "$QUERY" \
  -s

echo ""
echo ""
echo "3️⃣ Esperando respuestas de servicios (3 segundos)..."
sleep 3

echo ""
echo "4️⃣ Resultados en JSON:"
echo ""

curl -s http://localhost:5001/api/results | jq . 2>/dev/null || curl -s http://localhost:5001/api/results

echo ""
echo ""
echo "5️⃣ Para ver visualización HTML:"
echo "   📊 Abre: http://localhost:5001/viewresults"
echo ""
echo "6️⃣ Para ver RabbitMQ Management:"
echo "   🐰 Abre: http://localhost:15672 (guest/guest)"
echo ""
