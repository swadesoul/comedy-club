import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const p=new URL('../engine/comedy_studio.py',import.meta.url);
const b=readFileSync(p,'utf8');
const h=readFileSync(new URL('../studio/production.html',import.meta.url),'utf8');
test('60-second demo is a real private owner-scoped signed B2 route',()=>{
 assert.match(b,/def sample_sixty_review/);
 assert.match(b,/owner_id':'eq\.'\+actor\['id'\]/);
 assert.match(b,/smart-house-60sec-intro-first-unreviewed\.mp3/);
 assert.match(b,/path\.startswith\('\/comedy\/sample-sixty\/'\)/);
});
test('studio offers an honest 60-second preview instead of billing or public posting',()=>{
 assert.match(h,/Play 60-second Smart House sample/);
 assert.match(h,/not GPT Live One/);
 assert.match(h,/published\)/);
});
