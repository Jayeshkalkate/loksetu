// Dependency-free smoke tests for the loading page. Run: node test_loader.mjs
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const source = fs.readFileSync(path.join(here, 'loader.js'), 'utf8');

function makeHarness({ backendUrl = 'https://loksetu-api.onrender.com', fetchImpl = async () => ({ ok: true, status: 200, text: async () => 'ok' }) } = {}) {
  const elements = new Map();
  const timers = [];
  let redirect = null;
  let fetchCalls = 0;
  const getElement = (id) => {
    if (!elements.has(id)) elements.set(id, {
      id, hidden: false, disabled: false, textContent: '', dataset: {}, listeners: {},
      addEventListener(event, cb) { this.listeners[event] = cb; }
    });
    return elements.get(id);
  };
  const windowObj = {
    LOKSETU_CONFIG: { backendUrl },
    location: { replace(url) { redirect = url; } },
    setTimeout(fn, delay) { timers.push({ fn, delay }); return timers.length; },
    clearTimeout() {}
  };
  const context = {
    window: windowObj,
    document: { getElementById: getElement },
    URL,
    AbortController,
    Date,
    fetch: async (...args) => { fetchCalls += 1; return fetchImpl(...args); },
    console
  };
  vm.runInNewContext(source, context, { filename: 'loader.js' });
  return { elements, timers, get redirect() { return redirect; }, get fetchCalls() { return fetchCalls; } };
}

// Healthy backend: only the exact successful health response redirects.
{
  let requested;
  const h = makeHarness({ fetchImpl: async (url, options) => {
    requested = { url, options };
    return { ok: true, status: 200, text: async () => 'ok' };
  }});
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(requested.url.startsWith('https://loksetu-api.onrender.com/healthz/?loader_check='), true);
  assert.equal(requested.options.mode, 'cors');
  assert.equal(requested.options.credentials, 'omit');
  assert.equal(h.redirect, 'https://loksetu-api.onrender.com/');
}

// Database not ready: it retries instead of redirecting to an unavailable app.
{
  const h = makeHarness({ fetchImpl: async () => ({ ok: false, status: 503, text: async () => 'db error' }) });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.redirect, null);
  assert.equal(h.timers.some(t => t.delay > 0), true);
}

// Empty config: visible actionable configuration error and no network call.
{
  const h = makeHarness({ backendUrl: '' });
  assert.equal(h.fetchCalls, 0);
  assert.equal(h.elements.get('error-panel').hidden, false);
  assert.equal(h.elements.get('retry-button').hidden, true);
}

// A bad health route gives a visible actionable error without redirecting.
{
  const h = makeHarness({ fetchImpl: async () => ({ ok: false, status: 404, text: async () => 'not found' }) });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(h.redirect, null);
  assert.equal(h.elements.get('error-panel').hidden, false);
  assert.equal(h.elements.get('retry-button').hidden, false);
}

console.log('Loader smoke tests passed (healthy, sleeping/unready, missing config, wrong route).');
