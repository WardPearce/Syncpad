# Not production ready...

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
Purplix Survey is a free & open source survey tool what can't read your questions & answers.

With traditional surveys you are one data breach, one rouge employee or one government warrant away from all your user's data being exposed. Purplix uses modern encryption techniques to keep your user's data away from any actors.

### How does it work?
#### Questions, Descriptions & Title encryption

When you create a survey, we encrypt your title, descriptions & questions with a secret key. This key is then stored encrypted in your keychain. When you share your survey with others using a link, the key is stored in the link for your participants. This ensures that your survey questions can only be read by your participants.

#### Answers encryption
Every survey has its own unique key pair. The private key is securely stored in your keychain, while the public key is used by users to encrypt their answers. Only you have the means to decrypt the answers once they are submitted. When you share a survey, we include a hash of the public key in the URL to prevent main-in-the-middle attacks.

#### Preventing spam & multiple submissions
Survey creators can opt-in to use VPN blocking, requiring a Purplix account or IP blocking. IP blocking works by storing a hash of the IP salted with a key not stored by Purplix, minimizing the attack surface of tracking submission locations, these IP hashes are only stored for 7 days or until the survey closes. Users will always be informed when any of these features are enabled.

## What is Purplix Canary?
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
        VITE_API_SCHEMA_URL: true
    ports:
      - "8866:80"

    purplix-backend:
        container_name: purplix-backend
        image: wardpearce/purplix-backend:latest
        restart: unless-stopped
        ports:
            - "8865:80"
        environment:
            # ProxiedUrls Settings
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
                    "secret": "your_jwt_secret",
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

  purplix-socks5:
    restart: unless-stopped
    image: serjs/go-socks5-proxy:latest
    environment:
        PROXY_USER: someuser
        PROXY_PASSWORD: somepass
        PROXY_PORT: 1080
    ports:
      - "1080:1080"

volumes:
    purplix-mongo-data:
```