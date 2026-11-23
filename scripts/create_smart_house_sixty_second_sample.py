#!/usr/bin/env python3
"""One-minute Smart House editorial sample with intro-first, clean joke end.
No voice regeneration, model costs, publication or current-master replacement.
Preserve the complete 3 spoken jokes and shorten only tails of audience reactions.
"""
from pathlib import Path
import hashlib,json,subprocess
root=Path('/opt/work/comedy-club-integration/audio')
src=root/'pilot-001-resinglab-v3/stems'
out=root/'pilot-001-sixty-second-review'
out.mkdir(parents=True,exist_ok=True)
run=lambda c: subprocess.run(c,check=True,capture_output=True,text=True,timeout=45)
def duration(path):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],text=True).strip())
# Intro, post-intro live audience, then the first complete three Marcus lines.
# Laughter only after joke lines; trim no speech. Crowd lasts 3.35 / 2.60 / 3.10 / 1.761 seconds.
clips=[
 ('00-announcer-resinglab.wav',None),
 ('-1-audience-opening.wav',3.35),
 ('01-marcus-resinglab.wav',None),
 ('01-audience-large.wav',2.60),
 ('02-marcus-resinglab.wav',None),
 ('02-audience-big.wav',3.10),
 ('03-marcus-resinglab.wav',None),
 ('03-audience-short.wav',None),
]
# Reuse verified opening crowd stem from ReSingLab V3.
opening=src/'-1-audience-opening.wav'
if not opening.exists():
 raise FileNotFoundError('Require verified original opening audience stem '+str(opening))
# Preserve complete final line, then fill remainder with natural fade rather than cut dialogue.
selection=[]
for index,(name,max_seconds) in enumerate(clips):
 p=src/name
 assert p.exists(),p
 target=out/(f'{index:02d}-'+name)
 c=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(p)]
 if max_seconds is not None:c+=['-t',str(max_seconds)]
 c+=['-ar','24000','-ac','2','-c:a','pcm_s16le',str(target)]
 run(c)
 selection.append(target)
durations=[duration(p) for p in selection]
total=sum(durations)
remaining=60-total
if remaining<0:raise ValueError('Spoken takes and selected laughter exceed 60 seconds '+str(total))
# Add the remaining duration as end-of-laugh decay; never fill with synthetic speech.
if remaining>.001:
 last=selection[-1]
 # Extend by quiet room to land a clean ending
 pad=out/'08-room-tail.wav'
 run(['ffmpeg','-hide_banner','-loglevel','error','-f','lavfi','-i','anullsrc=r=24000:cl=stereo','-t',str(remaining),'-c:a','pcm_s16le',str(pad)])
 selection.append(pad)
concat=out/'concat.txt'
concat.write_text(''.join("file '"+str(p).replace("'","'\\''")+"'\n" for p in selection))
wav=out/'smart-house-60s-intro-first-unreviewed.wav'
mp3=out/'smart-house-60s-intro-first-unreviewed.mp3'
run(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),
     '-af','afade=t=out:st=59.35:d=0.65,alimiter=limit=0.94','-t','60','-ac','2','-ar','24000','-c:a','pcm_s16le',str(wav)])
run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(wav),'-c:a','libmp3lame','-b:a','160k',str(mp3)])
receipt={'type':'60-second-private-comedy-preview','title':'The Smart House That Snitched on Me','intro_first':True,
  'order':['MAESTRO COMEDY INTRO','AUDIENCE AFTER INTRO','THREE COMPLETE ORIGINAL JOKES','LAUGHTER FADE'],
  'voice_model':'Existing Kokoro source stems; not GPT Live One','brand':'MAESTRO Comedy Club',
  'laughter_source':'CC0 real theater audience recording, Soundeffects4You Freesound 231258',
  'duration_wav_seconds':round(duration(wav),3),'duration_mp3_seconds':round(duration(mp3),3),
  'sha256':hashlib.sha256(mp3.read_bytes()).hexdigest(),
  'license_source':'https://freesound.org/people/Soundeffects4You/sounds/231258/',
  'published':False,'review_required':True,'original_master_unchanged':True,'vendor_cost_usd':0,
  'segments':list(zip([p.name for p in selection],[round(duration(p),3) for p in selection]))}
(out/'60s-receipt.json').write_text(json.dumps(receipt,indent=2))
assert abs(receipt['duration_wav_seconds']-60)<0.08
print(json.dumps(receipt,indent=2))

