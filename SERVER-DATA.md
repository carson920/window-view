# Private window data

`data/` stays on the Node server. It is not imported into browser code or copied into `dist`.

- `GET /api/catalog`: estate, building, floor and flat selectors; no window coordinates.
- `GET /api/unit?estate=…&building=…&flat=…`: one selected unit's windows and building outline. No bulk endpoint.
- Switching selection clears the previous view while loading. Late responses cannot overwrite a newer selection.
- Window review now displays only the selected unit, so it does not fetch the whole estate in the background.

Development: `npm run dev`
Production: `npm run build`, then `npm start` (default localhost:5173; configure HOST/PORT behind your reverse proxy).
Deploy server/, data/, package.json and dist/ to the server. Only dist assets are served publicly. A static-only host such as GitHub Pages cannot run this API. Do not publish the data directory to a public repository; moving data to an API does not remove copies from existing Git history or old deployed builds.

The API prevents sending the entire dataset as a bundle, but is not an authorization system: requested coordinates remain visible and a public API can be enumerated. Add authenticated access and enforced per-account quotas if scraping prevention is required. Do not expose the Vite development server publicly.

## Login and query limits

Authentication is currently disabled by default (`AUTH_REQUIRED` is not `true`), so visitors can enter the main page and query units directly. The login/accounts implementation is retained. To turn the gate back on, set `AUTH_REQUIRED=true` on the Node process; then catalog/unit API requests require a login. Accounts are invitation-only, created by the operator; there is no public signup. Passwords use salted scrypt hashes. Sessions expire after 8 hours, use HttpOnly/SameSite=Strict cookies, and use Secure in production. Login/logout require a matching Origin. Logging in again invalidates the previous session for that account. Logout and removing an account invalidate access.

Each account gets 30 unit requests per minute and 100 per UTC day. Invalid unit lookups also count. Quotas are persisted with accounts in `.private/auth.json`; logging out or restarting does not reset them. Login attempts are limited to 5 per IP per 15 minutes (in memory); behind the included proxy that is a shared limit, since untrusted forwarded IP headers are deliberately ignored. API errors never return window data. This deters bulk scraping, not screenshots or copying legitimately viewed data.

Local account management:

```
npm run user:add -- yourname
npm run user:remove -- yourname
```

The add command generates and displays a password once. Store it in your password manager. `.private/` is excluded from Git, Docker context and Vite serving. If an initial admin was bootstrapped, its generated credential is in `.private/initial-login.txt`; move it into your password manager and delete that bootstrap file afterwards.

## Production deployment (single app process)

Point a domain to your server, install Docker Compose, then run:

```
DOMAIN=your.domain docker compose up -d --build
DOMAIN=your.domain docker compose exec app npm run user:add -- yourname
```

Caddy terminates HTTPS; only ports 80/443 are public. The Node app is internal, Secure cookies are required, and APP_ORIGIN must match the HTTPS domain. Accounts/quotas persist in the accounts volume; keep a private backup. Do not scale the app to multiple workers/replicas without replacing file quotas and memory sessions with a shared transactional store. Production startup fails closed without an HTTPS APP_ORIGIN. The runtime needs no npm packages; Vite is build-time only.

For a manually managed HTTPS reverse proxy: `APP_ORIGIN=https://your.domain npm run start:production`. Do not use `npm run dev` for public hosting. Deployment files are provided; no remote host or DNS has been provisioned by this change.
