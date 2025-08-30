# Duel Insights - AI Command Center

This document contains the core mission, guiding principles, and master index for the Duel Insights project.

## 1. Project Goals & Core Features (What & Why)

The primary goal of Duel Insights is to provide deep analysis of DuelingBook replay data through a web application.

- **Individual Mode:** Users can submit a list of replay URLs for a single player to get a detailed performance breakdown.
- **GFWL Mode (Planned):** Users can submit team data to discover all players involved and receive comprehensive team and individual analysis.

## 2. Guiding Principles

These are high-level rules that apply across the entire project.

- **Testing Philosophy:** All new business logic must be accompanied by validation. The backend relies exclusively on unit tests where external dependencies are mocked.
- **Data Architecture:** The system follows a "raw data storage + on-demand transformation" pattern. Raw scraped data stored in S3 is the source of truth. Processed results are computed on-demand and cached in Redis.

## 3. Master Document Index

For detailed information, refer to the following documents:

- **System Overview:** [`/docs/system-architecture.md`](/docs/system-architecture.md)

  - _Purpose:_ A high-level description of how all system components connect and interact.

- **Backend Package:** [`/packages/backend/CLAUDE.md`](/packages/backend/CLAUDE.md)
  - _Purpose:_ The primary AI context and detailed document index for all backend-specific development.

## 4. Miscellaneous Rules

- All markdown files are to be in kebab-case.
- No mermaid diagrams in any files.
