import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,readFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';
import {LiveCapture} from '../engine/gpt-live-capture.mjs';
const started={type:'session.started',session:{id:'live-test-fixture',model:'gpt-live-1.1'}};
const samples=Buffer.from([0,0,1,0,255,127,0,128]);
test('captures authentic event-shaped PCM and produces valid RIFF PCM WAV',()=>{
  const c=new LiveCapture({expectedModel:'gpt-live-1.1'});
  c.ingest(started);
  c.ingest({type:'session.output_audio.delta',delta:samples.subarray(0,4).toString('base64')});
  c.ingest({type:'session.output_audio.delta',delta:samples.subarray(4).toString('base64')});
  c.ingest({type:'session.closed',reason:'close_requested',usage:{audio_seconds:1}});
  const p=mkdtempSync(path.join(tmpdir(),'comedy-live-capture-test-'));
  const {wavPath,receipt}=c.save(p,'unit-fixture');
  const wav=readFileSync(wavPath);
  assert.equal(wav.toString('utf8',0,4),'RIFF');
  assert.equal(wav.toString('utf8',8,12),'WAVE');
  assert.equal(wav.readUInt32LE(24),24000);
  assert.equal(wav.readUInt16LE(22),1);
  assert.equal(wav.readUInt32LE(40),samples.length);
  assert.deepEqual(wav.subarray(44),samples);
  assert.equal(receipt.session_id,'live-test-fixture');
  assert.equal(receipt.model,'gpt-live-1.1');
  assert.equal(receipt.broadcast_authorized,false);
});
test('rejects spoofed resolved model, missing closure, and missing audio',()=>{
  assert.throws(()=>new LiveCapture().ingest({type:'session.started',session:{id:'x',model:'kokoro'}}),/Unexpected model/);
  const c=new LiveCapture();c.ingest(started);
  assert.throws(()=>c.receipt(),/complete session close/);
  assert.throws(()=>c.ingest({type:'session.closed',reason:'network_timeout'}),/Unexpected live session closure/);
  const d=new LiveCapture();d.ingest(started);d.ingest({type:'session.closed',reason:'close_requested'});
  assert.throws(()=>d.receipt(),/zero recorded audio/);
});
test('enforces byte budget and refuses truncated frames',()=>{
  const c=new LiveCapture({maxAudioSeconds:0.0001});c.ingest(started);
  assert.throws(()=>c.ingest({type:'session.output_audio.delta',delta:samples.toString('base64')}),/recording cap/);
  assert.throws(()=>c.ingest({type:'session.output_audio.delta',delta:Buffer.from([1]).toString('base64')}),/complete 2-byte/);
});
test('rejects chunks before session.started',()=>{
 const c=new LiveCapture();
 assert.throws(()=>c.ingest({type:'session.output_audio.delta',delta:samples.toString('base64')}),/Out-of-order/);
});

test('accepts official session.started with ID and status but no echoed model',()=>{
 const c=new LiveCapture();
 c.ingest({type:'session.started',session:{id:'live-official-sample',expires_at:1788307200,status:'active'}});
 c.ingest({type:'session.output_audio.delta',delta:samples.toString('base64')});
 c.ingest({type:'session.closed',reason:'close_requested'});
 const receipt=c.receipt();
 assert.equal(receipt.model_confirmation,'server_accepted_requested_model');
 assert.equal(receipt.model,'gpt-live-1.1');
});
