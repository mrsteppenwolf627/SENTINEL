# 🛡️ Sentinel

**Tu Agente Autónomo de Infraestructura (MVP v1.0)**

> *Un sistema inteligente que vigila tus servidores, diagnostica problemas y los arregla antes de que te despierten a las 3 A.M.*

---

## 🌟 ¿Qué es Sentinel?

Sentinel es un "guardián digital" para sistemas informáticos. Imagina que tienes un ingeniero experto monitoreando tus servidores las 24 horas del día, listo para actuar en milisegundos si algo falla. Eso es Sentinel.

En esta versión MVP (Producto Mínimo Viable), Sentinel puede:
1.  **Escuchar**: Detecta alertas simuladas como "CPU al 100%" o "Disco lleno".
2.  **Pensar**: Analiza por qué ocurrió el problema usando un motor de reglas lógico.
3.  **Decidir**: Evalúa si es peligroso actuar automáticamente o si debe pedir permiso humano.
4.  **Actuar**: Ejecuta la solución (reiniciar un servicio, borrar caché, etc.).
5.  **Recordar**: Guarda un registro auditor de todo lo que hizo.

---

## 🚀 Guía Rápida para "No Expertos"

Si solo quieres ver cómo funciona la magia:

1.  **Instala los requisitos**: Asegúrate de tener Python instalado.
    ```bash
    pip install -r requirements.txt
    ```
2.  **Enciende a Sentinel**:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  **Observa**: 
    Abre tu navegador en `http://127.0.0.1:8000/audit`. Verás una lista en vivo de problemas que aparecen y cómo Sentinel los resuelve.

---

## 🔧 Documentación Técnica

Para desarrolladores e ingenieros que quieran extender el sistema.

### Arquitectura Modular
Sentinel no es un script monolítico; es un sistema modular diseñado para crecer.

*   **Ingestion (`app/modules/ingestion`)**: 
    *   Actualmente: Un simulador (`AlertSimulator`) que genera ruido estocástico.
    *   Futuro: Webhooks para Prometheus, Datadog, AWS CloudWatch.
*   **Analysis (`app/modules/analysis`)**:
    *   Actualmente: Motor de reglas determinista (`RuleBasedAnalyzer`).
    *   Futuro: Integración con LLMs (OpenAI/DeepSeek) para Root Cause Analysis (RCA) semántico.
*   **Policy (`app/modules/policy`)**:
    *   Matriz de riesgo configurable. Decide si una acción es `SAFE` (auto-ejecutable) o `CRITICAL` (requiere aprobación).
*   **Action (`app/modules/action`)**:
    *   Ejecutores abstractos. En este MVP, las acciones son "mockeadas" (logs) por seguridad.

### Stack Tecnológico
*   **Lenguaje**: Python 3.14+
*   **API Framework**: FastAPI (Asynchronous)
*   **Logging**: Estructurado (JSON) con `python-json-logger`
*   **Tests**: Pytest + Pytest-Asyncio

### Estructura de Carpetas
```text
Sentinel/
├── app/
│   ├── core/           # Definiciones de dominio (Entidades, Interfaces)
│   ├── modules/        # Implementación de lógica (La "carne" del sistema)
│   └── main.py         # Orquestador principal
├── SENTINEL_DOCUMENTATION.md # Documentación profunda del proyecto
└── audit.log           # Historial de decisiones (JSONL)
```

---

## 🔮 El Futuro (Roadmap)

Este repositorio (`Sentinel_MPV_V1`) es la base fundacional. Las próximas versiones incluirán:
*   [ ] Conexión real a servidores vía SSH/Ansible.
*   [ ] "Cerebro" basado en IA para entender logs complejos.
*   [ ] Interfaz gráfica (Dashboard) en React.
*   [ ] Base de datos persistente (PostgreSQL).

---
*Hecho con ❤️ y Python.*
