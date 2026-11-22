import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const html=readFileSync(new URL('../studio/production.html',import.meta.url),'utf8');
const backend=readFileSync(new URL('../engine/comedy_studio.py',import.meta.url),'utf8');
test('studio saves only real authenticated data and does not produce dummy rows',()=>{
 assert.match(html,/api\('\/private'\)/);
 assert.match(html,/api\('\/drafts'/);
 assert.match(html,/api\('\/batches\/plan'/);
 assert.match(html,/api\('\/assets'/);
 assert.match(html,/api\('\/stations'\)/);
 assert.doesNotMatch(html,/Math\.random\(|sample routine|placeholder routine/i);
});
test('studio requires rights confirmation, real account and backend spending guards',()=>{
 assert.match(backend,/rights_confirmed/);
 assert.match(backend,/external_spend_authorized':False/);
 assert.match(backend,/provider_spend_cap_cents':0/);
 assert.match(backend,/owner_id/);
 assert.match(backend,/age_gate_verified|adult_stations_disabled/);
});
