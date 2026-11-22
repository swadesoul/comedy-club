import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const file=fileURLToPath(new URL('../scripts/run-gpt-live-take.mjs',import.meta.url));
test('dry-run makes no network connection and returns config only',()=>{
 const run=spawnSync(process.execPath,[file,'--dry-run'],{
   env:{...process.env,OPENAI_API_KEY:'not-used',COMEDY_LIVE_MAX_SECONDS:'15',
   COMEDY_LIVE_PAID_APPROVED:'NO'},
   encoding:'utf8',timeout:15000
 });
 assert.equal(run.status,0,run.stderr);
 const obj=JSON.parse(run.stdout);
 assert.equal(obj.dry_run,true);
 assert.equal(obj.websocket_opened,false);
 assert.equal(obj.model,'gpt-live-1.1');
});
test('non-dry run refuses to spend without explicit budget authorization',()=>{
 const run=spawnSync(process.execPath,[file],{
   env:{...process.env,COMEDY_LIVE_PAID_APPROVED:'NO'},
   encoding:'utf8',timeout:15000
 });
 assert.notEqual(run.status,0);
 assert.match(run.stderr,/authorization is missing/);
});
test('refuses overlong sessions even on non-network dry-run',()=>{
 const run=spawnSync(process.execPath,[file,'--dry-run'],{
   env:{...process.env,COMEDY_LIVE_MAX_SECONDS:'301'},
   encoding:'utf8',timeout:15000
 });
 assert.notEqual(run.status,0);
 assert.match(run.stderr,/Maximum session length/);
});
