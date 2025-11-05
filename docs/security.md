# Security Overview (SPIS MVP)

### 1. Authentication & Authorization
- Use **JWT (JSON Web Tokens)** for API authentication.
- Enforce **HTTPS** in production.
- All endpoints must require authentication except `/api/health/` and `/api/auth/login/`.

### 2. Data Protection
- **PII (Personally Identifiable Information)** such as user names, emails, and credentials will be **encrypted at rest**.
- Sensitive environment variables stored in `.env` files (never committed).
- Access to production DB limited by IP and IAM roles.

### 3. Backups & Storage
- Nightly **PostgreSQL backups** to **AWS S3**.
- All S3 objects encrypted using **AES-256 server-side encryption**.

### 4. Logging & Monitoring
- API access logs stored securely (rotated weekly).
- Error logs avoid storing personal or sensitive data.

### 5. Future Enhancements
- Add role-based access control (admin, pharmacist).
- Integrate two-factor authentication for admin accounts.
