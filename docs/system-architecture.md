# System Architecture

This document provides a high-level overview of the components, data flows, and deployment model for the Duel Insights project.

## 1. Components

The system is composed of several distinct services and technologies that work together.

-   **Frontend (Planned):** A **Next.js** application responsible for the user interface. Deployed on **Vercel**.
-   **Backend:** A **FastAPI** application that provides a REST API for all operations. Deployed on **Railway**.
-   **Database:** A **PostgreSQL** database managed by Railway, used for storing metadata like users, jobs, and S3 object keys.
-   **Task Queue:** **Celery** workers handle long-running jobs like web scraping.
-   **Message Broker / Cache:** **Redis**, managed by Railway, is used as the Celery broker and for caching processed results.
-   **Raw Data Storage:** **AWS S3** is used to store the raw JSON data scraped from replay URLs and for daily database backups.
-   **Authentication:** **Clerk** handles user authentication. The frontend gets a JWT from Clerk, which is passed to and validated by the backend on each API call.
-   **Scraping Service:** **Playwright** is used for browser automation to scrape replay data, routed through the **BrightData** proxy service to handle CAPTCHAs and prevent blocking.

## 2. Data Flow for an Individual Job

The following describes the end-to-end flow for processing a standard "Individual Mode" job.

1.  **Job Submission:** The user, authenticated via Clerk on the frontend, submits a list of DuelingBook replay URLs to the backend API, including the JWT in the request header.
2.  **Job Creation:** The FastAPI backend validates the JWT and the request, then creates a `Job` record in the PostgreSQL database with a `PENDING` status.
3.  **Task Queuing:** The API enqueues an orchestration task (`process_individual_job`) in Celery via the Redis broker.
4.  **Async Processing:** A Celery worker picks up the job. It creates a separate `scrape_single_url` task for each URL in the job.
5.  **Scraping:** Each scraping task checks the database to see if the URL has been scraped before.
    -   **Cache Hit:** If the URL exists, it uses the existing S3 key.
    -   **Cache Miss:** If new, the task uses Playwright to connect through the BrightData proxy, scrape the replay, and upload the raw JSON to the S3 bucket. A record mapping the URL to the new S3 key is saved in the database.
6.  **Progress Update:** As each URL task completes, it atomically increments the `processed_urls` count on the main `Job` record in the database.
7.  **Results Retrieval:** When the user requests the results, the backend checks a Redis cache.
    -   **Cache Hit:** The cached results are returned immediately.
    -   **Cache Miss:** The backend retrieves all raw JSON files from S3, transforms them into the final analysis format on-demand, caches the result in Redis with a 1-hour TTL, and returns it to the user.

## 3. Maintenance and Backup (Planned)

To ensure data durability, a daily backup process will be implemented.

-   **Scheduled Task:** A daily scheduled job (e.g., a cron job or Celery Beat task) will trigger a database dump (`pg_dump`).
-   **S3 Storage:** The resulting backup file will be compressed and uploaded to a designated S3 bucket.
-   **Retention Policy:** An S3 Lifecycle Policy will be configured to automatically delete backups older than 7 days to manage storage costs.