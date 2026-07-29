# Bitácora de desarrollo — Voice Command API

28-07-2026-19:40

## Objetivo del proyecto

Construir una API backend que permita gestionar una lista de tareas mediante comandos de voz.

El flujo esperado es:

Usuario habla → Frontend convierte voz a texto → Backend recibe la transcripción → Groq interpreta la intención → Backend devuelve qué endpoint ejecutar → Frontend ejecuta la acción sobre las tareas.

La API debe permitir:

- Crear tareas.
- Listar tareas.
- Actualizar tareas.
- Completar tareas.
- Eliminar tareas.

El almacenamiento será únicamente en memoria utilizando una lista de Python. No se utilizará base de datos.

---

## Fase 1 — Preparación del entorno

## Creación del entorno virtual

Se creó un entorno virtual para aislar las dependencias del proyecto.

### ¿Por qué?

Un entorno virtual permite que las librerías utilizadas por este proyecto no afecten otros proyectos de Python instalados en el equipo.

Cada proyecto puede tener versiones diferentes de sus dependencias sin generar conflictos.

---

## Gestión de dependencias con UV

El proyecto utiliza `uv` como gestor de dependencias.

Se detectaron los archivos:

- `pyproject.toml`
- `uv.lock`

Estos archivos indican que el proyecto está preparado para trabajar con UV.

Se ejecutó:

```bash
uv sync
```

### ¿Qué hace?

UV lee las dependencias declaradas en `pyproject.toml` y prepara el entorno con las versiones exactas definidas.

Esto garantiza que todos los desarrolladores trabajen con las mismas versiones de librerías.

Dependencias principales:

- FastAPI → Framework para construir la API.
- Uvicorn → Servidor ASGI para ejecutar FastAPI.
- Groq SDK → Comunicación con el modelo de IA.
- python-dotenv → Lectura de variables desde archivos `.env`.
- pydantic-settings → Gestión de configuración.

---

## Variables de entorno

Se creó un archivo:

```bash
.env
```

Este archivo permanecerá fuera del control de versiones.

Su función será almacenar información sensible como: GROQ_API_KEY

## ¿Por qué no se sube `.env`?

Las claves privadas nunca deben almacenarse en Git.

Si una API Key se sube a un repositorio público, cualquier persona podría utilizarla y generar consumo en nuestra cuenta.

---

## Archivo .env.example

Se creó:

```bash
.env.example
```

Este archivo sirve como plantilla para otros desarrolladores.

Ejemplo: GROQ_API_KEY=Aqui tu api de Groq

Contiene solamente los nombres de las variables necesarias, pero nunca sus valores reales.

---

## Configuración de Git

Se creó o configuró:

```bash
.gitignore
```

Incluyendo archivos que no deben ser versionados:

```text
.env
.venv/
pycache/
*.pyc
```

## ¿Por qué?

Git debe almacenar únicamente código y archivos necesarios para reconstruir el proyecto.

Archivos temporales, entornos virtuales y secretos deben permanecer únicamente en la máquina local.

---

## Fase 2 — Organización del proyecto

Se creó una carpeta principal:

```text
app/
```

Esta carpeta contiene el código fuente del backend.

La estructura inicial:

app/
├── init.py
├── main.py
├── config.py
├── models.py
├── routes.py
└── storage.py

---

## Separación de responsabilidades

La aplicación se divide en módulos para evitar mezclar responsabilidades.

## main.py

Responsabilidad:

- Crear la aplicación FastAPI.
- Configurar elementos generales.
- Registrar rutas.

No debe contener lógica de negocio.

---

## config.py

Responsabilidad:

- Leer variables de entorno.
- Gestionar configuración del proyecto.

Ejemplo:

- API Key de Groq.
- Configuraciones generales.

---

## models.py

Responsabilidad:

Definir la estructura de los datos.

Ejemplo conceptual:

Una tarea contiene:
id
title
done

Este archivo describe cómo debe ser una tarea, pero no almacena tareas.

---

## storage.py

Responsabilidad:

Mantener el almacenamiento temporal de la aplicación.

El proyecto requiere una lista en memoria:

```bash
tasks = []
```

Esta lista será reiniciada cada vez que el servidor se reinicie.

No se utiliza base de datos porque el objetivo del ejercicio es aprender la comunicación entre API, frontend y modelo de IA.

---

## routes.py

Responsabilidad:

Contener los endpoints de la API.

Aquí estarán:
GET /tasks
POST /tasks
PUT /tasks/{id}
PATCH /tasks/{id}
DELETE /tasks/{id}

POST /instruction

---

## Decisiones tomadas

## No crear una arquitectura demasiado compleja

Aunque existen estructuras más avanzadas con:

routers/
services/
repositories/
schemas/
database/

para este proyecto se decidió mantener una estructura simple.

Motivo:

El objetivo principal es comprender:

- FastAPI.
- APIs REST.
- Modelos Pydantic.
- Variables de entorno.
- Integración con un LLM.

La complejidad arquitectónica se añadirá en proyectos futuros.

## Fase 3 — Primera API funcional

Durante esta fase se comenzó la construcción del backend siguiendo una arquitectura modular. El objetivo fue comprender la responsabilidad de cada archivo antes de implementar toda la lógica de negocio.

---

## Creación de la aplicación FastAPI

En `main.py` se creó la aplicación principal.

Responsabilidades de este archivo:

- Crear la instancia de FastAPI.
- Configurar la aplicación.
- Registrar los routers.
- Iniciar la API.

Se añadió un endpoint de prueba:

```text
GET /
```

Su única finalidad es verificar que el servidor funciona correctamente.

Respuesta:

```json
{
    "message": "Voice Command API running"
}
```

---

## Ejecución del servidor

La aplicación se ejecuta mediante Uvicorn utilizando UV:

```bash
uv run uvicorn app.main:app --reload
```

Desglose del comando:

- `uv run` ejecuta el comando dentro del entorno administrado por UV.
- `uvicorn` inicia el servidor ASGI.
- `app.main:app` indica dónde se encuentra la aplicación.
- `--reload` reinicia automáticamente el servidor cuando se detectan cambios en el código.

---

## Documentación automática

FastAPI genera automáticamente una documentación interactiva disponible en:

```text
http://127.0.0.1:8000/docs
```

Desde esta interfaz es posible:

- visualizar todos los endpoints;
- probar la API sin utilizar Postman;
- conocer los modelos de entrada y salida;
- inspeccionar los códigos de respuesta HTTP.

---

## Configuración de CORS

Se añadió el middleware CORS para permitir que el frontend pueda comunicarse con la API.

Conceptualmente, CORS actúa como una política de seguridad del navegador que controla qué aplicaciones web tienen permiso para realizar peticiones al backend.

El flujo de una petición queda de la siguiente forma:

```text
Frontend
    │
    ▼
CORS Middleware
    │
¿Origen permitido?
    │
 ┌──Sí──────────────┐
 ▼                  ▼
Endpoint         Navegador bloquea
```

Durante el desarrollo únicamente se permiten los orígenes necesarios para el frontend local.

---

## Organización mediante Router

Se decidió separar los endpoints de `main.py`.

Se creó:

```text
routes.py
```

Responsabilidad:

- contener todos los endpoints de la aplicación.

El router se registra posteriormente desde `main.py`.

Esta separación permite mantener la aplicación organizada y facilita el crecimiento del proyecto.

---

## Almacenamiento temporal

Se creó:

```text
storage.py
```

Contiene una lista global:

```python
tasks = []
```

Esta lista funciona como un almacén temporal de datos.

No existe persistencia.

Cuando el servidor se reinicia:

```text
Servidor detenido

↓

tasks desaparece

↓

Servidor iniciado

↓

tasks = []
```

Este comportamiento es el requerido por la especificación del proyecto.

---

## Primer endpoint del proyecto

Se implementó:

```text
GET /tasks
```

Su única responsabilidad es devolver el contenido de la lista `tasks`.

Si no existen tareas, la respuesta correcta es:

```json
[]
```

No se considera un error.

Una lista vacía representa que actualmente no existen recursos almacenados.

---

## Modelos de datos (Pydantic)

Se comenzó el diseño de los modelos utilizando Pydantic.

Se comprendió que un mismo recurso puede necesitar distintos modelos dependiendo del contexto.

Ejemplo:

## Modelo de entrada

Representa los datos que envía el cliente.

```text
POST /tasks
```

Ejemplo:

```json
{
    "title": "Comprar leche"
}
```

---

## Modelo de salida

Representa la tarea completa devuelta por la API.

```json
{
    "id": 1,
    "title": "Comprar leche",
    "done": false
}
```

Separar ambos modelos evita que el cliente envíe información que únicamente debe generar el servidor.

---

## Comprensión del flujo Backend

Durante esta sesión se comprendió el flujo básico de comunicación entre frontend y backend.

```text
Frontend

↓

Petición HTTP

↓

FastAPI

↓

Pydantic valida los datos

↓

Endpoint

↓

Almacenamiento (tasks)

↓

Respuesta JSON

↓

Frontend
```

Este patrón será el mismo para todos los endpoints del proyecto.

Únicamente cambiará la lógica ejecutada por cada uno.

---

## Patrón general de los endpoints

Todos los endpoints siguen la misma estructura:

```text
Recibir petición

↓

Validar datos (Pydantic)

↓

Ejecutar lógica

↓

Responder con JSON
```

Lo que cambia entre un endpoint y otro es la operación realizada sobre los datos.

| Endpoint | Acción |
| ---------- | -------- |
| GET | Consultar datos |
| POST | Crear datos |
| PUT | Reemplazar un recurso completo |
| PATCH | Modificar parcialmente un recurso |
| DELETE | Eliminar un recurso |

---

## Conceptos aprendidos

- Arquitectura básica de un proyecto FastAPI.
- Diferencia entre aplicación (`FastAPI`) y router (`APIRouter`).
- Función del middleware CORS.
- Qué es un endpoint.
- Qué es un modelo de datos.
- Función de Pydantic.
- Diferencia entre modelos de entrada y salida.
- Almacenamiento temporal en memoria.
- Flujo completo entre frontend y backend.

---

## Estado del proyecto

### Completado

- ✅ Entorno virtual configurado.
- ✅ Dependencias instaladas con UV.
- ✅ Variables de entorno preparadas (`.env` / `.env.example`).
- ✅ Git configurado para proteger archivos sensibles (`.gitignore`).
- ✅ Estructura inicial del backend (`app/`).
- ✅ Aplicación FastAPI creada (`main.py`).
- ✅ Endpoint de prueba `GET /`.
- ✅ Documentación automática (`/docs`).
- ✅ CORS configurado para el frontend local.
- ✅ Router creado y registrado (`routes.py` → `main.py`).
- ✅ Almacenamiento temporal en memoria (`storage.py` → `tasks = []`).
- ✅ Endpoint `GET /tasks`.
- ✅ Diseño inicial de modelos Pydantic (`TaskCreate`, `Task`).

### Pendiente

- ⬜ Completar `POST /tasks` (ahora está iniciado, pero sin lógica).
- ⬜ Generar IDs únicos e incrementales.
- ⬜ Implementar `PUT /tasks/{task_id}`.
- ⬜ Implementar `PATCH /tasks/{task_id}`.
- ⬜ Implementar `DELETE /tasks/{task_id}`.
- ⬜ Leer configuración desde `.env` en `config.py`.
- ⬜ Integrar Groq en `POST /instruction`.
- ⬜ Implementar `POST /transcribe`.
- ⬜ Probar flujo completo voz → IA → acción (frontend + backend).