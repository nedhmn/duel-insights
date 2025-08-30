# Backend AI Context

## Overview

This is the FastAPI backend for the Duel Insights project. It provides the REST API, manages the database via SQLAlchemy, and handles all asynchronous data processing with Celery.

## Core Technologies

- FastAPI
- PostgreSQL & SQLAlchemy 2.0 (async)
- Celery & Redis
- Pydantic V2

## Documentation Index

This directory contains all the detailed documentation for the backend. Use the following files as your primary source of truth for their respective topics:

- **`api-specification.md`**: The complete REST API reference, including all endpoints, request/response models, and error codes.

- **`conventions.md`**: The strict rulebook for all backend code, covering file structure, Python/FastAPI best practices, and error handling patterns.

- **`database.md`**: A detailed description of the PostgreSQL schema, including all models, fields, relationships, and performance indexes.

- **`pipeline.md`**: An explanation of the data processing pipeline, from initial data extraction to the final on-demand transformation.

- **`inspo/`**: A directory containing non-runnable reference code snippets for core business logic (e.g., `extractor.md`, `parser.md`).
