# Purplix is in early alpha
Please report any issues.

&nbsp;

<div align="center">
  <img src="https://i.imgur.com/1pkrLq9.png" width="100px" />
  <h1>Purplix</h1>
  <quote>
    Purplix is an open-source collection of tools dedicated to user privacy and creating trust with your audience.
  </quote>
</div>

&nbsp;

# About
## What is Purplix Survey?
![Purplix survey preview](https://files.catbox.moe/13yjgb.gif)

Purplix Survey is a free & open source survey tool what can't read your questions & answers.

With traditional surveys you are one data breach, one rouge employee or one government warrant away from all your user's data being exposed. Purplix uses modern encryption techniques to keep your user's data away from any actors.

### How does it work?
#### Questions, Descriptions & Title encryption

When you create a survey, we encrypt your title, descriptions & questions with a secret key. This key is then stored encrypted in your keychain. When you share your survey with others using a link, the key is stored in the link for your participants. This ensures that your survey questions can only be read by your participants.

#### Answers encryption
Every survey has its own unique key pair. The private key is securely stored in your keychain, while the public key is used by users to encrypt their answers. Only you have the means to decrypt the answers once they are submitted. When you share a survey, we include a hash of the public key in the URL to prevent man-in-the-middle attacks.

#### Preventing spam & multiple submissions
Survey creators can opt-in to use VPN blocking, requiring a Purplix account or IP blocking. IP blocking works by storing a hash of the IP salted with a key not stored by Purplix, minimizing the attack surface of tracking submission locations, these IP hashes are only stored for 7 days or until the survey closes. Users will always be informed when any of these features are enabled.

## What is Purplix Canary?
![Image of canary site](https://i.imgur.com/c3HUe1C.png)
Purplix Canary is a free & open source warrant canary tool what helps you to build trust with your users.

It allows you to inform users cryptographically if your site has been compromised, seized or raided by anyone.

### How does it work?
#### Site verification
Purplix uses DNS records to verify the domain the canary is for, giving your users confidence they are trusting the right people.

#### Canary signatures
Each domain is associated with a unique key pair. The private key is generated locally and securely stored within the owner's keychain. When a user visits a canary from a specific domain for the first time, their private key is used to sign the public key. This signed version of the public key is then automatically employed for subsequent visits, effectively mitigating man-in-the-middle attacks and ensuring the trustworthiness of canary statements from the respective domain.

#### Files
Canaries can include signed documents to help users further understand a situation.

#### Notifications
Users are automatically notified on the event of a new statement being published.

# Setup
## Production
In order to self-host Purplix, you must be conformable using Docker, using some sort of reverse proxy & following documentation.

### Images used
- `wardpearce/purplix-backend:latest` - Backend for Purplix.
- `wardpearce/purplix-frontend:latest` - Frontend for Purplix (Optional if using Vercel.)
- `wardpearce/purplix-docs:latest` - OpenAPI schema docs for Purplix.
- `mongo:latest` - Database for Purplix.
- `redis:latest` - Cache for Purplix.
- `serjs/go-socks5-proxy:latest` - Sock5 proxy for Purplix untrusted webhooks.

### Configuration
I recommend looking at the example docker compose to learn what the values should be.

#### wardpearce/purplix-frontend:latest
- Set `VITE_MCAPTCHA_ENABLED`, `VITE_MCAPTCHA_API` & `VITE_MCAPTCHA_SITE_KEY` if mCaptcha in use.
- `VITE_BLOCKSTREAM_API` is use to get the most recent BTC block hash, most likely you should set this as `https://blockstream.info/api`

#### wardpearce/purplix-docs:latest
- Set `VITE_API_SCHEMA_URL` as the reverse proxied URL for the API, e.g. `https://{myurl.tld}/api/schema/openapi.json`.

#### serjs/go-socks5-proxy:latest
 - `PROXY_USER`: proxy username.
 - `PROXY_PASSWORD`: proxy password.

#### wardpearce/purplix-backend:latest
- `purplix_untrusted_request_proxy`: This variable should be set to the reverse proxied SOCKS5 proxy. It determines the proxy server used for handling untrusted requests.

- `purplix_disable_registration`: Set this variable to true if you want to disable user registration. If set to false, registration will be enabled.

- `purplix_csrf_secret`: This variable should contain a randomly generated 32-character secret key used for Cross-Site Request Forgery (CSRF) protection. If you want the secret to be generated randomly, you can remove this variable from your configuration.

- `purplix_proxy_urls`: This variable should contain a JSON object with reverse proxied URLs for different endpoints. Ensure there is no trailing slash in the URLs. For example, it includes frontend, backend, and documentation URLs.

- `purplix_s3`: These settings are related to the Amazon S3 storage configuration. You need to specify your S3 region, secret access key, access key ID, bucket name, folder, download URL, and optionally an endpoint URL and chunk size.

- `purplix_mcaptcha`: These settings are for configuring mCaptcha, a CAPTCHA service. You should provide the verification URL, site key, and account secret, which are typically obtained from the mCaptcha website you host.

- `purplix_jwt`: This variable should contain a randomly generated 32-character secret key used for JSON Web Token (JWT) authentication. If you want the secret to be generated randomly, you can remove this variable from your configuration. Additionally, you can specify the number of days until JWT tokens expire.

- `purplix_ntfy`: Configure this variable with the URL and topic length for Ntfy, a notification service.

- `purplix_domain_verify`: These settings are for domain verification. You can specify a prefix and timeout for verification.

- `purplix_proxycheck`: Configuration for Proxycheck, which may include an API key and the URL for the service.

- `purplix_smtp`: These settings are for configuring the SMTP server, including the host, port, username, password, and sender email address.

- `purplix_enabled`: This variable contains settings for enabling or disabling certain features, such as surveys and canaries.

- `purplix_mongo`: Configuration for connecting to a MongoDB database, including the host, port, and collection name.

- `purplix_redis`: Configuration for connecting to a Redis database, including the host, port, and database number.


### Compose example
```yaml
version: "3"
services:
  purplix-frontend:
      container_name: purplix-frontend
      image: wardpearce/purplix-frontend:latest
      restart: unless-stopped
      environment:
          VITE_MCAPTCHA_ENABLED: true
          VITE_MCAPTCHA_API: https://mcaptcha.purplix.io/api/v1
          VITE_MCAPTCHA_SITE_KEY: 691wu6nlaYfeNl1XyYYYfRYYjIp4HQw6
          VITE_THEME: "#8749f4"
          VITE_SITE_NAME: "Purplix"
          VITE_BLOCKSTREAM_API: https://blockstream.info/api
      ports:
          - "8866:80"

  purplix-docs:
      container_name: purplix-docs
      image: wardpearce/purplix-docs:latest
      restart: unless-stopped
      environment:
          VITE_API_SCHEMA_URL: https://localhost/api/schema/openapi.json
      ports:
          - "8866:80"

  purplix-backend:
      container_name: purplix-backend
      image: wardpearce/purplix-backend:latest
      restart: unless-stopped
      ports:
          - "8865:80"
      environment:
          purplix_untrusted_request_proxy: "sock5://"

          purplix_disable_registration: false

          purplix_csrf_secret: "!!change_me!!"

          # ProxiedUrls Settings
          # No trailing slash!
          purplix_proxy_urls: |
              {
                  "frontend": "https://localhost",
                  "backend": "https://localhost/api",
                  "docs": "https://docs.localhost"
              }

          # S3 Settings
          purplix_s3: |
              {
                  "region_name": "your_region",
                  "secret_access_key": "your_secret_key",
                  "access_key_id": "your_access_key_id",
                  "bucket": "your_bucket",
                  "folder": "purplix",
                  "download_url": "your_download_url",
                  "endpoint_url": null,
                  "chunk_size": 655400
              }

          # mCaptcha Settings
          purplix_mcaptcha: |
              {
                  "verify_url": "https://mcaptcha.purplix.io/api/v1/pow/verify",
                  "site_key": "691wu6nlaYfeNl1XyYYYfRYYjIp4HQw6",
                  "account_secret": "f0bm6QvcbZoddSqeeTXoY4BvdGaMmOv7"
              }

          # Jwt Settings
          purplix_jwt: |
              {
                  "secret": "!!change_me!!",
                  "expire_days": 30
              }

          # Ntfy Settings
          purplix_ntfy: |
              {
                  "url": "your_ntfy_url",
                  "topic_len": 32
              }

          # DomainVerify Settings
          purplix_domain_verify: |
              {
                  "prefix": "purplix.io__verify=",
                  "timeout": 60
              }

          # Proxycheck Settings
          purplix_proxycheck: |
              {
                  "api_key": "",
                  "url": "https://proxycheck.io/v2/"
              }

          # Smtp Settings
          purplix_smtp: |
              {
                  "host": "your_smtp_host",
                  "port": your_smtp_port,
                  "username": "",
                  "password": "",
                  "email": "your_email@example.com"
              }

          # Enabled Settings
          purplix_enabled: |
              {
                  "survey": true,
                  "canaries": true
              }

          # MongoDB Settings
          purplix_mongo: |
              {
                  "host": "purplix-mongo",
                  "port": 27017,
                  "collection": "purplix"
              }

          # Redis Settings
          purplix_redis: |
              {
                  "host": "purplix-redis",
                  "port": 6379,
                  "db": 0
              }

  purplix-ntfy:
    image: binwiederhier/ntfy
    container_name: ntfy
    command:
      - serve
    environment:
      - TZ=UTC
    user: 1000:1000
    volumes:
      - /var/cache/ntfy:/var/cache/ntfy
      - /etc/ntfy:/etc/ntfy
    ports:
      - 9997:80
    healthcheck:
        test: ["CMD-SHELL", "wget -q --tries=1 https:/example.com/v1/health -O - | grep -Eo '\"healthy\"\\s*:\\s*true' || exit 1"]
        interval: 60s
        timeout: 10s
        retries: 3
        start_period: 40s
    restart: unless-stopped

  purplix-mongo:
    image: mongo:latest
    container_name: purplix-mongo
    restart: unless-stopped
    environment:
      MONGODB_DATA_DIR: /data/db
      MONDODB_LOG_DIR: /dev/null
    volumes:
      - purplix-mongo-data:/data/db
  
  purplix-redis:
    image: redis:latest
    container_name: purplix-redis
    restart: unless-stopped
  
  purplix-socks5:
    restart: unless-stopped
    image: serjs/go-socks5-proxy:latest
    environment:
      PROXY_USER: someuser
      PROXY_PASSWORD: somepass
      PROXY_PORT: 1080
    ports:
    - "1080:1080"

  mcaptcha:
    image: mcaptcha/mcaptcha:latest
    ports:
      - 7000:7000
    restart: unless-stopped
    environment:
      DATABASE_URL: postgres://postgres:password@mcaptcha_postgres:5432/postgres
      MCAPTCHA_REDIS_URL: redis://mcaptcha_redis/
      RUST_LOG: debug
      PORT: 7000
      MCAPTCHA_SERVER_DOMAIN: mcaptcha.example.com
      MCAPTCHA_COMMERCIAL: false
      MCAPTCHA_ALLOW_REGISTRATION: false
      MCAPTCHA_ALLOW_DEMO: false
    depends_on:
      - mcaptcha_postgres
      - mcaptcha_redis

  mcaptcha_postgres:
    image: postgres:13.2
    restart: unless-stopped
    volumes:
      - purplix-mcaptcha-data:/var/lib/postgresql/
    environment:
      POSTGRES_PASSWORD: password
      PGDATA: /var/lib/postgresql/data/mcaptcha/

  mcaptcha_redis:
    image: mcaptcha/cache:latest
    restart: unless-stopped

volumes:
    purplix-mongo-data:
    purplix-mcaptcha-data:
```
