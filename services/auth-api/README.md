# Auth API

SQLite-backed login and logout for the operations dashboard. User creation is
SQL-only; there are no registration, user-management, or password-reset APIs.

## Run

From this directory, with the repository virtual environment activated:

```sh
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8003
```

Startup creates `data/auth.sqlite3`. Set `AUTH_DATABASE_PATH` to use a different
database file. Keep the database private, backed up, and outside version control.

## Create a User

Generate a password hash locally (the password prompt does not echo):

```sh
python -m app.passwords
```

Open the database after the service has started:

```sh
sqlite3 data/auth.sqlite3
```

Insert a user, replacing the hash placeholder with the full generated value:

```sql
INSERT INTO users (id, username, password_hash)
VALUES ('operator-001', 'operator', '<generated-password-hash>');
```

Store only generated hashes, never plaintext passwords. To disable an account
and revoke its sessions:

```sql
BEGIN;
UPDATE users SET active = 0 WHERE id = 'operator-001';
DELETE FROM sessions WHERE user_id = 'operator-001';
COMMIT;
```

After changing a password through SQL, delete that user's sessions as well.

## API

- `POST /login` with JSON `{"username":"operator","password":"..."}`
  returns `userId`, a UUID `sessionId`, `expiresAt`, and an opaque `token`.
- `POST /login` with `Authorization: Bearer <token>` and no body validates the
  existing session and returns its identity and expiry, without extending it.
- `POST /logout` with the bearer token revokes that session; repeated logout is
  safe and returns HTTP 204.

Sessions expire after eight hours. Only SHA-256 hashes of session tokens are
stored. Passwords use salted PBKDF2-HMAC-SHA256 with 600,000 iterations.

## Dashboard

Run the dashboard from `uis/backoffice/dashboard` with `npm run dev`. It defaults
to this API at `http://127.0.0.1:8003`; override the server-only `AUTH_API_URL`
environment variable if needed. Open `/login` to sign in.

The dashboard uses Next.js server actions, stores the token in an HTTP-only,
SameSite=Lax cookie, and validates it before fetching dashboard data. Cookies
are Secure in production, so deploy the dashboard behind HTTPS. The auth API
does not need browser CORS access; keep it on a private network and terminate
TLS for any traffic crossing an untrusted network.

This is a minimal internal login service, not a production identity provider.
Apply login rate limiting at your gateway before exposing it publicly. Other
backoffice applications and APIs are not protected by this dashboard login.
