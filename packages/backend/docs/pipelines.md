# Data Processing Pipeline

This document describes the entire pipeline for processing DuelingBook replay data, from initial scraping to final analysis.

## 1. Shared Component: Data Extraction

Data extraction is the process of acquiring the raw replay JSON from a DuelingBook URL. This logic is executed within a Celery task (`scrape_single_url`) for each URL.

The core strategy is to use a headless browser (Playwright) to capture the replay page's `console.log` output. The full, unconcealed replay data is dynamically loaded and logged to the console by the site's JavaScript, which this process intercepts and saves.

For a detailed code implementation of this logic, see the reference file: `../inspo/extractor.md`.

## 2. Shared Component: Data Transformation

Data transformation is the process of parsing the raw replay JSON from the extraction step into a structured, analyzable format. This logic is executed on-demand when a user requests job results.

The core strategy is to load the raw JSON into a `pandas` DataFrame to efficiently process the list of game events. The process normalizes the nested data, extracts key information like card names and game winners, and groups the events game-by-game to build a structured summary of the match.

For a detailed code implementation of this logic, see the reference file: `../inspo/parser.md`.

## 3. End-to-End Flow: Individual Mode

The Individual Mode pipeline uses the shared components in a straightforward sequence:

1.  **Extraction:** For each URL submitted in the job, a Celery task executes the **Data Extraction** process. The resulting raw JSON for each URL is stored in S3.
2.  **Transformation:** When the user requests the results, the system retrieves all the raw JSON files for that job from S3 and runs the **Data Transformation** process on the entire collection to produce the final, aggregated analysis.

## 4. End-to-End Flow: GFWL Mode (Planned)

The GFWL Mode pipeline involves a multi-step flow that uses the components in a more complex sequence:

1.  **Extraction:** The **Data Extraction** process is run for every URL found in the submitted team data, and the raw JSON files are stored in S3.
2.  **Initial Transformation & Discovery:** A partial **Data Transformation** is run on all the raw data with the specific goal of identifying and extracting a list of all unique player names. This list is then presented to the user.
3.  **User Confirmation:** The system waits for the user to submit a list of "confirmed players" they wish to analyze.
4.  **Final Transformation:** Once players are confirmed, a final, more detailed **Data Transformation** is performed on the raw data to generate profiles and analysis for _only_ the confirmed players.
