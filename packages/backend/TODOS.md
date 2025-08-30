# Duel Insights API - Implementation Todo List

## Phase 1: Core Infrastructure (Week 1-2)

### Testing & Validation Setup (Must Pass Before Phase 2)

- [x] **Testing Infrastructure**
  - [x] Set up pytest configuration and test database
  - [x] Create basic test structure (`tests/` directory)
  - [x] Add unit test for Settings configuration
  - [x] Create test command in Makefile for validation

### Database & Models

- [x] **Setup Database Schema**
  - [x] Implement User model with clerk_user_id field (extending existing)
  - [x] Implement Job model with shareable_id and is_public fields
  - [x] Implement ScrapedData model (URL -> S3 key mapping)
  - [x] Implement GFWLTeamSubmission model
  - [x] Add database indexes for performance
  - [x] **Unit tests**: Test model validation and relationships

### Authentication & Security

- [x] **Clerk JWT Integration**
  - [x] Create JWT dependency for route protection
  - [x] Implement user context extraction from JWT claims
  - [x] Create middleware for authentication
  - [x] Add user creation/lookup logic on first JWT verification
  - [x] **Unit tests**: Test JWT validation and user lookup logic

### Configuration & Environment

- [x] **Environment Setup**
  - [x] Update Settings class with all required environment variables
  - [x] Add Redis URL configuration
  - [x] Add AWS S3 configuration (with aioboto3)
  - [x] Add Clerk JWT configuration
  - [x] Add BrightData configuration
  - [x] Create .env.example file
  - [x] **Unit tests**: Test configuration validation and defaults

### Phase 1 Success Criteria (All Must Pass)

- [x] **Validation Gate**
  - [x] All unit tests pass (`pytest`) - **Note: Tests require DB env vars**
  - [x] Type checking passes (`mypy app/`)
  - [x] Code formatting passes (`ruff check app/`)
  - [x] Database models can be created successfully
  - [x] Settings can load from environment variables

## Phase 2: Core API Endpoints (Week 2-3)

### Job Management Endpoints

- [x] **Individual Mode Endpoints**
  - [x] `POST /api/v1/jobs/individual` - Submit job with URL validation
  - [x] `GET /api/v1/jobs/{job_id}` - Get job status and metadata
  - [x] `GET /api/v1/jobs/{job_id}/progress` - Get real-time progress
  - [x] `GET /api/v1/jobs/{job_id}/results` - Get transformed results *(stub implementation)*
  - [x] `DELETE /api/v1/jobs/{job_id}` - Cancel pending/running job
  - [x] **Unit tests**: Test endpoint validation, error handling, and responses

### User Job Management

- [x] **User-Specific Endpoints**
  - [x] `GET /api/v1/jobs/` - List user's jobs with pagination (implemented in main jobs route)
  - [x] Add filtering by status and job_type
  - [x] **Unit tests**: Test pagination, filtering, and user isolation

### Shareable Results

- [x] **Public Sharing Feature**
  - [x] `POST /api/v1/jobs/{job_id}/share` - Enable/disable sharing
  - [x] `GET /api/v1/results/{shareable_id}` - Public results endpoint *(stub implementation)*
  - [x] Implement ShareService class
  - [x] Add share URL generation logic
  - [x] **Unit tests**: Test sharing permissions and public access

### Phase 2 Success Criteria (All Must Pass)

- [x] **Validation Gate**
  - [x] All unit tests pass (including new endpoint tests) - **Note: Tests require DB env vars**
  - [x] Type checking passes (`mypy app/`)
  - [x] Code formatting passes (`ruff check app/`)
  - [x] All endpoints return proper HTTP status codes
  - [x] Authentication middleware works correctly

## Phase 3: Celery & Task Processing (Week 3-4)

### Celery Infrastructure

- [ ] **Celery Setup**
  - [ ] Configure Celery app with Redis broker/backend
  - [ ] Set up task routing and worker configuration
  - [ ] Implement task retry configuration with exponential backoff
  - [ ] Add task result expiration settings
  - [ ] **Unit tests**: Test Celery configuration and basic task queueing

### Core Tasks

- [ ] **Scraping Tasks**
  - [ ] Implement `scrape_single_url` task with retry logic
  - [ ] Implement `process_individual_job` orchestration task
  - [ ] Add atomic job progress tracking (increment processed_urls)
  - [ ] Add job completion detection and status updates
  - [ ] Implement task timeout handling (5+ minutes per URL)
  - [ ] **Unit tests**: Test task logic, retry mechanisms, and progress tracking

### Task Orchestration

- [ ] **Job Processing Logic**
  - [ ] Create job submission workflow (queue individual URL tasks)
  - [ ] Add concurrent task limiting for BrightData
  - [ ] Implement task failure handling and error reporting
  - [ ] Add job cancellation logic
  - [ ] **Unit tests**: Test workflow orchestration and error handling

### Phase 3 Success Criteria (All Must Pass)

- [ ] **Validation Gate**
  - [ ] All unit tests pass (including Celery task tests)
  - [ ] Type checking passes (`mypy app/`)
  - [ ] Code formatting passes (`ruff check app/`)
  - [ ] Celery workers can be started successfully
  - [ ] Tasks can be queued and executed

## Phase 4: S3 Integration & Data Processing (Week 4-5)

### AWS S3 Integration

- [ ] **S3 Service Implementation**
  - [ ] Implement S3Service class using aioboto3 for async operations
  - [ ] Add raw JSON upload/download functionality
  - [ ] Implement S3 key generation strategy
  - [ ] Add S3 error handling and retries
  - [ ] **Unit tests**: Test S3 operations with mocked S3 client

### Data Caching & Deduplication

- [ ] **Caching Strategy**
  - [ ] Implement ScrapedData lookup before scraping
  - [ ] Add Redis caching for transformed results (1-hour TTL)
  - [ ] Create cache key generation strategy
  - [ ] Implement cache invalidation logic
  - [ ] **Unit tests**: Test caching logic and Redis operations

### Phase 4 Success Criteria (All Must Pass)

- [ ] **Validation Gate**
  - [ ] All unit tests pass (including S3 and caching tests)
  - [ ] Type checking passes (`mypy app/`)
  - [ ] Code formatting passes (`ruff check app/`)
  - [ ] S3 operations work with test buckets
  - [ ] Redis caching functions correctly

## Phase 5: Transformation Service (Week 5-6)

### On-Demand Processing

- [ ] **TransformationService Implementation**
  - [ ] Create TransformationService class
  - [ ] Implement `transform_individual_results` method
  - [ ] Add S3 data retrieval and parsing logic
  - [ ] Implement result caching with Redis
  - [ ] Add transformation error handling
  - [ ] **Unit tests**: Test transformation logic with mock data

### Dummy Data Processing

- [ ] **Placeholder Logic**
  - [ ] Create dummy data transformation logic for testing
  - [ ] Implement basic game-by-game analysis structure
  - [ ] Add series summary generation
  - [ ] Create JSON output format structure
  - [ ] **Unit tests**: Test dummy data processing and output format

### Phase 5 Success Criteria (All Must Pass)

- [ ] **Validation Gate**
  - [ ] All unit tests pass (including transformation tests)
  - [ ] Type checking passes (`mypy app/`)
  - [ ] Code formatting passes (`ruff check app/`)
  - [ ] Transformation service produces valid JSON output
  - [ ] End-to-end Individual mode workflow completes

## Phase 6: GFWL Mode (Week 6-7) - Future Phase

### GFWL Endpoints (To be implemented after Individual mode)

- [ ] **GFWL-Specific Endpoints**
  - [ ] `POST /api/v1/jobs/gfwl/submit-team` - Submit team data
  - [ ] `GET /api/v1/jobs/gfwl/{job_id}/discovered-players` - Get discovered players
  - [ ] `POST /api/v1/jobs/gfwl/{job_id}/confirm-players` - Confirm players
  - [ ] `GET /api/v1/jobs/gfwl/{job_id}/results` - Get GFWL results

### GFWL Tasks

- [ ] **GFWL Task Implementation**
  - [ ] Implement `process_gfwl_discovery` task
  - [ ] Implement `process_gfwl_profiles` task
  - [ ] Add player discovery from raw scraped data
  - [ ] Implement GFWL result transformation

## Phase 7: Production Deployment (Week 7-8)

### Railway Deployment

- [ ] **Infrastructure Setup**
  - [ ] Create Dockerfile with Playwright dependencies
  - [ ] Configure railway.toml for multi-service deployment
  - [ ] Set up PostgreSQL and Redis services on Railway
  - [ ] Configure environment variables for production

### BrightData Integration

- [ ] **Real Scraping Logic**
  - [ ] Integrate ReplayExtractor class into Celery tasks
  - [ ] Configure Playwright with BrightData proxy
  - [ ] Add proper browser automation setup
  - [ ] Implement captcha bypass handling

### Monitoring & Performance

- [ ] **Production Features**
  - [ ] Add comprehensive logging
  - [ ] Implement rate limiting middleware
  - [ ] Add performance monitoring
  - [ ] Create health check endpoints
  - [ ] Add error tracking and alerting

## Phase 8: Final Validation & Quality Assurance (Week 8-9)

### Comprehensive Testing

- [ ] **End-to-End Testing**
  - [ ] Test complete Individual mode workflow
  - [ ] Validate error handling across all components
  - [ ] Test concurrent job processing scenarios
  - [ ] Verify data consistency and caching

### Performance Validation

- [ ] **System Performance**
  - [ ] Validate S3 integration under realistic load
  - [ ] Test Redis caching performance with large datasets
  - [ ] Verify task retry mechanisms work correctly
  - [ ] Test system resource usage and limits

### Phase 8 Success Criteria (All Must Pass)

- [ ] **Final Validation Gate**
  - [ ] All unit tests pass across entire codebase
  - [ ] Type checking passes (`mypy app/`)
  - [ ] Code formatting passes (`ruff check app/`)
  - [ ] End-to-end workflows complete successfully
  - [ ] System meets performance requirements

## Critical Dependencies & Notes

### External Dependencies to Coordinate

- [ ] **ReplayExtractor Integration**: Wait for provided scraping logic
- [ ] **Result Format Specification**: Wait for JSON structure definition
- [ ] **GFWL Team Data Structure**: Wait for team data format

### Development Priorities

1. **Start with Individual Mode**: Complete end-to-end Individual mode before GFWL
2. **Use Dummy Data**: Implement with placeholder transformation logic initially
3. **Test Thoroughly**: Each phase should be fully tested before proceeding
4. **Deploy Early**: Get basic version deployed to Railway early for testing

### Performance Considerations

- Each URL scrape takes 1+ minutes
- Plan for concurrent processing limits
- Implement proper error handling for long-running tasks
- Design for horizontal scaling of Celery workers

## Success Criteria

### Phase 1-5 (Individual Mode MVP)

- [ ] **All validation gates passed for each phase**
- [ ] Users can submit Individual jobs with URLs
- [ ] Jobs process asynchronously with progress tracking
- [ ] Results are transformed on-demand and cached
- [ ] Results can be made publicly shareable
- [ ] System handles failures gracefully with retries
- [ ] **Continuous validation**: mypy, ruff, and pytest pass throughout

### Phase 6-8 (Production Ready)

- [ ] **All validation gates passed for each phase**
- [ ] GFWL mode fully implemented
- [ ] Real scraping integration working
- [ ] Deployed on Railway with monitoring
- [ ] Comprehensive unit test coverage (>90%)
- [ ] Performance meets requirements
- [ ] **Final validation**: All code quality checks pass

This todo list provides a clear roadmap for implementing the Duel Insights API according to the planning document specifications.
