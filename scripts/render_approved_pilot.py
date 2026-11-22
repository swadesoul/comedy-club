#!/usr/bin/env python3
"""Produce original approved pilot using existing zero-vendor-spend SWADE Kokoro CPU TTS.
Stages private, audio requires human listening review before any publication.
Audience sounds: public domain ezwa (Commons Laughter.ogg), CC0 sagetyrtle
(Commons Laughter(s).ogg). Original comedians are fictional, no voice impersonation.
"""
import hashlib, json, os, subprocess, time, wave, re, sys
from pathlib import Path
from io import BytesIO
import requests
import numpy as np
import soundfile as sf

ROOT=Path('/opt/work/comedy-club-integration/audio')
SOURCE=ROOT/'cc0'
STAGE=ROOT/'pilot-001-review'
STAGE.mkdir(parents=True,exist_ok=True)
VOICE={'announcer':'kokoro:am_echo','marcus':'kokoro:am_onyx','man':'kokoro:am_liam',
       'woman':'kokoro:af_bella','fridge':'kokoro:af_sky','crowd':'kokoro:af_nicole'}
VOICE_URL='http://172.16.0.1:8790/v1/speak'
TOKEN=next(l.partition('=')[2].strip().strip('"').strip("'") for l in open('/opt/swade-secrets/voice-service.env') if l.startswith('VOICE_SERVICE_TOKEN='))
SESSION=requests.Session();SESSION.headers.update({'Authorization':'Bearer '+TOKEN})
SR=24000
# Ordered audience + comedian performances. All dialogue is from founder-approved routine.
EVENTS=[
 ('announcer',"You're live at Maestro Comedy Club! Let the laughter begin!",''),
 ('marcus',"I bought a smart house last month. Everything's connected. Refrigerator, thermostat, doorbell, lights. Even the toilet got Wi-Fi! First night, my wife said, baby, this house is gonna make our lives so much easier. I said, wonderful. But somebody needs to tell this house one thing. What happens in this house STAYS in this house!",'large'),
 ('marcus',"Three days later, my refrigerator sent my wife a notification. Said, Marcus consumed cheesecake at two forty seven A.M. My wife comes downstairs. Who been eating cheesecake? I said, I don't know! Maybe somebody broke in! She said, then why does the security camera show you eating it with a FORK and a flashlight?",'big'),
 ('marcus',"I'm paying a mortgage on a house that's building a case against me!",'short'),
 ('marcus',"Anybody here got one of these smart houses?",''),
 ('man',"Mine listens to everything!",''),
 ('marcus',"EVERYTHING? Brother, you living in a house or testifying before Congress?",'big'),
 ('woman',"Just unplug it!",''),
 ('marcus',"Ma'am, I tried that! The house sent me an email saying, we noticed you're trying to disconnect from the relationship.",'big'),
 ('marcus',"Even the HOUSE won't let me break up peacefully!",'short'),
 ('marcus',"Then yesterday, I got into an argument with my wife. I said, I never said that! You know what happened? The living room speaker turned on by itself! It said, actually Marcus, you said that Tuesday at eight fourteen P.M. Would you like me to play the recording?",'big'),
 ('marcus',"I said, whose side are you ON?! That speaker said, based on household usage patterns, hers.",'big'),
 ('marcus',"So last night, I finally figured out how to fix it. I went into the settings. Changed every password. Turned off every notification. I told my wife, baby, we're taking our privacy back! She said, good! Then, in the dark, I heard a little voice from the kitchen.",'silence'),
 ('fridge',"Marcus, you still owe us for the cheesecake.",'big'),
 ('marcus',"I TOLD YOU! WHAT HAPPENS IN THIS HOUSE!",''),
 ('crowd',"STAYS IN THIS HOUSE!",''),
 ('marcus',"EXCEPT MY BUSINESS! THE HOUSE GOT A PODCAST!",'final'),
]
def read_wav(data):
 buf=BytesIO(data);audio,sr=sf.read(buf,dtype='float32',always_2d=True)
 assert sr==SR, sr
 return audio
def speak(role,text,index):
 path=STAGE/f'{index:02d}-{role}.wav'
 if path.exists():
  y,s=sf.read(path,dtype='float32',always_2d=True)
  if s==SR and len(y)>SR*.3:return y
 start=time.time()
 r=SESSION.post(VOICE_URL,json={'text':text,'voice':VOICE[role],'engine':'kokoro','format':'wav',
   'speed':1.06 if role=='marcus' else 1.0,'normalize':False},timeout=200)
 if not r.ok:raise RuntimeError('Kokoro CPU generation failed ('+str(r.status_code)+')')
 path.write_bytes(r.content)
 audio=read_wav(r.content)
 print('generated',index,role,round(len(audio)/SR,1),'sec',round(time.time()-start,1),'wall',flush=True)
 return audio
def cc0(name):
 src=SOURCE/name
 out=STAGE/(name+'.wav')
 if not out.exists():subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(src),'-ar',str(SR),'-ac','2',str(out)],check=True)
 audio,s=sf.read(out,dtype='float32',always_2d=True)
 assert s==SR
 return audio
def adjust_spoken_pace(audio,role):
    if role=='announcer':return audio
    tempo=.80 if role=='marcus' else (.87 if role in ('man','woman','crowd') else .85)
    buf=BytesIO();sf.write(buf,audio,SR,format='WAV',subtype='PCM_16')
    p=subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','wav','-i','pipe:0',
        '-filter:a','atempo='+str(tempo),'-ar',str(SR),'-f','wav','pipe:1'],
        input=buf.getvalue(),capture_output=True,timeout=60,check=True)
    slowed,_=sf.read(BytesIO(p.stdout),dtype='float32',always_2d=True)
    return slowed

def multichannel(a,role):
 if a.shape[1]==1:a=np.repeat(a,2,axis=1)
 if role=='man':a[:,0]*=.64;a[:,1]*=.88
 if role=='woman':a[:,0]*=.9;a[:,1]*=.60
 if role=='fridge':a*=.67
 if role=='crowd':a*=.82
 return a
def laughter(kind,index):
 if kind=='silence':return np.zeros((int(1.5*SR),2),dtype='float32')
 src=SOURCE/'laughter-variety.ogg' if kind in ('big','final') else SOURCE/'laughter.ogg'
 a=cc0(src.name)
 duration={'short':2.0,'large':4.0,'big':4.5,'final':7.0}[kind]
 n=int(duration*SR)
 # Avoid repeats from the same waveform region by choosing deterministic offsets.
 off=(index*19007) % max(1,len(a)-n)
 part=a[off:off+n].copy()
 if len(part)<n:part=np.pad(part,((0,n-len(part)),(0,0)))
 fade=min(int(.22*SR),n//5)
 part[:fade]*=np.linspace(0,1,fade)[:,None]
 part[-int(.42*SR):]*=np.linspace(1,0,int(.42*SR))[:,None]
 part*=.28 if kind=='short' else .36
 return part.astype('float32')
def main():
 events=[];frames=[]
 for i,(role,text,react) in enumerate(EVENTS):
  audio=multichannel(adjust_spoken_pace(speak(role,text,i),role),role)
  if i==0:
    # Precisely five-second liner; pad when shorter, modestly increase pace if long.
    goal=5*SR
    if len(audio)>goal:
     import scipy.signal
     audio=scipy.signal.resample(audio,goal,axis=0).astype('float32')
    elif len(audio)<goal:audio=np.pad(audio,((0,goal-len(audio)),(0,0)))
  start=sum(len(x) for x in frames)/SR
  frames.append(audio)
  events.append({'position_seconds':round(start,2),'speaker':role,'text':text,'duration_seconds':round(len(audio)/SR,2),'react':react})
  if react:
   part=laughter(react,i)
   frames.append(part)
  elif role=='woman' or role=='man':
   frames.append(np.zeros((int(.6*SR),2),dtype='float32'))
 raw=np.concatenate(frames,axis=0)
 # Natural CC0 applause tail brings an underlength performance to the exact 3:00 target.
 target=int(179.9*SR)
 if len(raw)<target and (SOURCE/'applause.ogg').exists():
  applause=cc0('applause.ogg')
  n=target-len(raw)
  part=applause[:n].copy()
  if len(part)<n:part=np.pad(part,((0,n-len(part)),(0,0)))
  fadein=min(int(.65*SR),n//4)
  fadeout=min(int(1.2*SR),n//3)
  if fadein:part[:fadein]*=np.linspace(0,1,fadein)[:,None]
  if fadeout:part[-fadeout:]*=np.linspace(1,0,fadeout)[:,None]
  part*=.23
  raw=np.concatenate([raw,part],axis=0)
 duration=len(raw)/SR
 print('UNEDITED_SECONDS',round(duration,2),'WORDS',sum(len(t.split()) for _,t,_ in EVENTS),flush=True)
 # Delivery target 180 seconds: do not aggressively speed up laughs/punchlines.
 if duration>183:
  print('NEEDS_PACING_EDIT; keeps master unreleased',flush=True)
 # Normalize master to 95% peak to avoid clipping
 peak=float(np.max(np.abs(raw)))
 if peak>0:raw*=min(0.93/max(peak,.01),1.7)
 fade=int(.4*SR);raw[-fade:]*=np.linspace(1,0,fade)[:,None]
 master=STAGE/'pilot-001-unreviewed.wav'
 sf.write(master,raw,SR,subtype='PCM_16')
 mp3=STAGE/'pilot-001-unreviewed.mp3'
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(master),'-codec:a','libmp3lame','-b:a','160k',str(mp3)],check=True)
 receipt={'id':'comedy-pilot-001','status':'needs_human_listening_review','published':False,
   'rights':'original approved script; CC0/PD laughter credited below',
   'sources':['https://commons.wikimedia.org/wiki/File:Laughter.ogg',
      'https://commons.wikimedia.org/wiki/File:Laughter(s).ogg',
      'https://commons.wikimedia.org/wiki/File:Sound_Effects_-_Applause_after_a_concert.ogg'],
   'voice_provider':'SWADESOUL_KOKORO_CPU',
   'external_voice_cost_usd':0,'duration_seconds':round(duration,2),
   'target_duration_seconds':180,'duration_passed':duration<=180,
   'events':events,'sha256':hashlib.sha256(mp3.read_bytes()).hexdigest(),
   'audio_file':str(mp3)}
 (STAGE/'production-receipt.json').write_text(json.dumps(receipt,indent=2))
 print('DRAFT',mp3,'SIZE',mp3.stat().st_size,'SHA256',receipt['sha256'],'DURATION_PASS',receipt['duration_passed'],flush=True)
if __name__=='__main__':main()
