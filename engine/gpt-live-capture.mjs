import { createHash } from 'node:crypto';
import { writeFileSync, mkdirSync } from 'node:fs';
import path from 'node:path';

/**
 * GPT Live One capture ledger. Handles real primary /v1/live/sessions
 * audio deltas (mono PCM16LE at 24000 Hz).
 * Does not claim model provenance unless resolved session ID + model match.
 * No provider calls in this module.
 */
export class LiveCapture {
  constructor({expectedModel='gpt-live-1.1', maxAudioSeconds=180}={}) {
    this.expectedModel=expectedModel;
    this.maxAudioSeconds=maxAudioSeconds;
    this.sessionId=null;
    this.resolvedModel=null;
    this.audioChunks=[];
    this.events=[];
    this.sampleBytes=0;
    this.finished=false;
    this.started=false;
    this.usage=null;
    this.failure=null;
  }
  ingest(message) {
    const e=typeof message==='string'?JSON.parse(message):message;
    if (!e||typeof e.type!=='string') throw Error('Invalid session event');
    if(e.type==='session.started') {
      const m=e.session?.model || e.session?.config?.model || null;
      const id=e.session?.id;
      if(!id||typeof id!=='string')throw Error('Live session has no identifier');
      if(m && m!==this.expectedModel)throw Error('Unexpected model in live session: '+m);
      if(this.started)throw Error('Duplicate live session start');
      this.started=true;this.sessionId=id;this.resolvedModel=m||this.expectedModel;
      this.modelConfirmedByProvider=!!m;
      this.events.push({type:e.type,session_id:id,requested_model:this.expectedModel,confirmed_model:m});
    } else if (e.type==='session.output_audio.delta') {
      if(!this.started||this.finished)throw Error('Out-of-order audio chunk');
      if(this.resolvedModel!==this.expectedModel)throw Error('Expected GPT Live One, received '+this.resolvedModel);
      if(typeof e.delta!=='string'|| !/^[A-Za-z0-9+/]*={0,2}$/.test(e.delta))throw Error('Invalid base64 audio');
      const bytes=Buffer.from(e.delta,'base64');
      if(bytes.length===0||bytes.length%2!==0)throw Error('PCM16 samples must contain complete 2-byte samples');
      if(this.sampleBytes+bytes.length>this.maxAudioSeconds*24000*2)throw Error('Audio exceeds recording cap');
      this.sampleBytes+=bytes.length;
      this.audioChunks.push(bytes);
    } else if(e.type==='session.closed') {
      if(!this.started)throw Error('Live session closed without session.started');
      if(e.reason!=='close_requested')throw Error('Unexpected live session closure: '+(e.reason||'unknown'));
      this.finished=true;this.usage=e.usage??null;
      this.events.push({type:e.type,usage_recorded:Boolean(this.usage)});
    } else if(e.type==='error' || e.type==='session.error') {
      this.failure=e.error?.message||'Live session error';
    } else if(e.type==='session.output_transcript.delta') {
      this.events.push({type:e.type,text:String(e.delta||'').slice(0,1000)});
    }
  }
  receipt() {
    if(this.failure)throw Error('Provider error: '+this.failure);
    if(!this.finished||!this.started||!this.sessionId)throw Error('No complete session close receipt');
    if(this.resolvedModel!==this.expectedModel)throw Error('Wrong model: '+this.resolvedModel);
    if(this.sampleBytes===0)throw Error('Session had zero recorded audio');
    const audio=Buffer.concat(this.audioChunks);
    return {
      verified_source:true,
      model_confirmation:this.modelConfirmedByProvider?'server_explicit_model':'server_accepted_requested_model',
      model:this.resolvedModel,
      session_id:this.sessionId,
      source:'openai_live_primary_websocket',
      sample_rate:24000,
      channels:1,
      encoding:'pcm_s16le',
      audio_seconds:audio.length/(24000*2),
      audio_bytes:audio.length,
      sha256:createHash('sha256').update(audio).digest('hex'),
      closed:true,
      provider_usage:this.usage,
      broadcast_authorized:false,
      approval:'needs_human_review'
    };
  }
  save(directory,name='segment-001') {
    const r=this.receipt();
    mkdirSync(directory,{recursive:true,mode:0o700});
    const raw=Buffer.concat(this.audioChunks);
    const wav=Buffer.alloc(44);
    const rate=24000;
    wav.write('RIFF',0);
    wav.writeUInt32LE(36+raw.length,4);
    wav.write('WAVE',8);
    wav.write('fmt ',12);
    wav.writeUInt32LE(16,16);
    wav.writeUInt16LE(1,20);
    wav.writeUInt16LE(1,22);
    wav.writeUInt32LE(rate,24);
    wav.writeUInt32LE(rate*2,28);
    wav.writeUInt16LE(2,32);
    wav.writeUInt16LE(16,34);
    wav.write('data',36);
    wav.writeUInt32LE(raw.length,40);
    const wavPath=path.join(directory,name+'.wav');
    writeFileSync(wavPath,Buffer.concat([wav,raw]),{mode:0o600,flag:'wx'});
    const receiptPath=path.join(directory,name+'.receipt.json');
    writeFileSync(receiptPath,JSON.stringify({...r,wav_path:wavPath},null,2),{mode:0o600,flag:'wx'});
    return {wavPath,receiptPath,receipt:r};
  }
}

