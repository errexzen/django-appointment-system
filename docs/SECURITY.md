# Security Checklist

- [x] Custom user model with email login
- [x] JWT rotation and blacklist
- [x] Tenant-scoped querysets and role checks
- [x] Audit logging for key actions
- [x] Environment-based config
- [x] CSRF middleware enabled
- [x] XSS-safe Django templates
- [x] Clickjacking and content type protections
- [x] Password validation enabled
- [x] Deploy checks integrated
- [ ] Enforce HSTS in production (`SECURE_HSTS_SECONDS`)
- [ ] Set secure cookies and SSL redirect in production env
- [ ] Integrate login rate limiting package for stricter lockout policy
