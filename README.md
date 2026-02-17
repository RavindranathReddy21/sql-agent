# SQL Agent with LangGraph and FastAPI

A production-style SQL Agent built using LangGraph, FastAPI, and SQLite.

This system converts natural language questions into SQL queries,
executes them safely, and returns structured responses through a REST
API.

## Overview

The agent is implemented using a graph-based workflow powered by
LangGraph.\
It dynamically extracts database schema information, generates SQL using
an LLM, executes the query, and retries automatically if errors occur.

The system is designed with explicit state management and controlled
execution flow.

## Architecture

User Question\
→ Schema Extraction\
→ SQL Generation (LLM)\
→ SQL Execution\
→ Error Check\
→ SQL Fix (if needed)\
→ Response Formatting

The workflow ensures deterministic orchestration around probabilistic
LLM reasoning.

## Project Structure

    sql-agent/
    │
    ├── app/
    │   ├── main.py        # FastAPI entry point
    │   ├── graph.py       # LangGraph workflow
    │   ├── nodes.py       # Agent nodes
    │   ├── db.py          # Database connection
    │   ├── models.py      # Request/response models
    │
    ├── database/
    │   ├── schema.sql     # Table definitions
    │   ├── seed.sql       # Dummy relational data
    │
    ├── scripts/
    │   └── init_db.py     # Database initialization script
    │
    ├── .env
    ├── pyproject.toml
    └── README.md

## Features

-   LLM-powered SQL generation\
-   Automatic SQL error correction loop\
-   SQL safety layer (blocks destructive queries)\
-   Dynamic schema extraction from SQLite\
-   FastAPI REST interface\
-   Relational database with foreign key relationships\
-   Dummy data for realistic join queries

## Setup Instructions

### 1. Create Virtual Environment

``` bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install Dependencies

``` bash
pip install -e .
```

### 3. Configure Environment Variables

Create a `.env` file:

    OPENAI_API_KEY=your_key_here
    DATABASE_URL=sqlite:///mydb.db

### 4. Initialize Database

``` bash
python scripts/init_db.py
```

This will:

-   Create `mydb.db`
-   Create all relational tables
-   Insert dummy data

### 5. Start the API Server

``` bash
uvicorn app.main:app --reload
```

Access API documentation at:

    http://127.0.0.1:8000/docs

## Example Queries

-   Show total revenue per user\
-   List users with pending payments\
-   Which products sold the most\
-   Show top 5 orders by total amount\
-   How many orders did each user place

## SQL Safety

Only SELECT statements are permitted.\
Destructive operations such as DROP, DELETE, UPDATE, ALTER, and TRUNCATE
are blocked before execution.

## Tech Stack

-   Python 3.11+
-   FastAPI
-   LangGraph
-   LangChain
-   SQLAlchemy
-   SQLite

## Future Improvements

-   PostgreSQL support\
-   JWT-based authentication\
-   Query caching\
-   Streaming responses\
-   Query history logging\
-   Docker containerization\
-   CI/CD pipeline

## Purpose

This project demonstrates:

-   Controlled agent orchestration using LangGraph\
-   Structured state management\
-   Reliable LLM integration\
-   Backend API engineering\
-   Relational database integration

Designed as a production-style AI system.
