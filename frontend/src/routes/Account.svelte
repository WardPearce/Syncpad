<script lang="ts">
  import sodium from "libsodium-wrappers-sumo";
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import UAParser from "ua-parser-js";

  import OtpInput from "../components/OtpInput.svelte";
  import PageLoading from "../components/PageLoading.svelte";
  import account, { logout } from "../lib/account";
  import apiClient from "../lib/apiClient";
  import {
    WebhookModel,
    type SessionModel,
    type UserModel,
  } from "../lib/client";
  import { base64Decode } from "../lib/crypto/codecUtils";
  import { relativeDate } from "../lib/date";
  import { localSecrets, type LocalSecretsModel } from "../stores";

  interface SessionDeviceModel extends SessionModel {
    uaparser: UAParser;
  }

  let activeSessions: SessionDeviceModel[] = [];
  let loggedInSecrets = get(localSecrets) as LocalSecretsModel;
  let user: UserModel;

  let webhookUrl = "";
  let currentNotifyTab: WebhookModel.type = WebhookModel.type.CANARY_RENEWALS;

  let privateKey: Uint8Array;
  let publicKey: Uint8Array;

  let otpError = "";

  async function toggleIpLookupConsent() {
    if (user.ip_lookup_consent) {
      await apiClient.privacy.controllersAccountPrivacyIpProgressingDisallowIpProgressing();
    } else {
      await apiClient.privacy.controllersAccountPrivacyIpProgressingConsentIpProgressingConsent();
    }

    user.ip_lookup_consent = !user.ip_lookup_consent;
  }

  // Replace when crypto publicKey.ts is implemented
  function decryptSessionInfo(base64CipherText: string): string {
    try {
      return new TextDecoder().decode(
        sodium.crypto_box_seal_open(
          base64Decode(base64CipherText),
          publicKey,
          privateKey
        )
      );
    } catch (error) {
      return "Failed to decrypted";
    }
  }

  async function logoutSession(sessionId: string) {
    if (sessionId === loggedInSecrets.jti) {
      await account.logout();
    } else {
      await apiClient.session.controllersSessionSessionIdInvalidateSession(
        sessionId
      );
      activeSessions = activeSessions.filter((v) => v._id !== sessionId);
    }
  }

  async function logoutAllOther() {
    activeSessions.forEach(async (session) => {
      if (session._id !== loggedInSecrets.jti) {
        await logoutSession(session._id);
      }
    });
  }

  async function resetOtp(otpCode: string) {
    try {
      await apiClient.account.controllersAccountOtpResetResetOtp(otpCode);
      await account.logout();
    } catch (error) {
      otpError = error.body.detail;
    }
  }

  async function toggleEmail() {
    if (user.notifications.email.includes(currentNotifyTab)) {
      user.notifications.email = user.notifications.email.filter(
        (email) => email !== currentNotifyTab
      );

      await apiClient.notifications.controllersAccountNotificationsEmailRemoveRemoveEmail(
        currentNotifyTab
      );
    } else {
      user.notifications.email = [
        ...user.notifications.email,
        currentNotifyTab,
      ];

      await apiClient.notifications.controllersAccountNotificationsEmailAddAddEmail(
        currentNotifyTab
      );
    }
  }

  async function removeWebhook(url: string) {
    user.notifications.webhooks[currentNotifyTab] = user.notifications.webhooks[
      currentNotifyTab
    ].filter((webhook) => webhook !== url);

    await apiClient.webhook.controllersAccountNotificationsWebhookRemoveRemoveWebhook(
      {
        url: url,
        type: currentNotifyTab,
      }
    );
  }

  async function addWebhook() {
    if (!webhookUrl) return;

    if (!(currentNotifyTab in user.notifications.webhooks)) {
      user.notifications.webhooks[currentNotifyTab] = [];
    }

    user.notifications.webhooks[currentNotifyTab] = [
      ...user.notifications.webhooks[currentNotifyTab],
      webhookUrl,
    ];

    await apiClient.webhook.controllersAccountNotificationsWebhookAddAddWebhook(
      {
        url: webhookUrl,
        type: currentNotifyTab,
      }
    );

    webhookUrl = "";
  }

  onMount(async () => {
    user = await apiClient.account.controllersAccountMeGetMe();

    privateKey = base64Decode(loggedInSecrets.rawKeypair.privateKey);
    publicKey = base64Decode(loggedInSecrets.rawKeypair.publicKey);

    (await apiClient.session.controllersSessionGetSessions()).forEach(
      (session) =>
        activeSessions.push({
          uaparser: new UAParser(decryptSessionInfo(session.device as string)),
          ...session,
        })
    );

    activeSessions = activeSessions;
  });
</script>

{#if !user}
  <PageLoading />
{:else}
  <h3>Account</h3>
  <article>
    <details>
      <summary class="none">
        <div class="row">
          <div class="max">
            <h4>Security</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <h5>Password reset</h5>
      {#if user.otp.completed}
        <h5>OTP reset</h5>
        <p>Enter your current OTP code to reset it.</p>
        <div style="display: flex;">
          {#if otpError}
            <p>{otpError}</p>
          {/if}

          <OtpInput onOtpEnter={resetOtp} />
        </div>
      {:else}
        <h5>Setup OTP</h5>
        <nav class="wrap"><button on:click={logout}>Enable OTP</button></nav>
      {/if}
    </details>
  </article>

  <article>
    <details>
      <summary class="none">
        <div class="row">
          <div class="max">
            <h4>Privacy</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <h5>Login IP processing</h5>
      <p>
        Upon logging in, we utilize your IP address to provide you with details
        about the active session and their location. It is important to
        acknowledge that all device and location information is securely
        encrypted using your public key. This information can only be accessed
        by you once you have successfully logged in.
      </p>
      <p>
        We employ <a
          href="https://proxycheck.io/"
          target="_blank"
          class="link"
          rel="noopener noreferrer">proxycheck.io</a
        > to process your IP address; however, it's important to note that they cannot
        establish a direct correlation between IPs and user accounts.
      </p>
      <label class="switch">
        <input
          type="checkbox"
          checked={user.ip_lookup_consent}
          on:click={toggleIpLookupConsent}
        />
        <span />
      </label>
    </details>
  </article>

  <article>
    <details>
      <summary class="none">
        <div class="row">
          <div class="max">
            <h4>Notifications</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <div>
        <div class="tabs left-align scroll">
          {#each Object.values(WebhookModel.type) as webhookType}
            <a
              class:active={webhookType === currentNotifyTab}
              on:click={() => (currentNotifyTab = webhookType)}
              href={`#${webhookType}`}
              style="text-transform: capitalize;"
              >{webhookType.replaceAll("_", " ")}</a
            >
          {/each}
        </div>
        <div
          class="page padding active surface-variant"
          style="border-radius: 0 0 .75rem .75rem;"
        >
          <h6>Emails</h6>
          <label class="switch" style="margin: 1em 0;">
            <input
              type="checkbox"
              on:change={toggleEmail}
              checked={user.notifications.email.includes(currentNotifyTab)}
            />
            <span />
          </label>

          <h6>Browser</h6>
          <button style="margin: 1em 0;">Grant browser notifications</button>

          <h6>
            Webhooks ({currentNotifyTab in user.notifications.webhooks
              ? user.notifications.webhooks[currentNotifyTab].length
              : 0}/3)
          </h6>
          <ul class="webhooks">
            {#if currentNotifyTab in user.notifications.webhooks}
              {#each user.notifications.webhooks[currentNotifyTab] as webhook, iteration}
                <li>
                  <form
                    on:submit|preventDefault={async () =>
                      await removeWebhook(webhook)}
                  >
                    <nav class="wrap">
                      <div class="field label border">
                        <input type="text" value={webhook} readonly />
                        <label for="webhook">URL #{iteration + 1}</label>
                      </div>
                      <button class="square round secondary large">
                        <i>close</i>
                      </button>
                    </nav>
                  </form>
                </li>
              {/each}
            {/if}
            {#if !(currentNotifyTab in user.notifications.webhooks) || user.notifications.webhooks[currentNotifyTab].length < 3}
              <li>
                <form on:submit|preventDefault={addWebhook}>
                  <nav class="wrap">
                    <div class="field label border">
                      <input type="text" bind:value={webhookUrl} />
                      <label for="webhook">Add Webhook</label>
                    </div>
                    <button class="square round large">
                      <i>add</i>
                    </button>
                  </nav>
                </form>
              </li>
            {/if}
          </ul>
        </div>
      </div>
    </details>
  </article>

  <article>
    <details>
      <summary class="none">
        <div class="row">
          <div class="max">
            <h4>Sessions</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>

      {#if activeSessions.length === 0}
        <span class="loader medium" />
      {:else}
        {#if activeSessions.length > 1}
          <button on:click={logoutAllOther}>Logout all other sessions</button>
        {/if}

        {#each activeSessions as session}
          <article
            class:surface-variant={session._id !== loggedInSecrets.jti}
            class:primary-container={session._id === loggedInSecrets.jti}
          >
            <div class="grid">
              <div class="s12 m6 l3">
                <h6>Location</h6>
                <p>
                  <span style="font-weight: bold;">Country:</span>
                  {#if session.location.country}
                    {decryptSessionInfo(session.location.country)}
                  {:else}
                    Unknown
                  {/if}
                </p>
                <p>
                  <span style="font-weight: bold;">Region:</span>
                  {#if session.location.region}
                    {decryptSessionInfo(session.location.region)}
                  {:else}
                    Unknown
                  {/if}
                </p>
                <p>
                  <span style="font-weight: bold;">IP Address:</span>
                  {#if session.location.ip}
                    {decryptSessionInfo(session.location.ip)}
                  {:else}
                    Unknown
                  {/if}
                </p>
              </div>
              <div class="s12 m6 l3">
                <h6>Device</h6>
                <p>
                  <span style="font-weight: bold;">Browser:</span>
                  {session.uaparser.getBrowser().name}
                </p>
                <p>
                  <span style="font-weight: bold;">Engine:</span>
                  {session.uaparser.getEngine().name}
                </p>
                <p>
                  <span style="font-weight: bold;">OS:</span>
                  {session.uaparser.getOS().name}
                </p>
              </div>
              <div class="s12 m6 l3">
                <h6>Expires</h6>
                <p>
                  {relativeDate(session.expires)}
                </p>
              </div>
              <div class="s12 m6 l3">
                <button on:click={async () => await logoutSession(session._id)}
                  >Logout
                  {#if session._id === loggedInSecrets.jti}
                    current session
                  {/if}
                </button>
              </div>
            </div>
          </article>
        {/each}
      {/if}
    </details>
  </article>

  <article>
    <details>
      <summary class="none">
        <div class="row">
          <div class="max">
            <h4>Danger zone</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <nav class="wrap">
        <button class="secondary">Rotate keychain</button>
        <button class="tertiary">Delete account</button>
      </nav>
    </details>
  </article>
{/if}

<style>
  h6 {
    margin: 0;
    font-size: 1.6em;
  }

  .s12 p {
    margin: 0;
  }

  .s12 {
    display: flex;
    flex-direction: column;
  }

  .webhooks {
    list-style: none;
    margin: 0;
  }

  .webhooks li {
    margin: 1em 0;
  }
</style>
