<script lang="ts">
  import dayjs from "dayjs";
  import prettyBytes from "pretty-bytes";
  import { onMount } from "svelte";
  import { navigate } from "svelte-navigator";

  import { get } from "svelte/store";
  import Image from "../components/Image.svelte";
  import PageLoading from "../components/PageLoading.svelte";
  import apiClient from "../lib/apiClient";
  import { getTrustedCanary, saveCanaryAsTrusted } from "../lib/canary";
  import type {
    ApiError,
    DocumentCanaryWarrantModel,
    PublicCanaryModel,
    PublishedCanaryWarrantModel,
  } from "../lib/client";
  import { base64Decode } from "../lib/crypto/codecUtils";
  import { hashBase64Encode } from "../lib/crypto/hash";
  import signatures from "../lib/crypto/signatures";
  import { relativeDate, utcDate } from "../lib/date";
  import { advanceModeStore, localSecrets } from "../stores";

  export let domainName: string;
  export let signPublicKeyHash: string;

  let advanceMode: boolean;
  advanceModeStore.subscribe((value) => (advanceMode = value));

  let isLoading = true;

  enum SubscribeStatus {
    Unsubscribed,
    Subscribed,
    LoadingStatus,
  }

  let subscribeStatus: SubscribeStatus = SubscribeStatus.LoadingStatus;

  let canaryBioMatches = false;
  let serverKeyHashMatches = false;
  let canaryWarrantMatches = false;

  let firstCanaryVisit = true;

  const currentTime = dayjs();

  let currentPage = 0;
  let statementApiError = "";
  let canaryApiError = "";
  let serverPublicKeyHash: string;
  let canaryBio: PublicCanaryModel;
  let publicServerKey: Uint8Array;
  let currentPublishedWarrant: PublishedCanaryWarrantModel | undefined;
  let currentPublishedWarrantBlockTime: number;
  let documentHashes: Record<string, string> = {};
  let documentDownloading: string[] = [];
  onMount(async () => {
    try {
      canaryBio =
        await apiClient.canary.controllersCanaryDomainPublicPublicCanary(
          domainName
        );

      publicServerKey = base64Decode(canaryBio.keypair.public_key);

      serverPublicKeyHash = hashBase64Encode(publicServerKey, true);

      serverKeyHashMatches = serverPublicKeyHash === signPublicKeyHash;

      const trustedStoredPublicKeyHash = await getTrustedCanary(domainName);
      if (trustedStoredPublicKeyHash) {
        firstCanaryVisit = false;
      }

      if (serverKeyHashMatches) {
        // Validate stored canary.
        if (trustedStoredPublicKeyHash) {
          serverKeyHashMatches =
            signPublicKeyHash === trustedStoredPublicKeyHash;
        } else {
          // Store canary
          await saveCanaryAsTrusted(domainName, signPublicKeyHash);
        }
      } else if (trustedStoredPublicKeyHash === serverPublicKeyHash) {
        // If stored publicKey hash matches serverPublicKeyHash, then incorrect link was given.
        serverKeyHashMatches = true;
        signPublicKeyHash = trustedStoredPublicKeyHash;

        navigate(`/c/${domainName}/${trustedStoredPublicKeyHash}`, {
          replace: true,
        });
      } else {
        canaryBioMatches = false;
      }

      // This may change from the above logic.
      if (serverKeyHashMatches) {
        try {
          signatures.validateHash(
            publicServerKey,
            canaryBio.signature,
            JSON.stringify({
              domain: domainName,
              about: canaryBio.about,
              signature: "",
            })
          );
          canaryBioMatches = true;
        } catch (error) {
          canaryBioMatches = false;
        }
      }

      if (canaryBio.hex_color) await ui("theme", `#${canaryBio.hex_color}`);

      await getPublishedCanary();

      if (get(localSecrets) !== null) {
        // Load subscription status in the background
        loadSubscribeStatus();
      }
    } catch (error) {
      canaryApiError = (error as ApiError).body.detail;
    }

    isLoading = false;
  });

  async function toggleSubscribe() {
    if (subscribeStatus === SubscribeStatus.Subscribed) {
      subscribeStatus = SubscribeStatus.Unsubscribed;
      await apiClient.subscription.controllersCanarySubscriptionCanaryIdUnsubscribeUnsubscribe(
        canaryBio.id
      );
    } else {
      subscribeStatus = SubscribeStatus.Subscribed;
      await apiClient.subscription.controllersCanarySubscriptionCanaryIdSubscribeSubscribe(
        canaryBio.id
      );
    }
  }

  async function loadSubscribeStatus() {
    try {
      let status =
        await apiClient.subscription.controllersCanarySubscriptionCanaryIdAmSubscribed(
          canaryBio.id
        );

      subscribeStatus = status
        ? SubscribeStatus.Subscribed
        : SubscribeStatus.Unsubscribed;
    } catch {}
  }

  async function downloadDocument(toDownload: DocumentCanaryWarrantModel) {
    if (!toDownload.download_url) {
      return;
    }

    documentDownloading = [...documentDownloading, toDownload.file_id];

    let documentData: Uint8Array;
    try {
      documentData = new Uint8Array(
        await (await fetch(toDownload.download_url)).arrayBuffer()
      );
    } catch {
      return;
    }

    const documentHash = hashBase64Encode(documentData, true);
    if (documentHash !== toDownload.hash_) {
      return;
    }

    const anchor = document.createElement("a");
    const url = window.URL.createObjectURL(new Blob([documentData]));
    anchor.href = url;
    anchor.download = toDownload.filename;
    anchor.click();
    window.URL.revokeObjectURL(url);

    documentDownloading = documentDownloading.filter(
      (id) => id !== toDownload.file_id
    );
  }

  async function getPublishedCanary(page: number = 0) {
    isLoading = true;
    currentPage = page;
    documentHashes = {};

    try {
      const untrustedWarrant =
        await apiClient.warrant.controllersCanaryPublishedCanaryIdPagePublishedWarrant(
          canaryBio.id,
          page
        );

      untrustedWarrant.documents?.forEach((document) => {
        documentHashes[document.filename] = document.hash_;
      });

      try {
        signatures.validateHash(
          publicServerKey,
          untrustedWarrant.signature,
          JSON.stringify({
            btc_latest_block: untrustedWarrant.btc_latest_block,
            statement: untrustedWarrant.statement,
            concern: untrustedWarrant.concern,
            next_canary: untrustedWarrant.next_canary,
            issued: untrustedWarrant.issued,
            domain: domainName,
            id: untrustedWarrant.id,
            document_hashes: documentHashes,
          })
        );
        canaryWarrantMatches = true;
      } catch {
        canaryWarrantMatches = false;
      }

      // Used to validate block hash timestamp.
      try {
        const btcBlockTimestamp = (
          await (
            await fetch(
              `${import.meta.env.VITE_BLOCKSTREAM_API}/block/${
                untrustedWarrant.btc_latest_block
              }`
            )
          ).json()
        ).timestamp;

        currentPublishedWarrantBlockTime = btcBlockTimestamp * 1000;

        if (canaryWarrantMatches) {
          // Check if issued date is within 24 hours of block timestamp.
          canaryWarrantMatches =
            Math.abs(
              dayjs(currentPublishedWarrantBlockTime).valueOf() -
                utcDate(untrustedWarrant.issued).valueOf()
            ) <= 86400000;
        }

        currentPublishedWarrant = untrustedWarrant;
      } catch {
        statementApiError = `Failed to fetch from ${
          import.meta.env.VITE_BLOCKSTREAM_API
        }`;
        currentPublishedWarrant = undefined;
      }
    } catch (error) {
      statementApiError = (error as ApiError).body.detail;
      currentPublishedWarrant = undefined;
    }

    isLoading = false;
  }
</script>

{#if isLoading}
  <PageLoading />
{:else if canaryApiError}
  <h3>{canaryApiError}</h3>
{:else}
  {#if !serverKeyHashMatches}
    <article class="error">
      <h5>Public key has been tampered with!</h5>
      <p>
        Provided public key from the server, does not match the Public key hash
        in the URL.
      </p>
      <p>
        This is a <span style="font-weight: bold;">significant concern</span>,
        the host may be trying to issue fake canaries.
      </p>
    </article>
    {#if firstCanaryVisit}
      <article class="error">
        <h6>Please note</h6>
        <p>
          If you were given an invalid link, this alert would be triggered
          during your first visit to this canary. Please ensure you got this
          link off a trustworthy source.
        </p>
      </article>
    {/if}
  {:else if firstCanaryVisit}
    <article class="primary">
      Welcome to {canaryBio.domain}'s canary! This is your first visit on this
      browser/account, and we've saved it as a trusted canary.
    </article>
  {/if}
  {#if !canaryBioMatches}
    <article class="error">
      <h6>Canary information failed validation!</h6>
      <p>
        This is <span style="font-weight: bold;">concerning</span> & may mean the
        host is trying to trick you.
      </p>
    </article>
  {/if}

  {#if subscribeStatus !== SubscribeStatus.LoadingStatus}
    <nav class="right-align">
      <button on:click={toggleSubscribe}>
        {#if subscribeStatus === SubscribeStatus.Unsubscribed}
          <i>notifications</i>
          <span>Subscribe</span>
        {:else}
          <i>notifications_active</i>
          <span>Unsubscribe</span>
        {/if}
      </button>
    </nav>
  {/if}

  <article>
    <details>
      <summary class="none">
        <div class="row canary-name scroll">
          <Image
            size="medium"
            src={`${canaryBio.logo}`}
            alt={`Logo for ${canaryBio.domain}`}
          />
          <div class="max">
            <h4 class:strikeout={!canaryBioMatches}>{canaryBio.domain}</h4>
          </div>
          <i>arrow_drop_down</i>
        </div>
      </summary>
      <p class:strikeout={!canaryBioMatches}>
        {canaryBio.about}
      </p>

      <h6>Domain ownership</h6>
      <p class:strikeout={!canaryBioMatches}>
        Verified owner of <a
          href={`https://${canaryBio.domain}`}
          target="_blank"
          class="link"
          rel="noopener noreferrer">{canaryBio.domain}</a
        >.
      </p>

      {#if advanceMode}
        <h6>Canary ID</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={canaryBio.id} />
        </div>

        <h6>Public key</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={canaryBio.keypair.public_key} />
        </div>

        <h6>Public key hash</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={serverPublicKeyHash} />
        </div>

        <h6>Algorithms</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={canaryBio.algorithms} />
        </div>

        <h6>Signature</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={canaryBio.signature} />
        </div>

        <h6>Created</h6>
        <div class="field border" style="margin-top: 0;">
          <input readonly value={relativeDate(canaryBio.created)} />
        </div>

        <h5>Raw message</h5>
        <div class="field textarea extra border" style="margin-top: 0;">
          <textarea readonly value={JSON.stringify(canaryBio, null, 2)} />
        </div>
      {/if}
    </details>
  </article>

  {#if currentPublishedWarrant}
    <article>
      <nav class="scroll">
        {#if currentPage === 0}
          <h3>Latest Canary</h3>
        {:else}
          <h3>From {relativeDate(currentPublishedWarrant.issued)}</h3>
        {/if}
        {#if serverKeyHashMatches && canaryBioMatches && canaryWarrantMatches}
          <div class="small chip circle">
            <i>done_all</i>
            <div class="tooltip right">
              Cryptographically signed by {canaryBio.domain}
            </div>
          </div>
        {:else}
          <div class="small chip circle error">
            <i>error_outline</i>
            <div class="tooltip right">This canary failed validation.</div>
          </div>
        {/if}
      </nav>
      {#if !currentPublishedWarrant.active}
        <nav class="wrap">
          <h6>This canary is no longer active.</h6>
          <button
            on:click={async () => {
              (currentPage = 0), await getPublishedCanary(0);
            }}>Go to latest</button
          >
        </nav>
      {/if}
      {#if !serverKeyHashMatches || !canaryBioMatches || !canaryWarrantMatches}
        <article class="error">
          <p>This canary failed validation, do NOT trust it.</p>
        </article>
      {/if}
      {#if utcDate(currentPublishedWarrant.issued) > currentTime}
        <article class="error">
          <p>
            This canary is from the future, do NOT trust it. Please check your
            system clock.
          </p>
        </article>
      {/if}
      {#if currentPublishedWarrant.active && currentTime > utcDate(currentPublishedWarrant.next_canary)}
        <article class="error">
          <p>
            This canary is out of date, please consider the site compromised
            until a new canary is published saying otherwise.
          </p>
        </article>
      {/if}
      <div class="grid">
        <div class="s12 m6 l4">
          <article class="border surface-variant">
            <div class="row">
              <div class="max">
                <h5>Concern</h5>
                <h6
                  style="text-transform: capitalize;"
                  class:strikeout={!serverKeyHashMatches ||
                    !canaryBioMatches ||
                    !canaryWarrantMatches}
                >
                  {currentPublishedWarrant.concern}
                </h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l4">
          <article class="border surface-variant">
            <div class="row">
              <div class="max">
                <h5>Issued</h5>
                <h6
                  class:strikeout={!serverKeyHashMatches ||
                    !canaryBioMatches ||
                    !canaryWarrantMatches}
                >
                  {relativeDate(currentPublishedWarrant.issued)}
                </h6>
              </div>
            </div>
          </article>
        </div>
        <div class="s12 m6 l4">
          <article class="border surface-variant">
            <div class="row">
              <div class="max">
                <h5>Next Canary</h5>
                <h6
                  class:strikeout={!serverKeyHashMatches ||
                    !canaryBioMatches ||
                    !canaryWarrantMatches ||
                    !currentPublishedWarrant.active}
                >
                  {relativeDate(currentPublishedWarrant.next_canary)}
                </h6>
              </div>
            </div>
          </article>
        </div>
      </div>

      <h5>Statement</h5>
      <p
        class:strikeout={!serverKeyHashMatches ||
          !canaryBioMatches ||
          !canaryWarrantMatches}
      >
        {currentPublishedWarrant.statement}
      </p>

      {#if (serverKeyHashMatches && canaryBioMatches && canaryWarrantMatches) || advanceMode}
        <h5>Documents</h5>
        {#if Object.keys(currentPublishedWarrant.documents).length > 0}
          <div class="grid">
            {#each currentPublishedWarrant.documents as document}
              <div class="s12 m6 l4">
                <article class="surface-variant">
                  <div class="row">
                    <div class="max">
                      <h6>{document.filename}</h6>

                      <p>{prettyBytes(document.size)}</p>

                      {#if advanceMode}
                        <div
                          class="field border label"
                          style="margin-top: 1em;"
                        >
                          <label for="file-hash">BLAKE2b hash</label>
                          <input readonly value={document.hash_} />
                        </div>
                      {/if}

                      {#if documentDownloading.includes(document.file_id)}
                        <span class="loader small" />
                      {:else}
                        <nav class="wrap">
                          <button
                            on:click={async () => {
                              await downloadDocument(document);
                            }}
                            class="small secondary"
                          >
                            <i>download</i>
                          </button>
                        </nav>
                      {/if}
                    </div>
                  </div>
                </article>
              </div>
            {/each}
          </div>
        {:else}
          <p>No documents</p>
        {/if}
      {/if}

      {#if advanceMode}
        <h5>Canary warrant ID</h5>
        <div class="field border" style="margin-top: 0;">
          <input type="text" readonly value={currentPublishedWarrant.id} />
        </div>

        <h5>BTC Block</h5>
        <div class="field border" style="margin: 0;">
          <input
            type="text"
            readonly
            value={currentPublishedWarrant.btc_latest_block}
          />
        </div>
        <p style="margin-bottom: 2rem;">
          Created: {relativeDate(currentPublishedWarrantBlockTime)}
        </p>

        <h5>Signature</h5>
        <div class="field border" style="margin-top: 0;">
          <input
            type="text"
            readonly
            value={currentPublishedWarrant.signature}
          />
        </div>

        <h5>Raw message</h5>
        <div class="field textarea extra border" style="margin-top: 0;">
          <textarea
            readonly
            value={JSON.stringify(currentPublishedWarrant, null, 2)}
          />
        </div>
      {/if}
    </article>
  {:else}
    <article
      style="display: flex;justify-content: center; align-items: center;height: 35vh;"
    >
      <h5>{statementApiError}</h5>
    </article>
  {/if}

  <div class="pagination">
    {#if currentPublishedWarrant}
      <button
        on:click={async () => (
          currentPage++, await getPublishedCanary(currentPage)
        )}
      >
        <i>arrow_back</i>
        <span>Past statement</span>
      </button>
    {:else}
      <div />
    {/if}
    {#if currentPage !== 0}
      <button
        on:click={async () => (
          currentPage--, await getPublishedCanary(currentPage)
        )}
      >
        <span>Next statement</span>
        <i>arrow_forward</i>
      </button>
    {/if}
  </div>
{/if}

<style>
  .strikeout {
    text-decoration: line-through;
  }

  @media only screen and (max-width: 600px) {
    .canary-name {
      flex-direction: column;
    }
  }
  @media only screen and (max-width: 600px) {
    .canary-name i {
      display: none;
    }
  }
</style>
