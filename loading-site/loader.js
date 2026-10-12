(() => {
  'use strict';

  const config = window.LOKSETU_CONFIG || {};
  const backendUrl = (config.backendUrl || '').trim().replace(/\/+$/, '');
  const statusMessage = document.getElementById('status-message');
  const statusLabel = document.getElementById('status-label');
  const statusSpinner = document.getElementById('status-spinner');
  const statusPulse = document.getElementById('status-pulse');
  const errorPanel = document.getElementById('error-panel');
  const errorTitle = document.getElementById('error-title');
  const errorMessage = document.getElementById('error-message');
  const retryButton = document.getElementById('retry-button');

  const MAX_AUTO_WAIT_MS = 5 * 60 * 1000;
  const REQUEST_TIMEOUT_MS = 12000;
  let startedAt = Date.now();
  let attempt = 0;
  let busy = false;
  let timerId = null;

  function setStatus(message, label) {
    statusMessage.textContent = message;
    statusLabel.textContent = label;
  }

  function showError(title, message, isConfigError = false) {
    errorTitle.textContent = title;
    errorMessage.textContent = message;
    errorPanel.hidden = false;
    statusSpinner.hidden = true;
    statusPulse.hidden = true;
    retryButton.textContent = 'Check again';
    retryButton.hidden = isConfigError;
  }

  function validateBackendUrl(value) {
    if (!value) return 'The backend URL is not configured yet. Set BACKEND_URL in the Render Static Site environment and redeploy.';
    let parsed;
    try { parsed = new URL(value); } catch (_) { return 'The backend URL is not a valid URL. Check the BACKEND_URL setting and redeploy.'; }
    if (parsed.protocol !== 'https:' && parsed.hostname !== 'localhost' && parsed.hostname !== '127.0.0.1') {
      return 'The backend URL must use HTTPS on a public deployment. Check BACKEND_URL and redeploy.';
    }
    if (parsed.username || parsed.password || parsed.search || parsed.hash || (parsed.pathname !== '/' && parsed.pathname !== '')) {
      return 'Set BACKEND_URL to the backend origin only, for example https://loksetu-api.onrender.com, without a path or credentials.';
    }
    return null;
  }

  async function checkReady() {
    if (busy) return;
    busy = true;
    retryButton.disabled = true;
    errorPanel.hidden = true;
    statusSpinner.hidden = false;
    statusPulse.hidden = false;
    setStatus('Checking whether the application and database are ready.', 'Checking application status');

    const controller = new AbortController();
    const requestTimer = window.setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
    try {
      const url = `${backendUrl}/healthz/?loader_check=${Date.now()}`;
      const response = await fetch(url, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-store',
        redirect: 'follow',
        credentials: 'omit',
        headers: { 'Accept': 'text/plain' },
        signal: controller.signal
      });
      const body = (await response.text()).trim();
      if (response.ok && body === 'ok') {
        setStatus('LOKSETU is ready. Opening your application now.', 'Connection ready');
        statusLabel.textContent = 'Connection ready';
        window.clearTimeout(requestTimer);
        window.location.replace(`${backendUrl}/`);
        return;
      }
      if (response.status === 404) {
        showError('The health-check route was not found.', 'Confirm that BACKEND_URL points to your Django web service, not the Static Site, and that /healthz/ is available.');
      } else {
        scheduleRetry(`The server responded with status ${response.status || 'unknown'} and is not ready yet.`);
      }
    } catch (error) {
      const elapsed = Date.now() - startedAt;
      if (elapsed >= MAX_AUTO_WAIT_MS) {
        showError('LOKSETU is taking longer than usual to start.', 'The free web service may still be waking up, or the network may be blocking the health check. You can retry, or confirm BACKEND_URL and the service logs in Render.');
      } else {
        setStatus('The service may be waking from an idle state. We’ll check again automatically.', 'Waiting for the application');
        scheduleRetry(error && error.name === 'AbortError' ? 'The health check timed out; retrying.' : 'The application is not reachable yet; retrying.');
      }
    } finally {
      window.clearTimeout(requestTimer);
      busy = false;
      retryButton.disabled = false;
    }
  }

  function scheduleRetry(detail) {
    const elapsed = Date.now() - startedAt;
    if (elapsed >= MAX_AUTO_WAIT_MS) {
      showError('LOKSETU is taking longer than usual to start.', detail || 'Please check the backend service and try again.');
      return;
    }
    attempt += 1;
    const delay = Math.min(5000, 1300 + attempt * 350);
    if (detail) statusMessage.textContent = detail;
    statusLabel.textContent = `Next check in about ${Math.ceil(delay / 1000)} seconds`;
    if (timerId) window.clearTimeout(timerId);
    timerId = window.setTimeout(() => {
      timerId = null;
      checkReady();
    }, delay);
  }

  retryButton.addEventListener('click', () => {
    if (timerId) window.clearTimeout(timerId);
    timerId = null;
    startedAt = Date.now();
    attempt = 0;
    errorPanel.hidden = true;
    checkReady();
  });

  const configError = validateBackendUrl(backendUrl);
  if (configError) {
    setStatus('One setup step is still needed before this loader can connect.', 'Configuration required');
    showError('The loader needs a backend URL.', configError, true);
    statusSpinner.hidden = true;
    statusPulse.hidden = true;
  } else {
    checkReady();
  }
})();
