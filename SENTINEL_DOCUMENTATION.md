# 🛡️ Sentinel - Sistema de Agente Autónomo de Infraestructura

**Versión:** MVP 1.0  
**Fecha:** 5 de Febrero, 2026

---

## 📖 Introducción y Visión

**Sentinel** es un sistema de agente autónomo diseñado para la gestión y auto-remediación de incidentes de infraestructura. Su objetivo es recibir alertas, diagnosticar causas raíz, evaluar riesgos y ejecutar acciones correctivas automáticamente o solicitar aprobación humana cuando sea necesario.

**Visión a Futuro:**  
Este MVP es la semilla de un **SaaS de Observabilidad y Remediación Autónoma** a escala global. El objetivo final es integrar LLMs avanzados para diagnósticos complejos y conectores reales con nubes (AWS, Azure, GCP), Kubernetes y sistemas legacy.

---

## 🏗️ Arquitectura y Estructura del Proyecto

El sistema sigue una **Arquitectura Modular Estricta** para garantizar que cada componente sea reemplazable (ej. cambiar el motor de reglas por un LLM sin tocar el resto del sistema).

### Árbol de Directorios
```text
Sentinel/
├── app/
│   ├── main.py              # 🚀 Punto de entrada (API FastAPI y Loop de control)
│   ├── core/                # 🧠 Cerebro y Contratos
│   │   ├── entities.py      # Modelos de dominio (Alert, Diagnosis, Plan)
│   │   ├── interfaces.py    # Interfaces base (Abstract Base Classes)
│   │   ├── config.py        # Configuración global (Variables de entorno)
│   │   └── logging.py       # Logger estructurado (JSON)
│   ├── modules/             # 🧩 Piezas funcionales
│   │   ├── ingestion/       # Entrada de datos (Simulador de Alertas)
│   │   ├── analysis/        # Diagnóstico (Motor de Reglas)
│   │   ├── policy/          # Evaluación de Riesgos (Matriz de Riesgo)
│   │   ├── action/          # Ejecución (Mock SSH/API)
│   │   └── audit/           # Trazabilidad (Logs JSONL)
│   └── tests/               # 🧪 Tests automatizados (Unitarios e Integración)
├── requirements.txt         # Dependencias
├── SENTINEL_DOCUMENTATION.md # 📄 Este documento
└── README.md                # Instrucciones rápidas
```

### Flujo de Datos (Pipeline)
El sistema opera en un bucle continuo (`processing_loop` en `main.py`):

1.  **Ingestion**: `AlertSimulator` genera una alerta simulada (ej. "High CPU").
2.  **Analysis**: `RuleBasedAnalyzer` recibe la alerta y busca una regla coincidente para emitir un `Diagnosis`.
3.  **Policy**: `RiskEvaluator` toma el diagnóstico, evalúa la acción sugerida y decide el `RiskLevel` (SAFE, CRITICAL) y si requiere aprobación.
4.  **Action**: `ActionExecutor` intenta ejecutar la acción si está aprobada. En el MVP, esto es una simulación (log).
5.  **Audit**: `AuditService` registra todo el evento con detalles completos en `audit.log`.

---

## 🛠️ Cómo Funciona y Se Ejecuta

### Requisitos Previos
- Python 3.11+
- Pip

### Instalación
```bash
# Activar entorno virtual (opcional pero recomendado)
./.venv/Scripts/Activate.ps1

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución del Agente
```bash
# Iniciar el servidor y el agente en segundo plano
uvicorn app.main:app --reload
```
Una vez iniciado, el sistema comenzará a procesar alertas simuladas automáticamente cada 5 segundos.

### Verificación
1.  **Dashboard de Auditoría**: Abre tu navegador en `http://127.0.0.1:8000/audit` para ver las decisiones del agente en tiempo real.
2.  **Simulación Manual**: Puedes enviar una alerta custom vía API:
    ```bash
    curl -X POST http://127.0.0.1:8000/simulate \
    -H "Content-Type: application/json" \
    -d '{"source": "test", "severity": "CRITICAL", "message": "Database down", "metadata": {}}'
    ```

### Ejecutar Tests
```bash
pytest
```

---

## 🛣️ Roadmap y Estado del Proyecto

### ✅ Fase 1: MVP (Completado)
*   [x] **Estructura Base**: Configuración de entorno, Git, y Logging estructurado.
*   [x] **Ingestión**: Simulador de alertas de CPU, Memoria y Disco.
*   [x] **Análisis**: Motor de reglas determinista (If/Else logic).
*   [x] **Políticas**: Lógica de "Semáforo" de riesgo (Safe/Moderate/Critical).
*   [x] **Acción**: Ejecutor mockeado (simula reinicios y escalados).
*   [x] **Auditoría**: Persistencia en archivo `audit.log`.
*   [x] **Orquestación**: Loop asíncrono en background con FastAPI.
*   [x] **UI**: Visor básico de logs HTML.
*   [x] **Documentación**: Creación de este documento maestro.

### 🚀 Fase 2: Futuro (SaaS Vision)
*   [ ] **Persistencia Real**: Migrar SQLite/JSONL a PostgreSQL.
*   [ ] **Análisis IA**: Reemplazar `RuleBasedAnalyzer` con integración OpenAI/Claude para RCAs complejos.
*   [ ] **Conectores Reales**: Integraciones con AWS CloudWatch, Datadog y Kubernetes API.
*   [ ] **Dashboard React**: Interfaz profesional para gestión de incidentes y aprobación manual.
*   [ ] **Autenticación**: Multi-tenant support para clientes SaaS.

---

## 💡 Guía para Desarrolladores / LLMs

*   **Extensibilidad**: Para añadir una nueva fuente de alertas, implementa `IIngestionModule` en `app/modules/ingestion`.
*   **Reglas**: Añade nuevas reglas de detección en `app/modules/analysis/rules.py`.
*   **Riesgo**: Modifica la matriz de riesgo en `app/modules/policy/risk_manager.py`.
*   **Logging**: Siempre usa `logger.info(msg, extra={...})` pasando diccionarios en `extra` para mantener la estructura JSON.

---
*Documento generado automáticamente por Sentinel AI Assistant.*
