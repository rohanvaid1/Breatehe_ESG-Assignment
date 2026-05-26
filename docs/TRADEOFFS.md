# Tradeoffs

1. **No automated currency conversion service**  
   For the prototype, currency is stored but not converted. Production should integrate FX rates by date.

2. **Simplified emission factors**  
   Factors are static and illustrative. A production system would use region-specific factors and versioned factor sets.

3. **No automated API pulls**  
   File upload is the ingestion mechanism for all sources to keep the workflow auditable and deterministic. In production, SAP/utility/travel APIs should be scheduled and reconciled.
