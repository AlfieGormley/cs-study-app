import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../sw.js', import.meta.url), 'utf8');
const version = source.match(/const VERSION = '([a-f0-9]{12})';/)[1];
const origin = 'https://study.example';
const cacheName = `cs-study-${version}`;

function worker({ installFails = false } = {}) {
  const handlers = new Map();
  const buckets = new Map();
  const log = { requests: [], imported: [], deleted: [], skipped: false, claimed: false, network: [] };
  const bucket = (name) => {
    if (!buckets.has(name)) buckets.set(name, new Map());
    return {
      async addAll(requests) {
        log.requests.push(...requests);
        if (installFails) throw new Error('Download interrupted');
      },
      async match(request) {
        const url = new URL(typeof request === 'string' ? request : request.url, origin);
        return buckets.get(name).get(url.pathname);
      },
    };
  };
  const self = {
    APP_ASSETS: ['./', 'index.html', 'styles.css', 'data/index.json'],
    addEventListener: (name, fn) => handlers.set(name, fn),
    skipWaiting: async () => { log.skipped = true; },
    clients: { claim: async () => { log.claimed = true; } },
  };
  vm.runInNewContext(source, {
    self, URL, Response,
    Request: class extends Request {
      constructor(url, options) { super(new URL(url, origin), options); }
    },
    location: { origin },
    importScripts: (url) => log.imported.push(url),
    caches: {
      open: async (name) => bucket(name),
      keys: async () => [...buckets.keys()],
      delete: async (name) => { log.deleted.push(name); return buckets.delete(name); },
      match: () => { throw new Error('Must not search caches from older releases'); },
    },
    fetch: async (request) => {
      log.network.push(request.url);
      if (log.offline) throw new Error('Offline');
      return new Response('network');
    },
  });
  return {
    log, buckets,
    async lifecycle(name) {
      let promise;
      handlers.get(name)({ waitUntil: (p) => { promise = p; } });
      await promise;
    },
    async fetch(url, mode = 'cors', method = 'GET') {
      let response;
      handlers.get('fetch')({
        request: { url, mode, method },
        respondWith: (p) => { response = p; },
      });
      return response;
    },
    message: (data, port) => handlers.get('message')({ data, ports: [port] }),
  };
}

test('a new release downloads fresh files and uses its matching manifest', async () => {
  const w = worker();
  await w.lifecycle('install');
  assert.deepEqual(w.log.imported, [`assets.js?v=${version}`]);
  assert.equal(w.log.requests.length, 4);
  assert.ok(w.log.requests.every((request) => request.cache === 'reload'));
  assert.equal(w.log.skipped, true);
  const manifest = fs.readFileSync(new URL('../assets.js', import.meta.url), 'utf8');
  assert.ok(manifest.includes(`self.APP_VERSION = '${version}'`));
});

test('an interrupted download keeps the installed release active', async () => {
  const w = worker({ installFails: true });
  w.buckets.set('cs-study-old', new Map([['/styles.css', new Response('old CSS')]]));
  await assert.rejects(w.lifecycle('install'), /Download interrupted/);
  assert.equal(w.log.skipped, false);
  assert.equal(w.log.claimed, false);
  assert.equal(await w.buckets.get('cs-study-old').get('/styles.css').text(), 'old CSS');
});

test('requests use only the active release, even when an older cache exists', async () => {
  const w = worker();
  w.buckets.set('cs-study-old', new Map([['/styles.css', new Response('old CSS')]]));
  w.buckets.set(cacheName, new Map([['/styles.css', new Response('new CSS')]]));
  assert.equal(await (await w.fetch(`${origin}/styles.css?v=new`)).text(), 'new CSS');
  assert.equal(await (await w.fetch(`${origin}/not-cached.js`)).text(), 'network');
  assert.equal(w.log.network.length, 1);
  assert.equal(await w.fetch('https://other.example/styles.css'), undefined);
  assert.equal(await w.fetch(`${origin}/submit`, 'cors', 'POST'), undefined);
});

test('offline navigation falls back to the current app and cached lessons stay available', async () => {
  const w = worker();
  w.log.offline = true;
  w.buckets.set('cs-study-old', new Map([['/', new Response('old app')]]));
  w.buckets.set(cacheName, new Map([
    ['/', new Response('new app')],
    ['/data/index.json', new Response('cached lessons')],
  ]));
  assert.equal(await (await w.fetch(`${origin}/lesson`, 'navigate')).text(), 'new app');
  assert.equal(await (await w.fetch(`${origin}/data/index.json`)).text(), 'cached lessons');
  assert.equal((await w.fetch(`${origin}/missing.js`)).type, 'error');
});

test('activation removes old app caches, retains unrelated caches, and reports the release', async () => {
  const w = worker();
  w.buckets.set('cs-study-old', new Map());
  w.buckets.set(cacheName, new Map());
  w.buckets.set('another-app', new Map());
  await w.lifecycle('activate');
  assert.deepEqual(w.log.deleted, ['cs-study-old']);
  assert.ok(w.buckets.has('another-app'));
  assert.ok(w.buckets.has(cacheName));
  assert.equal(w.log.claimed, true);
  let reported;
  w.message('APP_VERSION', { postMessage: (v) => { reported = v; } });
  assert.equal(reported, version);
});
