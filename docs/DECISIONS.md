# Architecture Decisions

## Source formats & ingestion
- **SAP**: Chose a flat CSV export representing a common ECC/BW extract (e.g., MB51/SE16 style). This matches what sustainability teams often get via ad‑hoc exports and allows German headers. Decided against IDoc/OData for this prototype to keep uploads realistic but file-based.
- **Utility**: Chose portal CSV export instead of PDF bills, because ingestion needs line-level usage and billing periods. CSV is common in facility portals and supports automation.
- **Travel**: Chose Concur/Navan style CSV export because travel platforms commonly provide export reports and it captures mode-specific data.

## Normalization pipeline
- **Unit normalization at ingestion time**: ensures normalized quantities are consistent for analytics and anomalies.
- **Store raw + normalized**: raw rows remain immutable, while normalized rows are editable with a tracked audit history.
- **Emission factors as configurable data**: factors are stored in code constants for the prototype and should be externalized later.

## Multi-tenancy
- **Organization as tenant root**: all business data includes `organization_id` for tenant isolation.
- **Single-org users**: user accounts are bound to one organization for simplicity and audit clarity.

## Review & audit
- **Immutable audit trail**: edits create AnalystReview + AuditLog entries. Approved records are locked.
- **Approval workflow**: approval/rejection is explicit and stored separately from the normalized record’s status.

## Storage
- **PostgreSQL-first schema**: JSON fields for raw payloads while keeping normalized columns for analytics.
- **UUIDs everywhere**: stable identifiers across ingestion, review, and audit logs.

## API
- **DRF + JWT**: standard, tested authentication and permissions model.
- **Filtering & pagination**: all list endpoints are filterable to support analyst workflows.

## Frontend
- **React + Vite + Tailwind**: fast dev environment and consistent enterprise UI.
- **React Query**: reliable data fetching with caching and refetching on demand.
- **Zustand**: simple, explicit auth state without over-engineering.

## What I would ask the PM
- Should approvals be reversible or require a new correction batch?
- What regulatory guidance defines “locking” after approval for audit?
- Which emission factor library should be authoritative for production?
