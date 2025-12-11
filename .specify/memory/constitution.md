<!--
SYNC IMPACT REPORT - Constitution v1.0.0
========================================
Version Change: [NONE] → 1.0.0 (Initial constitution creation)
Date: 2025-12-09

Modified Principles:
- NEW: I. Simplicity First
- NEW: II. Clean Code & Readability
- NEW: III. Modular Architecture
- NEW: IV. Database Optimization
- NEW: V. Hybrid Storage Strategy

Added Sections:
- Core Principles (5 principles)
- Data Persistence Standards
- Development Workflow
- Governance

Removed Sections:
- None (initial version)

Templates Requiring Updates:
✅ .specify/templates/plan-template.md - Constitution Check section aligns with new principles
✅ .specify/templates/spec-template.md - Requirements structure supports data-centric features
✅ .specify/templates/tasks-template.md - Phase organization supports modular development

Follow-up TODOs:
- None - all placeholders filled

Impact Summary:
This is the initial constitution establishing core principles for the Turistando tourism
management system. All principles focus on data persistence, clean architecture, and
database optimization for hybrid SQL/NoSQL storage patterns.
-->

# Turistando Constitution

## Core Principles

### I. Simplicity First

Every component, API, and data structure MUST be designed with simplicity as the primary goal. Complex solutions are permitted only when simpler alternatives cannot meet functional requirements.

**Rules**:
- MUST start with the simplest possible implementation that satisfies requirements
- MUST avoid premature optimization unless performance requirements demand it
- MUST document any deviation from simple patterns with explicit justification
- MUST prefer standard library features over external dependencies when feasible
- SHOULD aim for code that can be understood by developers unfamiliar with the codebase within 15 minutes

**Rationale**: Tourism data management involves clear CRUD operations, file handling, and queries. Overengineering creates maintenance burden without delivering user value. Simple code reduces bugs, accelerates onboarding, and facilitates database optimization.

### II. Clean Code & Readability

Code MUST be self-documenting, consistent, and readable. Prioritize clarity over cleverness.

**Rules**:
- MUST use descriptive variable and function names that reveal intent (e.g., `findTouristSpotsByCity` not `find`)
- MUST follow consistent naming conventions across backend and frontend
- MUST limit function length to 50 lines; methods exceeding this require refactoring justification
- MUST include inline comments only when the "why" is non-obvious (the code explains "what")
- MUST use type hints/annotations in Python backend and TypeScript in frontend
- MUST format code with automated tools (black, prettier) - no exceptions

**Rationale**: Multiple developers and database technologies require consistent patterns. Clean code reduces cognitive load during debugging queries, file operations, and API integrations. Readability directly impacts bug detection and database schema evolution.

### III. Modular Architecture

System components MUST be loosely coupled and highly cohesive. Each module has a single, well-defined responsibility.

**Rules**:
- MUST separate concerns: models, services, repositories, controllers, views
- MUST implement repository pattern for all database access (SQL and NoSQL)
- MUST encapsulate business logic in service layer, never in controllers or views
- MUST design APIs with clear contracts (input/output schemas validated)
- MUST ensure frontend components are reusable and independent
- MUST use dependency injection for testability and flexibility

**Rationale**: Hybrid database architecture (relational + NoSQL) demands clear separation. Repository pattern allows swapping PostgreSQL for MySQL or MongoDB for Redis without affecting business logic. Modular design enables independent testing of CRUD, file uploads, and search features.

### IV. Database Optimization

All data access MUST be optimized for performance, scalability, and maintainability. Database choice MUST match data characteristics.

**Rules**:
- MUST use relational database (PostgreSQL recommended) for structured entities: tourist spots, users, accommodations
- MUST use NoSQL (MongoDB/Redis recommended) for semi-structured data: comments, ratings, activity logs
- MUST index all foreign keys and frequently queried fields (city, rating, type)
- MUST use connection pooling for both SQL and NoSQL connections
- MUST implement query pagination for list endpoints (max 50 results per page)
- MUST avoid N+1 queries; use eager loading or batch fetching
- MUST measure query performance; endpoints exceeding 200ms require optimization
- MUST implement database migrations with rollback capability

**Rationale**: Tourism data has predictable access patterns. Structured data (spots, accommodations) benefits from relational integrity. Unstructured data (comments, photos) benefits from NoSQL flexibility. Proper indexing and pagination ensure system scales beyond 10,000 tourist spots.

### V. Hybrid Storage Strategy

File storage and database selection MUST follow data nature and access patterns.

**Rules**:
- MUST store images on disk/object storage (not in database); store only file paths in database
- MUST organize uploaded files: `/uploads/{spot_id}/{timestamp}_{filename}`
- MUST validate file types (JPEG, PNG, WebP) and size limits (max 5MB per image)
- MUST generate thumbnails for image listings (async processing recommended)
- MUST use relational DB for entities requiring transactions and referential integrity
- MUST use NoSQL for high-write, flexible-schema data (comments, logs, user activity)
- MUST implement caching for frequently accessed read-heavy data (spot details, search results)

**Rationale**: Storing images in databases bloats tables and slows queries. Filesystem + metadata pattern is industry standard for media. Hybrid storage leverages SQL's ACID properties for critical data while exploiting NoSQL's speed for comments/ratings that tolerate eventual consistency.

## Data Persistence Standards

### Schema Design

- MUST normalize relational schema to 3NF minimum; denormalization requires performance justification
- MUST use UUID primary keys for distributed system compatibility
- MUST define explicit foreign key constraints with ON DELETE/UPDATE behavior
- MUST document entity relationships in ER diagrams (kept in `/docs/data-model.md`)
- SHOULD use soft deletes (deleted_at timestamp) for audit trails on user-generated content

### Data Integrity

- MUST validate data at API layer (request validation) and database layer (constraints)
- MUST use database transactions for multi-table operations (e.g., creating spot + initial photo record)
- MUST implement idempotency for non-GET endpoints (prevent duplicate submissions)
- MUST sanitize user inputs to prevent SQL injection and NoSQL injection
- MUST backup databases daily; retain backups for 30 days minimum

### Query Patterns

- MUST implement full-text search for spot names and descriptions (PostgreSQL `tsvector` or Elasticsearch)
- MUST support filtering by multiple criteria: city, rating, type, availability
- MUST implement geospatial queries if location-based search is required (PostGIS extension)
- MUST log slow queries (>200ms) for optimization analysis
- SHOULD implement read replicas for heavy read workloads

## Development Workflow

### Code Quality Gates

- MUST pass linter checks (flake8/pylint for Python, ESLint for JavaScript)
- MUST maintain 80%+ code coverage for service and repository layers (tests required)
- MUST pass all unit and integration tests before merge
- MUST review database migrations for index creation and backward compatibility
- SHOULD conduct code reviews focusing on principle adherence

### Testing Strategy

- MUST write unit tests for business logic (services)
- MUST write integration tests for repository layer (actual database calls with test DB)
- MUST write contract tests for API endpoints (request/response validation)
- SHOULD write E2E tests for critical user journeys (create spot, upload photo, add comment)
- MUST use test fixtures to seed test databases with consistent data

### Documentation Requirements

- MUST document all API endpoints: method, path, request body, response schema, status codes
- MUST maintain ER diagram reflecting current database schema
- MUST document environment variables and configuration
- SHOULD include setup instructions for local development (README.md)
- SHOULD document deployment procedures and database migration steps

## Governance

This constitution supersedes all other development practices. All code, architectural decisions, and reviews MUST verify compliance with these principles.

**Amendment Process**:
- Proposed changes MUST include rationale and impact analysis
- Breaking changes to principles require review and explicit approval
- MINOR version increments for new principles/sections
- PATCH version increments for clarifications and wording improvements
- MAJOR version increments for fundamental principle changes or removals

**Enforcement**:
- All pull requests MUST be reviewed against constitution principles
- Complexity and deviations from principles MUST be explicitly justified in PR descriptions
- Constitution violations MUST be resolved before merge approval
- Recurring violations indicate principle refinement is needed

**Version**: 1.0.0 | **Ratified**: 2025-12-09 | **Last Amended**: 2025-12-09
