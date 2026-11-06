# 📋 Gestor de Tareas — API REST + Interfaz Web

Aplicación web completa para la gestión de tareas (CRUD) construida con **Flask**, **SQLAlchemy** y **SQLite/PostgreSQL**, totalmente dockerizada y desplegada en **Render**.

🔗 **Aplicación en vivo:** [dockerizaci-n-implantaci-n-y-despliegue.onrender.com](https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com)

---

## 📖 Tabla de Contenidos
1. [Descripción](#-descripción)
2. [Demo en vivo](#-demo-en-vivo)
3. [Características](#-características)
4. [Tecnologías Utilizadas](#-tecnologías-utilizadas)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Endpoints de la API](#-endpoints-de-la-api)
7. [Instalación y Ejecución Local](#-instalación-y-ejecución-local)
8. [Ejecución con Docker](#-ejecución-con-docker)
9. [Despliegue en Render](#-despliegue-en-render)
10. [Variables de Entorno](#-variables-de-entorno)
11. [Autor](#-autor)
12. [Licencia](#-licencia)

---

## 📝 Descripción

**Gestor de Tareas** es una aplicación *full-stack* que permite crear, listar, editar, marcar como completadas y eliminar tareas desde una interfaz web moderna e intuitiva. El backend expone una API REST construida en Flask y el frontend consume dicha API mediante JavaScript (`Fetch API`).

El proyecto fue desarrollado como parte de un ejercicio práctico de **dockerización, implantación y despliegue de aplicaciones web**.

---

## 🚀 Demo en vivo

| Recurso | URL |
| :--- | :--- |
| 🌐 **Interfaz Web** | [https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com](https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com) |
| 📡 **API (Listar tareas)** | [https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com/api/tasks](https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com/api/tasks) |
| ❤️ **Health Check** | [https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com/healthz](https://dockerizaci-n-implantaci-n-y-despliegue.onrender.com/healthz) |

> ⚠️ **Nota:** La instancia gratuita de Render entra en suspensión tras periodos de inactividad. La primera petición puede tardar ~50 segundos en responder mientras el servicio se reactiva.

---

## ✨ Características

- ✅ **CRUD completo** de tareas (Crear, Leer, Actualizar, Eliminar).
- 🎨 **Interfaz web moderna** con diseño responsive y animaciones.
- 🔎 **Filtros por estado:** Todas / Pendientes / Completadas.
- 📊 **Estadísticas en tiempo real** (total, completadas, pendientes).
- 💾 **Persistencia de datos** con SQLite (local) o PostgreSQL (producción).
- 🐳 **Totalmente dockerizada** (`Dockerfile` + `docker-compose.yml`).
- ☁️ **Despliegue en la nube** con Render.
- 🔒 **CORS habilitado** para permitir peticiones desde el frontend.
- 🩺 **Endpoint de health check** (`/healthz`) para monitoreo.

---

## 🛠 Tecnologías Utilizadas

### Backend
| Tecnología | Versión | Uso |
| :--- | :--- | :--- |
| **Python** | 3.12 | Lenguaje principal |
| **Flask** | 3.1.2 | Framework web |
| **Flask-SQLAlchemy** | 3.1.1 | ORM para base de datos |
| **SQLAlchemy** | 2.0.39 | Motor ORM |
| **Flask-CORS** | 5.0.0 | Manejo de peticiones de origen cruzado |
| **Gunicorn** | 22.0.0 | Servidor WSGI para producción |
| **psycopg2-binary** | 2.9.10 | Driver PostgreSQL |

### Frontend
| Tecnología | Uso |
| :--- | :--- |
| **HTML5** | Estructura de la interfaz |
| **CSS3** | Estilos, animaciones y diseño responsive |
| **JavaScript (ES6+)** | Lógica del cliente y peticiones con `Fetch API` |

### DevOps & Herramientas
| Tecnología | Uso |
| :--- | :--- |
| **Docker** | Contenedorización de la aplicación |
| **Docker Compose** | Orquestación de servicios |
| **Render** | Plataforma de despliegue en la nube |
| **GitHub** | Control de versiones |

---

## 📂 Estructura del Proyecto

```text
proyecto-todo-api/
│
├── src/
│   ├── app.py                 # Aplicación Flask (API + rutas estáticas)
│   └── static/                # Archivos estáticos del frontend
│       ├── index.html         # Interfaz web principal
│       ├── style.css          # Estilos de la aplicación
│       └── script.js          # Lógica del cliente (Fetch API)
│
├── data/                      # Base de datos SQLite (desarrollo local)
│   └── tasks.db
│
├── Dockerfile                 # Imagen Docker de la aplicación
├── docker-compose.yml         # Orquestación de servicios
├── requirements.txt           # Dependencias de Python
├── .dockerignore              # Archivos excluidos del build de Docker
├── .env                       # Variables de entorno locales
├── .gitignore                 # Archivos ignorados por Git
└── README.md                  # Documentación del proyecto
