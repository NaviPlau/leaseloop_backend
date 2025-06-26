# Guesthouse PMS Backend

## A modern, containerized Django backend for managing properties, bookings, clients, units, and services — ready for production deployment with Docker.

## Table of Contents

1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Quickstart](#quickstart)
4. [Usage](#usage)
5. [Environment Variables](#environment-variables)
6. [Contact](#contact)

---

## Introduction

This full-stack-ready backend provides the API for a hotel and guesthouse Property Management System (PMS). It supports multiple properties, units, bookings, clients, seasonal pricing, invoices, and analytics. The system uses PostgreSQL as the database and is designed to be deployed using Docker.

Perfectly suited for digital nomads, solopreneurs, or guesthouse owners looking for a privacy-respecting alternative to SaaS platforms.

---

---

## Prerequisites

- Ubuntu/Debian Server (local or remote)
- Docker & Docker Compose

```sh
sudo apt update && sudo apt install -y docker.io docker-compose
```

---

## Quickstart

1. **Install dependencies:**
   ```sh
   sudo apt update && sudo apt install -y docker.io docker-compose git
   ```
2. **Clone the repository:**
   ```sh
   git clone git@github.com:NaviPlau/leaseloop_backend.git
   cd leaseloop_backend
   ```
3. **Generate and configure the .env file:** <br>
   The environment file will be created automatically from env.template.
   Adjust the values to match your setup (optional):
   ```sh
   cp .env.template .env
   nano .env (optional)
   ```
4. **Log in to the admin panel:**
   ```sh
   http://<your-server-ip>:8020/admin
   ```

---

## Usage

### **Environment Variables**

The application uses environment variables to configure certain aspects of the system. These can be set in the `.env` file:

[simple_env_config.env](truck_signs_designs/settings/simple_env_config.env)

### **Managing the Database**

Run migrations manually inside the container if needed:

```sh
docker exec -it web python manage.py migrate
```

To create a new Django superuser manually:

```sh
docker exec -it web python manage.py createsuperuser
```

### **Collecting Static Files**

If you update static files and need to collect them again, run:

```sh
docker exec -it web python manage.py collectstatic --noinput
```

### **Stopping and Restarting the Container**

To stop the container:

```sh
docker stop web
```

To restart it:

```sh
docker start web
```

To remove the container completely:

```sh
docker rm web
```

To rebuild and restart:

```sh
TODO: final version
```

---

## Contact

### 👤 Personal

- [Portfolio](https://benjamin-tietz.com/)
- [Drop me a mail](mailto:mail@benjamin-tietz.com)

### 🌍 Social

- [LinkedIn](https://www.linkedin.com/in/benjamin-tietz/)

### 💻 Project Repository

- [GitHub Repository](https://github.com/NaviPlau/leaseloop_backend)
