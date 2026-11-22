import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const back=readFileSync(new URL('../engine/comedy_studio.py',import.meta.url),'utf8');
const page=readFileSync(new URL('../studio/production.html',import.meta.url),'utf8');
test('genuine one-off GPT Live One review takes require an authenticated owner',()=>{
 assert.match(back,/actor=auth\(f,handler\)/);
 assert.match(back,/path\.startswith\('\/comedy\/live-take\/'\)/);
 assert.match(back,/def live_take_review\(/);
 assert.match(back,/owner_id':'eq\.'\+actor\['id'\]/);
 assert.match(back,/smart-house-gpt-live-1\.1-first-take-unreviewed\.mp3/);
});
test('studio labels short GPT Live take honestly and leaves full master separate',()=>{
 assert.match(page,/Review GPT Live One take \(25s\)/);
 assert.match(page,/opening_only/);
 assert.match(page,/Not the full routine/);
});
