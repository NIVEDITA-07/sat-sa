# Public Dataset Support & Source Ingestion

This directory handles varied source formats (e.g., Public SOC Samples, SIEM Exports).

**Important Principles:**
1. **Semantic Mapping Only**: Public datasets may have fields that do not map directly to SAT-SA. Only semantically valid fields should be mapped (e.g., `priority` -> `severity`).
2. **Never Falsify Data**: Missing supervisory evidence must remain `NOT_AVAILABLE`. Do not automatically convert missing fields to `No`.
3. **Demonstration Only**: Any public dataset included here is used strictly to demonstrate ingestion, normalization, and evidence coverage architecture. It is NOT intended to claim or imply that it represents a real NCIIPC CSE or actual national infrastructure.
