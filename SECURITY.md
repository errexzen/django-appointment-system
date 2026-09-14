# Security Policy

## Supported versions
Active branch receives security fixes.

## Reporting a vulnerability
Please open a private security report with reproduction steps and impact.
Do not publish sensitive exploit details publicly before triage.

## Security practices
- Environment-based secrets
- JWT refresh rotation and blacklist
- Tenant isolation through scoped querysets and permissions
- CSRF/session protections for web endpoints
- Audit logs for sensitive actions
