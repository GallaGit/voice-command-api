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

---

## Estado actual

Completado:

✅ Entorno virtual configurado.  
✅ Dependencias instaladas mediante UV.  
✅ Variables de entorno preparadas.  
✅ Git configurado para proteger archivos sensibles.  
✅ Estructura inicial del backend creada.

Pendiente:

⬜ Crear la aplicación FastAPI.  
⬜ Configurar CORS.  
⬜ Crear modelos de datos.  
⬜ Crear endpoints CRUD de tareas.  
⬜ Integrar Groq en `/instruction`.  
⬜ Probar flujo completo voz → IA → acción.
