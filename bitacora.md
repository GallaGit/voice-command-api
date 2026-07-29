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

## El proyecto de la academia se debe desarrollar de esta forma

Voice Command API — Habla con tu Lista de Tareas Por @4GeeksAcademy y otros colaboradores en 4Geeks Academy build by developers4Geeks Academy Estas instrucciones están disponibles en inglés. Antes de empezar: 📗 Lee las instrucciones sobre cómo iniciar un proyecto de programación. 🎯 Tu reto Una startup de productividad ha construido una interfaz de voz que permite a sus usuarios gestionar una lista de tareas únicamente hablando. El frontend ya está listo — funciona en el navegador, captura la voz del usuario a través del micrófono y la transcribe a texto usando la Web Speech API. Tu trabajo es construir el backend que hace que esa interfaz funcione de verdad. El frontend envía cada transcripción a un único endpoint de entrada: POST /instruction. Desde ahí, tu API debe identificar qué pidió el usuario, redirigir la petición al endpoint interno correcto y devolver una respuesta que la interfaz pueda mostrar. El tech lead del equipo te dejó esta nota antes de irse de vacaciones: Especificaciones del backend — Voice Command API Punto de entrada POST /instruction — recibe una transcripción en texto plano y llama a la API de Groq para extraer la intención y los parámetros. Debe devolver un JSON que identifique qué endpoint llamar y con qué argumentos. El frontend usará esta respuesta para hacer la petición de seguimiento. Endpoints de tareas (almacenamiento en memoria — sin base de datos) GET /tasks — devuelve la lista completa de tareas POST /tasks — crea una nueva tarea (requiere title, campo opcional done, por defecto false) PUT /tasks/<int:task_id> — reemplaza una tarea completa PATCH /tasks/<int:task_id> — marca una tarea como completada o actualiza el título DELETE /tasks/<int:task_id> — elimina una tarea por ID Almacenamiento Usa una lista a nivel de módulo como almacén de datos. Cada tarea es un diccionario con id, title y done. Sin base de datos, sin sistema de archivos. Integración con Groq Usa la API de Groq (modelo: llama3-8b-8192 o similar) desde tu endpoint /instruction. El system prompt debe instruir al LLM para que responda únicamente con un objeto JSON en este formato exacto: { "endpoint": "/tasks", "method": "POST", "params": { "title": "Comprar leche" } } El LLM nunca debe devolver texto libre — solo ese JSON. Tu ingeniería de prompt es lo que hace que esto funcione. La PM de la startup quiere ver el flujo completo de voz a acción funcionando de extremo a extremo: el usuario dice "añade comprar leche a mi lista" y la tarea aparece. Ese es tu objetivo. esto es lo que quieren que haga: Configuración Crea un entorno virtual e instala FastAPI, Uvicorn y el SDK de Python de Groq Guarda tu API key de Groq en un archivo env nunca la subas al repositorio Configura CORS para que el frontend pueda comunicarse con tu API Almacenamiento en memoria Declara una lista a nivel de módulo llamada tasks para usarla como almacén de datos Cada tarea debe tener id (entero), title (cadena de texto) y done (booleano, por defecto false Endpoints de tareas GET /tasks devuelve todas las tareas como un array JSON POST /tasks crea una tarea a partir del cuerpo de la petición y la añade a la lista; devuelve la tarea creada con su ID asignado PUT/tasks/<task_id> reemplaza el objeto tarea completo para el ID indicado PATCH/tasks/<task_id> actualiza parcialmente una tarea (título y/o estado done DELETE /tasks/<task id> elimina la tarea con el ID indicado; devuelve un mensaje de confirmación Endpoint de instrucción POST/instruction recibe un cuerpo JSON con un campo transcription (texto plano) Llama a la API de Groq con un system prompt adecuado que fuerce al LLM a responder únicamente con un objeto JSON estructurado que indique endpoint method y params Devuelve ese JSON directamente al frontend Conexión extremo a extremo Usando la respuesta de/instruction, el frontend llama automáticamente al endpoint de tareas correcto - verifica que esto funcione al menos para: crear, listar, actualizar y eliminar tareas hablando en voz alta ▲ IMPORTANTE: No uses base de datos. Todos los datos deben vivir en una lista de Python en memoria. La lista se reinicia cada vez que el servidor se reinicia ese es el comportamiento esperado para este proyecto. ▲ IMPORTANTE: El endpoint /instruction no debe contener lógica de detección de intención codificada manualmente (sin if "añade" in text Todas las decisiones de enrutamiento deben provenir de la respuesta del LLM. Qué vamos a evaluar Los cinco endpoints de tareas (GET POST PUT PATCH DELETE) están implementados y devuelven los códigos de estado HTTP apropiados Cada endpoint devuelve una respuesta JSON correctamente serializada El endpoint POST / instruction llama a la API de Groq y devuelve el JSON de enrutamiento estructurado El system prompt está bien construido: el LLM devuelve consistentemente JSON válido en el formato requerido para distintas entradas de voz CORS está configurado para que el frontend incluido pueda comunicarse con la API sin errores El archivo env está en el .gitignore y la API key nunca está expuesta en el código La lista en memoria se gestiona correctamente: los IDs son únicos y los elementos se añaden, actualizan y eliminan correctamente Nota: El frontend se proporciona y no será evaluado. No se espera que lo modifiques. Quiero intentar de hacerlo todo a mano yo hasta donde pueda y entender los conceptos básicos, no me des la respuestas a menos que yo te lo pida. Ve, cuando me paso a paso, ya tengo el área de trabajo lista; vamos a trabajar en local y luego subir todo a github. Antes de empezar, tengo la primera pregunta: ¿qué pasa con environment setting? se debe hacer en la rama main porque si lo hacen en otra rama las cosa de gitignore que crees en esa rama no van a ir a la main si hay un .env no va a pasar a la main verdad?