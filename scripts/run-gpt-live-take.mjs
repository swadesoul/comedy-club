#!/usr/bin/env node
/** One short GPT Live One take, recorded into private WAV only.
 * SAFE BY DEFAULT: --dry-run is non-networked. Live requires TWO explicit
 * spending controls and a valid server-side API key. Never serve to public UI.
 * Uses the existing ReSingLab ws dependency, no new package installation.
 */
import {randomUUID} from 'node:crypto';
import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {LiveCapture} from '../engine/gpt-live-capture.mjs';

const model=process.env.COMEDY_LIVE_MODEL||'gpt-live-1.1';
const duration=Number(process.env.COMEDY_LIVE_MAX_SECONDS||15);
if(!['gpt-live-1','gpt-live-1.1'].includes(model))throw Error('Unapproved model');
if(!Number.isInteger(duration)||duration<5||duration>30)throw Error('Maximum session length must be 5–30 seconds');
const dryRun=process.argv.includes('--dry-run');
const scriptFile=process.env.COMEDY_LIVE_SCRIPT_FILE;
const source=scriptFile&&existsSync(scriptFile)?readFileSync(scriptFile,'utf8'):'';

const prompt=[
  'You are Marcus, an ORIGINAL fictional stand-up comedian in a small live theater.',
  'Deliver one short comic passage like an authentic live performance: engaged, conversational, precise timing, not a dry audiobook.',
  'Never impersonate a real comedian. Use your original character voice.',
  'No sound effects, canned laughter or artificial audience; the studio mixes the room sound after your recording.',
  'We are making a professionally reviewed recording. Deliver only the approved passage, without introductory filler.',
  source.slice(0,5000)
].join('\n');
const session={
  model,
  instructions:prompt,
  audio:{format:{type:'audio/pcm',rate:24000},output:{voice:'marin'}},
  delegation:{type:'client'}
};
const estimates={model,max_session_seconds:duration,
  indicative_voice_session_ceiling_usd_at_0_05_per_minute:Math.ceil(duration*5/60)/100,
  authorization_required:'COMEDY_LIVE_PAID_APPROVED=YES and COMEDY_LIVE_MAX_USD set to an explicit <= $0.10 limit',
  output:'private wav + session usage receipt; never automatically published'};
if(dryRun){
  process.stdout.write(JSON.stringify({dry_run:true,websocket_opened:false,...estimates,
    start_event:{type:'session.start',session}},null,2)+'\n');
  process.exit(0);
}
if(process.env.COMEDY_LIVE_PAID_APPROVED!=='YES')throw Error('Explicit owner-paid-session authorization is missing');
if(!source||source.length<100)throw Error('An approved script segment file is required');
const maxUsd=Number(process.env.COMEDY_LIVE_MAX_USD||'0');
if(!Number.isFinite(maxUsd)||maxUsd<=0||maxUsd>0.10)throw Error('Owner session spend cap must be positive and <= $0.10');
const upperBound=(duration/60)*0.05;
if(upperBound>maxUsd)throw Error('Session length exceeds approved cost ceiling');
const key=process.env.OPENAI_API_KEY;
if(!key||key.length<20)throw Error('Server-side OPENAI_API_KEY unavailable; never put a key in frontend code');
const cue=process.env.COMEDY_LIVE_CUE_FILE;
if(!cue||!existsSync(cue))throw Error('A real spoken cue file is required to trigger the audio-first model');
const cueRes=spawnSync('ffmpeg',['-hide_banner','-loglevel','error','-i',cue,
  '-ac','1','-ar','24000','-f','s16le','pipe:1'],{maxBuffer:4*1024*1024,timeout:20000});
if(cueRes.status!==0||!cueRes.stdout.length)throw Error('Cannot decode recording cue to PCM');
const require=createRequire('/opt/work/sites/resing/package.json');
const WebSocket=require('ws');
const ws=new WebSocket('wss://api.openai.com/v1/live/sessions',{
  headers:{Authorization:'Bearer '+key},
  handshakeTimeout:10000,maxPayload:2*1024*1024
});
const captured=new LiveCapture({expectedModel:model,maxAudioSeconds:duration});
const chunks=[];
for(let i=0;i<cueRes.stdout.length;i+=960)chunks.push(cueRes.stdout.subarray(i,i+960));
let cueTimer=null,limitTimer=null,closed=false,requestedClose=false,terminal=false;
const finish=(reason)=>{
  if(closed)return;closed=true;
  if(cueTimer)clearInterval(cueTimer);
  if(limitTimer)clearTimeout(limitTimer);
  if(!terminal){
    process.exitCode=2;
    process.stderr.write('LIVE_CAPTURE_INCOMPLETE '+reason+'; no record marked complete\n');
    ws.terminate();
    process.exitCode=2;
  }
};
ws.on('open',()=>ws.send(JSON.stringify({type:'session.start',event_id:randomUUID(),session})));
ws.on('message',raw=>{
  try {
    const event=JSON.parse(raw.toString());
    captured.ingest(event);
    if(event.type==='session.started'){
      let index=0;
      cueTimer=setInterval(()=>{
        if(index>=chunks.length){clearInterval(cueTimer);cueTimer=null;return}
        const audio=chunks[index++].toString('base64');
        ws.send(JSON.stringify({type:'session.input_audio.append',audio}));
      },20);
      limitTimer=setTimeout(()=>{
        if(cueTimer)clearInterval(cueTimer);
        requestedClose=true;
        ws.send(JSON.stringify({type:'session.close'}));
      },duration*1000);
    }
    if(event.type==='session.closed'){
      if(!requestedClose)throw Error('Session closed without the local bounded close request');
      const out=process.env.COMEDY_LIVE_OUTPUT_DIR||'/opt/work/comedy-club-integration/audio/gpt-live-review';
      const saved=captured.save(out,'smart-house-live-'+Date.now());
      terminal=true;
      writeFileSync(saved.receiptPath.replace('.receipt.json','.provenance.json'),
        JSON.stringify({user_approval_state:'unreviewed',broadcast_approved:false,source_script_sha_required:true,
          provider:'openai',model,session_id:saved.receipt.session_id,
          source_cue_path:cue,duration_bound_seconds:duration,
          session_closed_reason:event.reason,provider_usage:event.usage??null},null,2));
      process.stdout.write(JSON.stringify({status:'private_recording_captured',
        output_wav:saved.wavPath,recorded_seconds:saved.receipt.audio_seconds,
        resolved_model:saved.receipt.model,session_id:saved.receipt.session_id,
        final_usage_received:!!event.usage,
        published:false},null,2)+'\n');
      ws.close();finish('received terminal session.closed');
    }
    if(event.type==='error'||event.type==='session.error')
      throw Error('Live provider returned an error; audio invalid for release');
  } catch(e) {
    process.stderr.write('LIVE_CAPTURE_ERROR '+e.message+'\n');
    process.exitCode=2;finish('error');ws.terminate();
  }
});
ws.on('error',e=>{process.stderr.write('LIVE_SOCKET_ERROR '+e.message+'\n');finish('socket error')});
ws.on('close',()=>finish('connection closed without terminal receipt'));
setTimeout(()=>{if(!closed)finish('absolute timeout')},Math.max(25000,(duration+18)*1000));

