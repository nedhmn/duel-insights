# API Specification

This document provides a complete reference for the Duel Insights backend API.

## 1. Base URL

- **Development:** `http://localhost:8000/api/v1`

## 2. Authentication

All protected endpoints require a JWT issued by Clerk. The token must be included in the `Authorization` header.

- **Format:** `Authorization: Bearer <clerk_jwt_token>`

The user record is automatically created in the database upon the first verified API request.

## 3. Standard Response Format

### Success Response

```json
{
    "data": {...},
    "status": "success",
    "message": "Operation completed successfully"
}
```

### Error Response

```json
{
  "detail": "Error description",
  "status": "error",
  "error_code": "ERROR_CODE_STRING"
}
```

## 4. Job Status Values

- **PENDING:** Job is created and awaiting processing.
- **RUNNING:** Job is actively being processed.
- **COMPLETED:** Job finished successfully.
- **FAILED:** Job failed due to an error.
- **CANCELLED:** Job was cancelled by the user.

## 5. Error Codes

The `error_code` field in an error response will be one of the following strings:

- `VALIDATION_ERROR`
- `AUTHENTICATION_ERROR`
- `NOT_FOUND`
- `JOB_NOT_READY`
- `JOB_FAILED`
- `RATE_LIMIT_EXCEEDED`

## 6. Rate Limiting

The API enforces the following rate limits per user:

- **Job Submission:** 5 requests per hour.
- **Status/Progress Checks:** 60 requests per minute.

## 7. Individual Mode Endpoints

#### `POST /jobs/individual`

**Submit Individual Job:** Creates a new analysis job for a single player.

- **Request Body:**

```json
{
  "urls": ["https://duelingbook.com/replay?id=..."]
}
```

- **Validation:**
  - 1-12 URLs per job.
  - All URLs must be valid and unique DuelingBook replay links.

#### `GET /jobs/{job_id}`

**Get Job Status:** Retrieves the current status and metadata for a specific job.

#### `GET /jobs/{job_id}/progress`

**Get Job Progress:** Retrieves real-time progress for a running job.

#### `GET /jobs/{job_id}/results`

**Get Job Results:** Retrieves the transformed analysis for a completed job.

#### `DELETE /jobs/{job_id}`

**Cancel Job:** Cancels a job that is currently in `PENDING` or `RUNNING` status.

## 8. Job Sharing Endpoints

#### `POST /jobs/{job_id}/share`

**Enable/Disable Public Sharing:** Toggles the public visibility of a job's results.

- **Request Body:**

```json
{
  "is_public": true
}
```

#### `GET /results/{shareable_id}`

**Get Shared Results:** A public, unauthenticated endpoint to view the results of a shared job.

## 9. User Management Endpoints

#### `GET /users/me/jobs`

**Get User Jobs:** Lists all jobs for the currently authenticated user with pagination.

- **Query Parameters:**
  - `page`: The page number (default: 1).
  - `limit`: Items per page (default: 10, max: 50).
  - `status`: Filter by job status (optional).
  - `job_type`: Filter by job type (optional).

## 10. GFWL Mode Endpoints (Planned)

- `POST /jobs/gfwl/submit-team`
- `GET /jobs/gfwl/{job_id}/discovered-players`
- `POST /jobs/gfwl/{job_id}/confirm-players`
- `GET /jobs/gfwl/{job_id}/results`

## 11. Utility Endpoints

#### `GET /utils/health-check`

**Health Check:** Checks the operational status of the service.

- **Success Response (`200 OK`):**

```json
{
  "status": "ok"
}
```
