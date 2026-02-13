# 🛠️ BokkaPro Platform

A clean, scalable logistics platform designed for route planning and
operations management, built with **FastAPI**, **SQLModel**, **Alembic
migrations**, and modern server-rendered UI using **Jinja2 + HTMX +
Alpine.js + TailwindCSS**.

This repository follows **Clean Architecture** in a **Polylith-style
monorepo** layout and is structured to support future extensions like
multi‑tenant, authentication, and OR‑Tools based optimization.

------------------------------------------------------------------------

## 🚀 Overview

BokkaPro Platform is the backend and server-rendered UI for a logistics
planning system.\
It allows managing:

-   🏢 Offices\
-   🚚 Vehicles\
-   👥 Crews\
-   📍 Tasks (pickups & deliveries)\
-   🗺️ Routes (manual assignment initially)

This setup is Stage 1, focused on **data management and CRUD**,
preparing for Stage 2 --- real optimization with OR‑Tools.

------------------------------------------------------------------------

## 📦 Tech Stack

  Layer          Technology
  -------------- -----------------------------------------
  API            FastAPI
  ORM            SQLModel
  Migrations     Alembic
  Database       SQLite (dev) → PostgreSQL (prod)
  Runtime        Docker + Docker Compose (primary)
  UI             Jinja2 + HTMX + Alpine.js + TailwindCSS
  Architecture   Clean Architecture + Polylith

------------------------------------------------------------------------

## 📁 Repository Structure

    /bases
      ├── platform/
      ├── webapp/

    /components
      ├── domain__*
      ├── app__*
      ├── persistence__sqlmodel/
      ├── api__fastapi/
      ├── ui__server_rendered/

    /alembic
      ├── env.py
      └── versions/

    main.py
    Dockerfile
    docker-compose.yml
    README.md
    Makefile
    requirements.txt

------------------------------------------------------------------------

## 🐳 Docker-First Workflow (Primary)

### Prerequisites

-   Docker
-   Docker Compose

### Database URL and persistence

All services run with:

-   `DATABASE_URL=sqlite:////app/storage/app.db`
-   volume mount: `./storage:/app/storage`

This keeps SQLite data persisted on the host under `storage/app.db`.

### Run the stack

``` bash
docker compose up --build
```

-   `migrate` runs first (`alembic upgrade head`)
-   `app` starts only after `migrate` completes successfully
-   API docs: <http://localhost:8000/docs>
-   Health: <http://localhost:8000/health>

### Run migrations only

``` bash
docker compose run --rm migrate
```

### Run tests

``` bash
docker compose run --rm test
```

### Stop the stack

``` bash
docker compose down
```

### Reset local DB

``` bash
docker compose down -v
rm -f storage/app.db
```

------------------------------------------------------------------------

## 🧪 Makefile (Optional Shortcuts)

Make targets are thin wrappers around Docker Compose commands:

  Command      Docker Compose equivalent
  ------------ ----------------------------------------
  `make up`    `docker compose up --build`
  `make down`  `docker compose down`
  `make reset` `docker compose down -v && rm -f storage/app.db`
  `make migrate` `docker compose run --rm migrate`
  `make test`  `docker compose run --rm test`

------------------------------------------------------------------------

## 📈 Roadmap

Future enhancements:

-   OR‑Tools route optimization
-   JWT Authentication / Auth0
-   PostgreSQL production deployment
-   Multi‑tenant architecture
-   CI/CD pipelines

------------------------------------------------------------------------
