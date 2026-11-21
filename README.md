# Sistema de Gestión para Lavadero Vehicular (Backend Django)

Sistema backend desarrollado en **Django** para la gestión integral de un lavadero vehicular, cubriendo todo el ciclo operativo (Reservas, Recepción, Órdenes de Trabajo, Stock y Facturación).

## 🚀 Tecnologías utilizadas
* **Python / Django** (Backend y ORM)
* **PostgreSQL** (Base de datos relacional)
* **Docker & Docker Compose** (Contenedorización y entorno reproducible)

---

## 📋 Requisitos previos
Asegúrate de tener instalado en tu computadora:
* [Docker](https://www.docker.com/) y Docker Compose.
* Git.

---

## ⚙️ Configuración y Puesta en Marcha (Entorno Local)

Sigue estos pasos para clonar y poner a marchar el proyecto en cualquier máquina local:

### 1. Clonar el repositorio
```bash
git clone [https://github.com/nobodycaresv/Lavadero_DB.git](https://github.com/nobodycaresv/Lavadero_DB.git)
cd Lavadero_DB

2. Configurar las variables de entorno
Crea un archivo llamado .env en la raíz del proyecto basándote en la siguiente estructura local:

Fragmento de código
DB_NAME=lavadero_db
DB_USER=postgres
DB_PASSWORD=tu_password_local
DB_HOST=db
DB_PORT=5432
DEBUG=1
SECRET_KEY=tu-secret-key-super-segura
3. Levantar los contenedores con Docker
Ejecuta el siguiente comando para construir y encender tanto la base de datos PostgreSQL como el servidor de Django:

Bash
docker compose up -d --build
4. Aplicar migraciones y crear superusuario
Una vez que los contenedores estén corriendo, inicializa las tablas en la base de datos local y crea tu usuario administrador:

Bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
🌐 Acceso al Sistema
Una vez completados los pasos anteriores, podrás acceder a:

Panel de Administración: http://localhost:8000/admin

🔄 Flujo de Negocio Esperado
Reserva: Registro inicial de turnos y vehículos.

Recepción: Confección de fichas técnicas con el estado del vehículo.

Órdenes de Trabajo: Apertura y asignación del servicio.

Ejecución y Stock: Control de tiempos, empleados y descuento de insumos.

Caja y Facturación: Cierre de cobros y emisión de pagos.

## Estructura del proyecto

```
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── entrypoint.sh
├── .env.example
├── manage.py
├── config/          # configuración global del proyecto (settings, urls)
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── core/            # app de ejemplo (vista de inicio, reemplazar/ampliar)
│   ├── views.py
│   ├── models.py
│   └── templates/core/home.html
└── api/             # app de ejemplo para la API REST
    ├── views.py
    └── urls.py
```

---
Prof. Lic. Adrián Aguirre | ISDEM | Taller de Programación
