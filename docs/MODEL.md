# Data Model (Breathe ESG Ingestion)

## Goals
The schema is designed for multi-tenant ingestion, traceable normalization, and immutable audit history. Every record is tied to an organization, a source system, and an upload batch, with clear provenance from raw row to normalized record.

## Core entities

### Organizations & Users
- **Organization**: tenant boundary for data, users, and audit activity.
- **User**: belongs to a single organization with role-based access (**Admin**, **Analyst**, **Viewer**).

### Ingestion
- **SourceSystem**: SAP, Utility, or Travel feed definitions (global, reused across tenants).
- **UploadBatch**: file ingestion job with status, row counts, timestamps, and uploader.
- **RawRecord**: immutable raw CSV row with row number, raw hash, parse errors.

### Normalization & emissions
- **NormalizedRecord**: transformed data with standardized units, emission factors, and computed emissions.
- **EmissionCategory**: normalized category with scope mapping.
- **UnitConversion**: conversion multipliers for unit normalization.
- **PlantLookup**: SAP plant code mapping for tenant-specific plants.
- **AirportLookup**: airport codes and coordinates for distance estimation.

### Auditability
- **AnomalyFlag**: anomaly rule hits attached to a normalized record.
- **AnalystReview**: approval/rejection/edit/comment decisions (immutable history).
- **AuditLog**: append-only event log for normalization and review actions.

## Multi-tenancy
- All business data rows include `organization_id`.
- Non-superusers are filtered by `organization`.
- Organization data is isolated for uploads, raw records, normalized records, reviews, and audit logs.

## Audit strategy
- **RawRecord** is immutable input snapshot.
- **NormalizedRecord** tracks edits (`last_edited_by`, `last_edited_at`) and is locked after approval (`locked_at`).
- **AnalystReview** stores decisions and comment history, including before/after values.
- **AuditLog** tracks actions, actor, and delta payloads for every change.

## Normalization pipeline
1. **Schema mapping**: map CSV headers to canonical fields (supports German SAP headers).
2. **Unit normalization**: liters/gallons/kg/tonnes → standard units with `UnitConversion`.
3. **Emission classification**: derive Scope 1/2/3 and category.
4. **Emission calculation**: multiply normalized quantity by factor.
5. **Traceability**: store `conversion_metadata` and raw hash on the normalized record.

## Emission categorization
- **SAP fuel/procurement** → Scope 1 (fuel combustion) or Scope 3 (procurement).
- **Utility electricity** → Scope 2 (electricity consumption).
- **Corporate travel** → Scope 3 (business travel).

## Immutability & provenance
- Every normalized row references **raw record**, **upload batch**, **source system**, and **organization**.
- Edits are captured in **AnalystReview** and **AuditLog**, never overwritten silently.
