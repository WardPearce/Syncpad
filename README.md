# Not production ready...

&nbsp;

<div align="center">
  <img src="https://i.imgur.com/1pkrLq9.png" width="100px" />
  <h1>Purplix</h1>
  <quote>
    Purplix is a open source set of tools focused on privacy and building confidence with your users.
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

[More info]()

## What is Purplix Canary?
Purplix Canary is a free & open source warrant canary tool what helps you to build trust with your users.

It allows you to inform users cryptographically if your site has been compromised, seized or raided by anyone.

### Site verification
Purplix uses DNS records to verify the domain the canary is for, giving your users confidence they are trusting the right people.

### Canary signatures
Each domain is associated with a unique key pair. The private key is generated locally and securely stored within the owner's keychain. When a user visits a canary from a specific domain for the first time, their private key is used to sign the public key. This signed version of the public key is then automatically employed for subsequent visits, effectively mitigating man-in-the-middle attacks and ensuring the trustworthiness of canary statements from the respective domain.

### Files
Canaries can include signed documents to help users further understand a situation.

### Notifications
Users are automatically notified on the event of a new statement being published.

[More info]()

# Setup
## Production

## Development