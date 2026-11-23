# Acme TutorNest (Demo Target Application)

TutorNest is a deliberately vulnerable demo application built for testing and demonstrating **DPDP Lens**, a cross-layer readiness auditor for India's Digital Personal Data Protection Act 2023 and DPDP Rules 2025.

## WARNING: DELIBERATELY VULNERABLE

- **Do NOT deploy this application to any public server or cloud environment.**
- **Do NOT use this code as a template or reference for production applications.**
- This repository contains intentionally planted privacy and security violations designed to test compliance auditing tools.
- All personal data, names, phone numbers, email addresses, PANs, and Aadhaar numbers in this repository and in `seed.py` are strictly synthetic and artificial. None belong to real individuals.
- All credentials and secrets in configuration files and source code (such as `JWT_SECRET` and `SECRET_KEY`) are dummy demo values.

## Purpose

This repository serves as a target repository connected to DPDP Lens via Slack (`/dpdp connect`) and CI/CD pipelines to demonstrate static code scanning, finding triage, and verified fix workflows.
