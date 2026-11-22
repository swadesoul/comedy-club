#!/usr/bin/env python3
"""RESINGLAB spoken-word Smart House rebuild. Uses original owner-approved comedy
script and existing original voice stems; FFmpeg streaming audio pipeline.
Does NOT claim GPT Live One, which needs separate provider verification.
No paid generation or station publish. Human review required.
"""
from pathlib import Path
import hashlib,json,subprocess,math,time
ROOT=Path('/opt/work/comedy-club-integration/audio')
ORIGINAL=ROOT/'pilot-001-review'
OUT=ROOT/'pilot-001-resinglab-v3'
OUT.mkdir(parents=True,exist_ok=True)
STEMS=OUT/'stems'
STEMS.mkdir(exist_ok=True)
CROWD=ROOT/'cc0/audience-theater-CC0-hq-preview.mp3'
assert CROWD.exists(), 'Licensed CC0 audience recording is missing'
EVENTS=[
('announcer','',None),
('marcus','', 'large'),
('marcus','', 'big'),
('marcus','', 'short'),
('marcus','', None),
('man','',None),
('marcus','', 'big'),
('woman','',None),
('marcus','', 'big'),
('marcus','', 'short'),
('marcus','', 'big'),
('marcus','', 'big'),
('marcus','', 'pause'),
('fridge','', 'big'),
('marcus','',None),
('crowd','',None),
('marcus','', 'final'),
]
def run(command):
 r=subprocess.run(command,capture_output=True,text=True,timeout=180)
 if r.returncode: raise RuntimeError('ffmpeg failure: '+r.stderr[-1200:])
def seconds(path):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nw=1:nk=1',str(path)],text=True).strip())
def voice(i,role):
 src=ORIGINAL/f'{i:02d}-{role}.wav'
 assert src.exists(),src
 target=STEMS/f'{i:02d}-{role}-resinglab.wav'
 if role=='announcer':
  filt='apad=pad_dur=5,atrim=0:5'
 else:
  tempo=.82 if role=='marcus' else (.90 if role in ('man','woman','crowd') else .94)
  # Short club mic reflections, not long echo; center-stage direct voice dominates.
  filt=f'atempo={tempo},aecho=0.81:0.44:47|83|129:0.06|0.04|0.02'
  if role=='man':filt+=',pan=stereo|c0=0.65*c0|c1=0.93*c1'
  if role=='woman':filt+=',pan=stereo|c0=0.94*c0|c1=0.66*c1'
  if role=='fridge':filt+=',volume=0.72'
 run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(src),
      '-af',filt,'-ac','2','-ar','24000','-c:a','pcm_s16le',str(target)])
 return target
# This is a real theater audience recording, not a solo laugh loop.
# Use non-overlapping source windows, varied reactions, spread preserved in stereo.
def reaction(i,kind):
 if kind=='pause':
  dur=1.05
  target=STEMS/f'{i:02d}-hold.wav'
  run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','lavfi','-i','anullsrc=r=24000:cl=stereo',
       '-t',str(dur),'-c:a','pcm_s16le',str(target)])
  return target
 durations={'short':1.9,'large':3.3,'big':3.8,'final':5.9,'opening':3.35}
 dur=durations[kind]
 target=STEMS/f'{i:02d}-audience-{kind}.wav'
 # Nonrepeating regions are chosen across the original 96-sec room recording.
 offset={-1:2.0,1:9.8,2:20.7,3:29.6,6:37.5,8:47.1,9:54.4,10:62.8,11:70.8,13:79.1,16:87.2}.get(i,(i*7.3)%85)
 offset=min(offset,max(0,seconds(CROWD)-dur-.2))
 af=f'volume={0.47 if kind=="short" else .62},afade=t=in:st=0:d=0.12,afade=t=out:st={max(.2,dur-.65)}:d=0.6'
 run(['ffmpeg','-y','-hide_banner','-loglevel','error','-ss',str(offset),'-t',str(dur),
      '-i',str(CROWD),'-af',af,'-ac','2','-ar','24000','-c:a','pcm_s16le',str(target)])
 return target
def main():
 playlist=[]
 cue=[]
 first=reaction(-1,'opening');playlist.append(first)
 cue.append({'at_sec':0,'type':'opening_real_theater_audience','duration':round(seconds(first),2)})
 for i,(role,_,kind) in enumerate(EVENTS):
  src=voice(i,role)
  elapsed=sum(seconds(p) for p in playlist)
  cue.append({'at_sec':round(elapsed,2),'type':'speech','speaker':role,'source_stem':src.name})
  playlist.append(src)
  if kind:playlist.append(reaction(i,kind))
  if role in ('man','woman'):
   # Short breath rather than abrupt answer cuts
   playlist.append(reaction(i,'pause'))
 target=OUT/'smart-house-resinglab-v3-unreviewed.wav'
 concat=OUT/'concat.txt'
 concat.write_text(''.join("file '"+str(x).replace("'","'\\''")+"'\n" for x in playlist))
 run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),
      '-af','alimiter=limit=0.92:attack=5:release=65,afade=t=out:st=174:d=1.2',
      '-ac','2','-ar','24000','-c:a','pcm_s16le',str(target)])
 # Check measured actual runtime, no silence to fake 3m. If over budget, refuse promotion.
 total=seconds(target)
 mp3=OUT/'smart-house-resinglab-v3-unreviewed.mp3'
 run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(target),'-codec:a','libmp3lame',
      '-b:a','160k',str(mp3)])
 record={'title':'The Smart House That Snitched on Me','status':'needs_review',
   'source':'resinglab_spoken_word_production','speech_engine':'original Kokoro CPU stems reused, remixed through RESINGLAB production workflow',
   'GPT_Live_One_rendered':False,
   'separate_voice_roles':['announcer','marcus','man','woman','fridge','crowd'],
   'room_reaction_source':'Soundeffects4You CC0 theater audience recording, Freesound 231258',
   'source_license':'https://freesound.org/people/Soundeffects4You/sounds/231258/',
   'real_crowd_recording':True,
   'microphone_reverb':'47/83/129ms low-wet reflections (aecho)',
   'opening':'3.35 seconds laughter before five-second station liner',
   'duration_seconds':round(total,3),'duration_within_180':total<=180,
   'audio_sha256':hashlib.sha256(mp3.read_bytes()).hexdigest(),
   'mp3_bytes':mp3.stat().st_size,'published':False,
   'audio_file':str(mp3),'cues':cue}
 (OUT/'render-receipt.json').write_text(json.dumps(record,indent=2))
 print(json.dumps({key:record[key] for key in ('status','duration_seconds','duration_within_180','mp3_bytes','audio_sha256')},indent=2))
 if total>180:raise RuntimeError('Duration exceeded 180 second production cap; keep unreleased.')
if __name__=='__main__':main()

