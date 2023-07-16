<script lang="ts">
  import { onMount } from "svelte";
  import { get } from "svelte/store";
  import UAParser from "ua-parser-js";

  import OtpInput from "../components/OtpInput.svelte";
  import PageLoading from "../components/PageLoading.svelte";
  import account, { logout, resetPassword } from "../lib/account";
  import apiClient from "../lib/apiClient";
  import {
    WebhookModel,
    type SessionModel,
    type UserModel,
  } from "../lib/client";
  import publicKey, {
    PrivateKeyLocation,
    PublicKeyLocation,
  } from "../lib/crypto/publicKey";
  import { relativeDate } from "../lib/date";
  import { getCurrentThemePrimary } from "../lib/theme";
  import {
    advanceModeStore,
    localSecrets,
    type LocalSecretsModel,
  } from "../stores";

  interface SessionDeviceModel extends SessionModel {
    uaparser: UAParser;
  }

  let advanceMode: boolean;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  let activeSessions: SessionDeviceModel[] = [];
  let loggedInSecrets = get(localSecrets) as LocalSecretsModel;
  let user: UserModel;

  enum resetDialogStates {
    closed,
    password,
    otp,
  }
  let resetDialogError = "";
  let resetDialogState = resetDialogStates.closed;
  let newRawPassword = "";

  let webhookUrl = "";
  let currentNotifyTab: WebhookModel.type = WebhookModel.type.CANARY_RENEWALS;

  let themeColor = getCurrentThemePrimary();

  async function changeThemeColor() {
    await ui("theme", themeColor);

    try {
      localStorage.setItem("theme", themeColor);
    } catch {}
  }

  async function resetThemeToDefault() {
    await ui("theme", import.meta.env.VITE_THEME);
    themeColor = import.meta.env.VITE_THEME;

    try {
      localStorage.removeItem("theme");
    } catch {}
  }

  async function toggleIpLookupConsent() {
    if (user.ip_lookup_consent) {
      await apiClient.privacy.controllersAccountPrivacyIpProgressingDisallowIpProgressing();
    } else {
      await apiClient.privacy.controllersAccountPrivacyIpProgressingConsentIpProgressingConsent();
    }

    user.ip_lookup_consent = !user.ip_lookup_consent;
  }

  function boxSealOpen(toDecrypt: string): string {
    try {
      return publicKey.boxSealOpen(
        PublicKeyLocation.localKeypair,
        PrivateKeyLocation.localKeypair,
        toDecrypt,
        true
      ) as string;
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
      resetDialogError = error.body.detail;
    }
  }

  async function resetPass(otpCode: string) {
    try {
      for await (const _ of resetPassword(newRawPassword, otpCode)) {
        // Do nothing
      }
    } catch (error) {
      resetDialogError = error.body.detail;
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

    (await apiClient.session.controllersSessionGetSessions()).forEach(
      (session) =>
        activeSessions.push({
          uaparser: new UAParser(boxSealOpen(session.device as string)),
          ...session,
        })
    );

    activeSessions = activeSessions;
  });
</script>

{#if !user}
  <PageLoading />
{:else}
  <dialog
    class:active={resetDialogState !== resetDialogStates.closed}
    class="surface-variant"
  >
    {#if resetDialogError}
      <div class="error" style="padding: 0.3em 1em;">
        <p>{resetDialogError}</p>
      </div>
    {/if}

    {#if resetDialogState === resetDialogStates.otp}
      <p>Please enter your current OTP code to reset it.</p>
    {:else}
      <div class="field label border fill">
        <input type="password" bind:value={newRawPassword} required />
        <label for="password">New Password</label>
      </div>
    {/if}

    <div style="display: flex;">
      <OtpInput
        onOtpEnter={resetDialogState === resetDialogStates.otp
          ? resetOtp
          : resetPass}
      />
    </div>

    <nav class="wrap">
      <button
        class="tertiary"
        on:click={() => (resetDialogState = resetDialogStates.closed)}
      >
        <i>close</i>
        <span>Cancel reset</span>
      </button>
    </nav>
  </dialog>

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
      <nav class="wrap">
        {#if user.otp.completed}
          <button
            on:click={() => (resetDialogState = resetDialogStates.password)}
          >
            <i>password</i>
            <span>Password reset</span>
          </button>

          <button on:click={() => (resetDialogState = resetDialogStates.otp)}>
            <i>restart_alt</i>
            <span>OTP reset</span>
          </button>
        {:else}
          <button on:click={logout}>OTP enable</button>
        {/if}
      </nav>
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
          {#if currentNotifyTab === WebhookModel.type.CANARY_RENEWALS}
            <p>
              Whenever your canary is due for renewal, receive a alert via these
              channels.
            </p>
          {:else if currentNotifyTab === WebhookModel.type.CANARY_SUBSCRIPTIONS}
            <p>
              Receive a notification whenever a canary you are subscribed to
              publishes a new warrant via these channels.
            </p>
          {:else}
            <p>
              Whenever a user submits a survey you created, receive a
              notification via these channels.
            </p>
          {/if}
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
            <h4>Theming</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <label class="color">
        <input
          bind:value={themeColor}
          on:input={changeThemeColor}
          type="color"
        />
        <span>Custom color</span>
      </label>

      {#if themeColor !== import.meta.env.VITE_THEME}
        <button on:click={resetThemeToDefault} style="margin-top: 1em;"
          >Reset to default</button
        >
      {/if}
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
                    {boxSealOpen(session.location.country)}
                  {:else}
                    Unknown
                  {/if}
                </p>
                <p>
                  <span style="font-weight: bold;">Region:</span>
                  {#if session.location.region}
                    {boxSealOpen(session.location.region)}
                  {:else}
                    Unknown
                  {/if}
                </p>
                <p>
                  <span style="font-weight: bold;">IP Address:</span>
                  {#if session.location.ip}
                    {boxSealOpen(session.location.ip)}
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

  {#if advanceMode}
    <article>
      <details>
        <summary class="none">
          <div class="row">
            <div class="max">
              <h4>Advance mode</h4>
            </div>
            <i>arrow_drop_down</i>
          </div>
        </summary>
        <p>
          When advance mode is enabled, you'll be provided with extra
          information around how our systems work.
        </p>

        <h6>User ID</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={user._id} />
        </div>

        <h6>Algorithms</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={user.algorithms} />
        </div>

        <h6>Signature</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={user.signature} />
        </div>

        <h6>Raw account infomation</h6>
        <div class="field textarea extra border" style="margin-top: 0;">
          <textarea readonly value={JSON.stringify(user, null, 2)} />
        </div>
      </details>
    </article>
  {/if}

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
        <button class="secondary">
          <i>autorenew</i>
          <span>Rotate keychain</span>
        </button>
        <button class="tertiary">
          <i>delete_forever</i>
          <span>Delete account</span>
        </button>
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
