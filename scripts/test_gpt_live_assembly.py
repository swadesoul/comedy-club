#!/usr/bin/env python3
"""First offline test: two-part Live recording assembly with FFmpeg.
Does not call OpenAI or claim GPT Live One was captured.
A live production must supply real GPT Live output WAVs and a verified session ID.
"""
import json,subprocess,hashlib
from pathlib import Path
root=Path('/opt/work/comedy-club-integration/audio')
sample=root/'pilot-001-resinglab-v3/smart-house-resinglab-v3-unreviewed.mp3'
out=root/'gpt-live-first-test'
out.mkdir(parents=True,exist_ok=True)
def run(*args):
 subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=45)
def dur(path):
 return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],text=True).strip())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
assert sample.exists()
# Dry run from an existing master, not a fabricated GPT Live output.
parts=[out/'performance-part-1.wav',out/'performance-part-2.wav']
run('ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(sample),'-t','100','-ar','24000','-ac','2','-c:a','pcm_s16le',str(parts[0]))
run('ffmpeg','-hide_banner','-loglevel','error','-y','-ss','100','-i',str(sample),'-ar','24000','-ac','2','-c:a','pcm_s16le',str(parts[1]))
concat=out/'segments.txt'
concat.write_text(''.join(f"file '{p}'\n" for p in parts))
master=out/'first-test-joined.wav'
run('ffmpeg','-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(concat),'-ar','24000','-ac','2','-c:a','pcm_s16le',str(master))
delta=abs(dur(master)-dur(sample))
assert delta<.09,(dur(master),dur(sample),delta)
receipt={'test':'ffmpeg-two-part-assembly',
 'source':'existing Kokoro/RESINGLAB V3 private master; NO GPT Live One generated',
 'gpt_live_1_session_created':False,'charged_usd':0,'published':False,
 'source_duration_s':round(dur(sample),3),
 'part_1_duration_s':round(dur(parts[0]),3),'part_2_duration_s':round(dur(parts[1]),3),
 'joined_duration_s':round(dur(master),3),'duration_delta_s':round(delta,3),
 'result':'PASS','sha256':sha(master)}
(out/'dry-run-receipt.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))

