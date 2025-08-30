# Backend Conventions

This document outlines the code style, patterns, and best practices for developing the Duel Insights backend.

## 1. General Principles

- **Programming Style:** Use functional, declarative programming. Avoid classes where possible, including within `services.py` files.
- **Documentation:** Function and method documentation should be a single-line comment. Avoid adding a comment if the function name is sufficiently clear. Do not add comments to the top of Python files. Pydantic models should not have description comments.
- **Modularity:** Prefer iteration and modularization to avoid code duplication.
- **Naming:** Use descriptive variable names, including auxiliary verbs (e.g., `is_active`, `has_permission`).
- **API Pattern:** Follow the Receive an Object, Return an Object (RORO) pattern.

## 2. File & Directory Structure

- **Naming Convention:** All directories and files must use lowercase with underscores (e.g., `user_routes.py`).
- **Route Modularity:** Each route, including subroutes, must have its own directory containing at least `models.py`, `routes.py`, and `services.py` files.
- **Dependency Scoping:** If a dependency is used only in one route, it should be defined in that route's `routes.py` file. Shared dependencies must be hoisted to `packages/backend/app/api/deps.py`.

## 3. Python & FastAPI Best Practices

- **Type Hinting:**
  - Use `| None` instead of `Optional` from the `typing` library.
  - Use the built-in `dict` and `list` types instead of importing `Dict` or `List` from `typing`.
  - All function signatures must include type hints.
- **Asynchronous Code:**
  - Use `async def` for asynchronous operations like I/O.
  - Use `def` for synchronous, pure functions.
- **Validation:** Use Pydantic models for input validation and response schemas rather than raw dictionaries.
- **Dependency Injection:**
  - Rely on FastAPI's dependency injection system for managing resources.
  - To avoid repetition, assign common dependency patterns to a variable using `Annotated`.
    - Example: `AccountDep = Annotated[Account, Depends(get_account)]`
- **Application Lifecycle:** Use `lifespan` context managers instead of `@app.on_event("startup")` for managing startup and shutdown logic.
- **HTTP Requests:** All outbound HTTP requests must be made using the `httpx` library.
- **Testing:** Tests should be minimal.

## 4. Error Handling

- **Structure:** Handle errors and edge cases at the very beginning of functions. Use guard clauses to handle preconditions early.
- **Control Flow:** Use early returns for error conditions to avoid nested `if` statements. The "happy path" should be the last part of the function.
- **API Errors:** Use `HTTPException` for all expected, HTTP-related errors.

## 5. Performance

- **Asynchronous Operations:** All database calls and external API requests must be asynchronous to prevent blocking I/O.
- **Caching:** Implement caching strategies using Redis for frequently accessed data.

## 6. Testing & Validation

All new logic must be accompanied by tests to ensure correctness and prevent regressions.

- **Framework:** All tests are written using the `pytest` framework.
- **Location:** Tests reside in the top-level `tests/` directory, which mirrors the `app/` source structure.
- **Philosophy:** Tests should be minimal and focused. Each test should target a specific piece of functionality.
- **Test Type:**
  - **Unit Tests:** The project relies exclusively on unit tests. They are used to validate business logic in isolation. All external dependencies (database, external services, etc.) must be mocked.
- **Validation Gates:** Before any feature or task is considered complete, it must pass the following automated checks: `pytest`, `mypy`, and `ruff`.

## 7. Task Management (`TODOS.md`)

The development roadmap and a detailed list of tasks are managed in the `TODOS.md` file located in the root of the backend package (`packages/backend/TODOS.md`).

- **Single Source of Truth:** This file is the definitive source for what needs to be worked on next.
- **Dynamic Document:** It is a living document that should be updated dynamically during development sessions. As tasks are completed, they should be checked off. As new requirements or bugs are identified, they should be added.
- **Structure:** The file is organized into logical phases (e.g., "Phase 1: Core Infrastructure"), with tasks for each phase represented as a checklist.
