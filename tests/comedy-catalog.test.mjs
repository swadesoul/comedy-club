import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const page=readFileSync(new URL('../public/index.html',import.meta.url),'utf8');
const api=readFileSync(new URL('../engine/comedy_studio.py',import.meta.url),'utf8');
test('front end loads actual server records and has no seeded routine catalog',()=>{
 assert.match(page,/fetch\('\/comedy-api\/public'/);
 assert.doesNotMatch(page,/const\s+cast\s*=\s*\[\s*\{/);
 assert.doesNotMatch(page,/const\s+routines\s*=\s*\[\s*\{/);
});
test('audio URLs are only server-granted on published catalog items',()=>{
 assert.match(api,/"state":"eq.published"|'state':'eq.published'/);
 assert.match(api,/audio_b2_key/);
 assert.match(api,/comedy\/approved\//);
 assert.match(api,/adult_inventory_hidden/);
});
test('no active billing or synthetic playback in public catalog',()=>{
 assert.doesNotMatch(page,/sample-audio.mp3|lorem ipsum|Math\.random\(/i);
 assert.match(page,/No verified audio recordings have been published/);
});
