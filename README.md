## Purplix is still in development!
[https://github.com/users/WardPearce/projects/1](https://github.com/users/WardPearce/projects/1)

# Purplix is in early alpha
Please report any issues.

&nbsp;

<div align="center">
  <img src="https://i.imgur.com/1pkrLq9.png" width="100px" />
  <h1>Purplix</h1>
  <blockquote>
    Purplix is an open-source collection of tools dedicated to user privacy and creating trust with your audience.
  </blockquote>
</div>

&nbsp;

# About
## What is Purplix Survey?
![Purplix survey preview](https://files.catbox.moe/13yjgb.gif)

Purplix Survey is a free & open-source survey tool that can't read your questions and answers.

With traditional surveys, you are one data breach, one rogue employee, or one government warrant away from all your users' data being exposed. Purplix uses modern encryption techniques to keep your users' data away from any actors.

### How does it work?
#### Questions, Descriptions & Title Encryption

When you create a survey, we encrypt your title, descriptions, and questions with a secret key. This key is then stored encrypted in your keychain. When you share your survey with others using a link, the key is stored in the link for your participants. This ensures that your survey questions can only be read by your participants.

#### Answers Encryption
Every survey has its own unique key pair. The private key is securely stored in your keychain, while the public key is used by users to encrypt their answers. Only you have the means to decrypt the answers once they are submitted. When you share a survey, we include a hash of the public key in the URL to prevent man-in-the-middle attacks.

#### Preventing Spam & Multiple Submissions
Survey creators can opt-in to use VPN blocking, requiring a Purplix account, or IP blocking. IP blocking works by storing a hash of the IP salted with a key not stored by Purplix, minimizing the attack surface of tracking submission locations. These IP hashes are only stored for 7 days or until the survey closes. Users will always be informed when any of these features are enabled.

## What is Purplix Canary?
![Image of canary site](https://i.imgur.com/c3HUe1C.png)
Purplix Canary is a free & open-source warrant canary tool that helps you build trust with your users.

It allows you to inform users cryptographically if your site has been compromised, seized, or raided by anyone.

### How does it work?
#### Site Verification
Purplix uses DNS records to verify the domain the canary is for, giving your users confidence that they are trusting the right people.

#### Canary Signatures
Each domain is associated with a unique key pair. The private key is generated locally and securely stored within the owner's keychain. When a user visits a canary from a specific domain for the first time, their private key is used to sign the public key. This signed version of the public key is then automatically employed for subsequent visits, effectively mitigating man-in-the-middle attacks and ensuring the trustworthiness of canary statements from the respective domain.

#### Files
Canaries can include signed documents to help users further understand a situation.

#### Notifications
Users are automatically notified on the event of a new statement being published.

# Have any questions?
[Join our Matrix space](https://matrix.to/#/#ward:matrix.org)

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


#### mcaptcha/mcaptcha:latest
[Docs](https://github.com/mCaptcha/mCaptcha/blob/master/docs/CONFIGURATION.md)

#### binwiederhier/ntfy
[Docs](https://docs.ntfy.sh/)

### Compose example
```yaml
version: "3"
services:
  purplix-backend:
      container_name: purplix-backend
      image: wardpearce/purplix-backend:latest
      restart: unless-stopped
      ports:
          - "8865:80"
      networks:
        - purplix-network
      depends_on:
        - purplix-mongo
      environment:
          # Redis Settings
          purplix_redis: '{"host": "purplix-redis", "port": 6379, "db": 0}'

          purplix_untrusted_request_proxy: "socks5://purplix:password@address:1080"

          purplix_disable_registration: false

          purplix_csrf_secret: "!!changeme!!"

          # ProxiedUrls Settings
          # No trailing slash!
          purplix_proxy_urls: |
              {
                  "frontend": "https://purplix.io",
                  "backend": "https://purplix.io/api",
                  "docs": "https://docs.purplix.io"
              }

          # S3 Settings
          purplix_s3: |
              {
                  "region_name": "",
                  "secret_access_key": "",
                  "access_key_id": "",
                  "bucket": "",
                  "folder": "purplix",
                  "download_url": "",
                  "endpoint_url": "",
                  "chunk_size": 655400
              }

          # mCaptcha Settings
          purplix_mcaptcha: |
              {
                  "verify_url": "https://mcaptcha.example.com/api/v1/pow/verify",
                  "site_key": "",
                  "account_secret": ""
              }

          # Jwt Settings
          purplix_jwt: |
              {
                  "secret": "",
                  "expire_days": 30
              }

          # Ntfy Settings
          purplix_ntfy: |
              {
                  "url": "https://ntfy.example.com",
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
                  "host": ",
                  "port": 25,
                  "username": "",
                  "password": "",
                  "email": ""
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


  purplix-mongo:
    image: mongo:latest
    container_name: purplix-mongo
    restart: unless-stopped
    environment:
      MONGODB_DATA_DIR: /data/db
      MONDODB_LOG_DIR: /dev/null
    volumes:
      - purplix-mongo-data:/data/db
    networks:
      - purplix-network

  purplix-socks5:
    restart: unless-stopped
    image: serjs/go-socks5-proxy:latest
    environment:
      PROXY_USER: purplix
      PROXY_PASSWORD: "!!changeme!!"
      PROXY_PORT: 1080
    ports:
    - "1080:1080"

  purplix-redis:
    image: redis:latest
    restart: unless-stopped
    container_name: purplix-redis
    networks:
      - purplix-network

  purplix-mcaptcha-redis:
    image: mcaptcha/cache:latest
    restart: unless-stopped
    networks:
      - purplix-network

  purplix-mcaptcha:
    image: mcaptcha/mcaptcha:latest
    ports:
      - 7000:7000
    restart: unless-stopped
    environment:
      DATABASE_URL: postgres://postgres:password@purplix-postgres:5432/postgres
      MCAPTCHA_redis_URL: redis://purplix-mcaptcha-redis
      PORT: 7000
      MCAPTCHA_server_DOMAIN: mcaptcha.purplix.io
      MCAPTCHA_commercial: false
      MCAPTCHA_allow_registration: false
      MCAPTCHA_allow_demo: false
    depends_on:
      - purplix-postgres
      - purplix-mcaptcha-redis
    networks:
      - purplix-network

  purplix-postgres:
    image: postgres:latest
    restart: unless-stopped
    volumes:
      - purplix-mcaptcha-data:/var/lib/postgresql/
    environment:
      POSTGRES_PASSWORD: "!!changeme!!" 
      PGDATA: /var/lib/postgresql/data/mcaptcha/
    networks:
      - purplix-network

  ntfy:
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
        test: ["CMD-SHELL", "wget -q --tries=1 https://ntfy.example.com/v1/health -O - | grep -Eo '\"healthy\"\\s*:\\s*true' || exit 1"]
        interval: 60s
        timeout: 10s
        retries: 3
        start_period: 40s
    restart: unless-stopped

volumes:
    purplix-mongo-data:
    purplix-mcaptcha-data:


networks:
  purplix-network:
    driver: bridge
```
