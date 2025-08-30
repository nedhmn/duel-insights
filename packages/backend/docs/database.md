# Database Schema

This document provides a detailed overview of the PostgreSQL database schema, managed via SQLAlchemy 2.0 in async mode.

## 1. Overview

The database primarily stores metadata, job state, and pointers to data stored elsewhere (like S3). It is not intended to store large JSON blobs of raw or processed replay data.

## 2. BaseModel Inheritance

All core models inherit from a `BaseModel`, which provides the following common fields for every table:

- **`id`** (UUID, Primary Key): The internal unique identifier for the record.
- **`created_at`** (DateTime): Timestamp of when the record was created.
- **`updated_at`** (DateTime): Timestamp of when the record was last updated.

## 3. Core Models

### User

Stores user accounts, linked to a Clerk account.

- **Fields:**
  - **`clerk_user_id`** (String, Unique, Indexed): The immutable ID provided by Clerk.
- **Relationships:**
  - **`jobs`**: A one-to-many relationship to the `Job` model.

### Job

The central model for tracking an analysis job from submission to completion.

- **Fields:**
  - **`user_id`** (UUID, Foreign Key -> User, Indexed): Links the job to the user who submitted it.
  - **`job_type`** (Enum): The type of job (`INDIVIDUAL` or `GFWL`).
  - **`status`** (Enum): The current state of the job (`PENDING`, `RUNNING`, etc.).
  - **`urls`** (JSON): A list of DuelingBook replay URLs to be processed.
  - **`team_data`** (JSON, Nullable): The raw team data structure for GFWL jobs.
  - **`total_urls`** (Integer): The total number of unique URLs for this job.
  - **`processed_urls`** (Integer): A counter for completed URLs.
  - **`error_message`** (String, Nullable): Stores a fatal error message if the job fails.
  - **`shareable_id`** (UUID, Unique, Indexed): A unique ID for publicly sharing job results.
  - **`is_public`** (Boolean): A flag indicating if results are publicly accessible.
  - **`started_at`** (DateTime, Nullable): Timestamp of when processing began.
  - **`completed_at`** (DateTime, Nullable): Timestamp of when the job finished.
- **Relationships:**
  - **`user`**: A many-to-one relationship to the `User` model.
  - **`gfwl_submissions`**: A one-to-many relationship to the `GFWLTeamSubmission` model.

### ScrapedData

Maps a scraped URL to its raw data location in S3 to prevent duplicate scraping.

- **Fields:**
  - **`url`** (String, Unique, Indexed): The canonical DuelingBook replay URL.
  - **`s3_key`** (String): The path to the raw JSON object in the S3 bucket.

### GFWLTeamSubmission

Manages the state for the multi-step GFWL job workflow.

- **Fields:**
  - **`job_id`** (UUID, Foreign Key -> Job, Indexed): Links this record to its parent GFWL job.
  - **`team_name`** (String): The name of the team being analyzed.
  - **`discovered_players`** (JSON): A list of player names discovered during scraping.
  - **`confirmed_players`** (JSON, Nullable): The subset of players selected by the user for analysis.
  - **`confirmation_status`** (String): The state of the player confirmation step (`pending` or `confirmed`).
- **Relationships:**
  - **`job`**: A many-to-one relationship to the `Job` model.

## 4. Performance Indexes

The following indexes are defined to ensure query performance:

- **On `users` table:**
  - `clerk_user_id`
- **On `jobs` table:**
  - `user_id`
  - `shareable_id`
  - Composite: `(user_id, status)`
  - Composite: `(status, created_at)`
  - Composite: `(user_id, job_type)`
- **On `scraped_data` table:**
  - `url`
- **On `gfwl_team_submissions` table:**
  - `job_id`
  - Composite: `(job_id, confirmation_status)`
