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
    README.md
    Makefile
    requirements.txt

------------------------------------------------------------------------

## 🛠️ Getting Started

### Prerequisites

-   Python 3.12+
-   Git
-   Docker & Docker Compose (optional)

### Install (Local Dev)

``` bash
git clone https://github.com/bemonio/bokkapro-platform.git
cd bokkapro-platform

python3 -m venv .venv
. .venv/bin/activate

pip install -r requirements.txt
```

------------------------------------------------------------------------

## 🧪 Development Scripts (Makefile)

  Command        Description
  -------------- ----------------------
  make up        Start FastAPI server
  make migrate   Apply DB migrations
  make reset     Reset database
  make lint      Run ruff linter
  make test      Run pytest tests

------------------------------------------------------------------------

## 📡 API Documentation

OpenAPI docs:\
http://localhost:8000/docs

Health endpoint:\
http://localhost:8000/health

------------------------------------------------------------------------

## 🧩 UI Features

-   List view with pagination + search
-   Create/Edit modals
-   Soft delete support
-   HTMX dynamic updates

------------------------------------------------------------------------

## 📈 Roadmap

Future enhancements:

-   OR‑Tools route optimization
-   JWT Authentication / Auth0
-   PostgreSQL production deployment
-   Multi‑tenant architecture
-   CI/CD pipelines

------------------------------------------------------------------------
