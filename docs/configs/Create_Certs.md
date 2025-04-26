# Generating Certificates for Bumper

When you clone this Git repository, the certificate‑generation script is already in place. Simply run it to create all required certificates in the `certs/` directory.

---

## \\\\ Script Location & Purpose

The project includes a script at `scripts/create-cert.sh`. This script:

-   Generates a root CA (`ca.key` + `ca.crt`)
-   Generates a server certificate (`bumper.key` + `bumper.crt`)
-   Produces `ca.pem` by concatenating server and CA certs (for mitmproxy)

If you already have your own certificates, copy them into `certs/`:

-   **Bumper needs**: `ca.crt`, `bumper.key`, `bumper.crt` (for server/client TLS)
-   **mitmproxy needs**: `ca.pem` (combined PEM with key + cert)

---

## \\\\ Execute the Script

Run it from the project root:

```bash
$./scripts/create-cert.sh
```

On first run, you’ll see progress messages and end up with:

-   `certs/ca.key`  – Root CA private key
-   `certs/ca.crt`  – Root CA certificate
-   `certs/bumper.key` – Server private key
-   `certs/bumper.crt` – Server certificate
-   `certs/ca.pem`  – Combined PEM (for mitmproxy)

If files already exist, the script will skip regeneration to avoid overwriting.

---

## \\\\ Use in Your Workflow

-   **Bumper application**: Point to `certs/bumper.crt` and `certs/ca.crt` (or set `BUMPER_CERT_PATH` to `certs/ca.pem` if it reads PEM form).
-   **mitmproxy**: Mount or reference `certs/ca.pem` as your custom CA for intercepting traffic.

For example, in Docker:

```bash
$docker run --rm -it \
  -v $PWD/certs/ca.pem:/home/mitm/ca.pem:ro \
  mitmproxy/mitmproxy mitmweb --certs '*=/home/mitm/ca.pem' [...]
```

---

## \\\\ Python Configuration

Bumper’s Python code reads certificate paths and data directories from environment variables. You can override defaults by setting:

-   `BUMPER_DATA`     (Project root)/data
-   `BUMPER_CERTS`   (Project root)/certs
-   `BUMPER_CA`      CA certificate (`ca.crt`)
-   `BUMPER_CERT`    Server certificate (`bumper.crt`)
-   `BUMPER_KEY`     Server key (`bumper.key`)

Adjust these in your shell or CI environment if you need to load certificates from custom locations. The combined `ca.pem` is only required by mitmproxy and not used by Bumper’s Python code.
