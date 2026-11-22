"""Native Maestro Comedy Club adapter. Reuses existing factory identity, DB and B2.
Public reads are conservative: no sample records; no adult audio without age gate.
Private editing is admin-only pending audited customer entitlements.
"""
import json
import re
import hashlib
import base64
import io
import uuid
from urllib.parse import urlsplit
from station_libraries import identity, AccessError, fail

PUBLIC_RATINGS=('PG','PG-13')
MAX_BYTES=65536

def published(f):
    people=f.db('comedy_comedians',
        filters={'status':'in.(published,in_development)','rights_confirmed':'is.true'},
        select='id,slug,display_name,biography,artwork_path,default_rating,status',order='display_name.asc',limit=100)
    # The public site may show real cast profiles under development, never a fake
    # completed routine, fake listener counts, or phantom audio.
    routines=f.db('comedy_routines',
        filters={'state':'eq.published','rights_confirmed':'is.true',
                 'rating':'in.(PG,PG-13)','audio_b2_key':'not.is.null'},
        select='id,comedian_id,title,rating,duration_ms,created_at',order='created_at.desc',limit=500)
    return {'comedians':people,'routines':[
        {**r,'audio_url':'/comedy-api/media/'+r['id']} for r in routines
    ],'verified':True,'source':'maestroradio.comedy_catalog',
    'adult_inventory_hidden':True}

def auth(f,handler):
    actor=identity(f,handler.headers.get('Authorization',''))
    if not actor['admin']:fail('Comedy management requires an authorized administrator until customer billing is verified.',403)
    return actor

def receive(handler):
    if handler.command!='POST':fail('Use POST to save a routine.',405)
    try:length=int(handler.headers.get('Content-Length','0'))
    except ValueError:fail('Invalid body size.',400)
    if length<2 or length>MAX_BYTES:fail('Request too large.',413)
    try:body=json.loads(handler.rfile.read(length))
    except (ValueError,UnicodeDecodeError):fail('Invalid JSON.',400)
    if not isinstance(body,dict):fail('Invalid body.',400)
    return body

def create_draft(f,actor,b):
    title=str(b.get('title') or '').strip()
    script=str(b.get('script') or '').strip()
    rating=str(b.get('rating') or '')
    cid=str(b.get('comedian_id') or '')
    if len(title)<3 or len(title)>200:fail('Title must be 3–200 characters.')
    if len(script)<20 or len(script)>16000:fail('Script must be 20–16,000 characters.')
    if rating not in ('PG','PG-13','R'):fail('Invalid rating.')
    try:cid=f.uid(cid)
    except Exception:fail('Choose a real comedian profile.')
    profiles=f.db('comedy_comedians',filters={'id':'eq.'+cid},select='id,owner_id,status',limit=1)
    if not profiles:fail('Comedian does not exist.',404)
    if profiles[0]['status']=='retired':fail('Comedian is retired.',409)
    if profiles[0].get('owner_id') not in (None,actor['id']) and not actor['superadmin']:
        fail('No permission for this comedian.',403)
    if b.get('rights_confirmed') is not True:fail('Confirm ownership or written routine licensing.')
    rows=f.db('comedy_routines','POST',{
        'owner_id':actor['id'],'comedian_id':cid,'title':title,'script':script,
        'rating':rating,'rights_confirmed':True,'state':'draft'},
        select='id,title,rating,state,comedian_id,created_at')
    return {'ok':True,'routine':rows[0]}

def review_audio(f,actor,routine_id):
    try:rid=f.uid(routine_id)
    except Exception:fail('Invalid routine.',404)
    rows=f.db('comedy_routines',filters={'id':'eq.'+rid,'owner_id':'eq.'+actor['id']},
        select='id,audio_b2_key,state',limit=1)
    if not rows or not rows[0].get('audio_b2_key'):fail('No actual audio ready for review.',404)
    key=rows[0]['audio_b2_key']
    if not key.startswith('comedy/review/'+actor['id']+'/'+rid+'/'):
        fail('Review audio path failed tenant check.',403)
    return {'ok':True,'audio_url':f.signed(key),'expires_seconds':900,'state':rows[0]['state']}

def live_take_review(f,actor,routine_id):
    # Single owner-approved production pilot. Never substitute this brief
    # verified voice take for the three-minute official Comedy Club master.
    pilot='026c0be2-62e3-41b3-886f-7f3a9b427980'
    try:rid=f.uid(routine_id)
    except Exception:fail('Invalid routine.',404)
    if rid!=pilot:fail('No GPT Live One take exists for this routine.',404)
    rows=f.db('comedy_routines',filters={'id':'eq.'+rid,'owner_id':'eq.'+actor['id']},
        select='id,state,owner_id',limit=1)
    if len(rows)!=1:fail('Routine not available for this account.',404)
    if rows[0]['state'] not in ('needs_review','script_approved'):
        fail('Review state is not available.',409)
    key='comedy/review/'+actor['id']+'/'+rid+'/smart-house-gpt-live-1.1-first-take-unreviewed.mp3'
    return {'ok':True,'audio_url':f.signed(key),
        'expires_seconds':900,'model':'gpt-live-1.1',
        'duration_seconds':24.98,'take_type':'opening_only',
        'published':False,'state':'needs_review'}

def receive_upload(handler):
    try:length=int(handler.headers.get('Content-Length','0'))
    except ValueError:fail('Invalid upload length.',400)
    if length<10 or length>7*1024*1024:fail('Image must be 5 MB or less.',413)
    try:body=json.loads(handler.rfile.read(length))
    except Exception:fail('Invalid upload payload.',400)
    if not isinstance(body,dict) or body.get('rights_confirmed') is not True:
        fail('Confirm photo ownership and subject consent, if applicable.',403)
    label=str(body.get('label') or 'Comedy studio asset').strip()[:140]
    if not label:fail('Image label required.')
    declared=str(body.get('mime_type') or '')
    if declared not in ('image/jpeg','image/png','image/webp'):fail('Unsupported image type.',415)
    try:raw=base64.b64decode(body.get('base64') or '',validate=True)
    except Exception:fail('Invalid image encoding.',400)
    if len(raw)>5*1024*1024 or not raw:fail('Image exceeds the limit.',413)
    return label,raw

def create_image(f,actor,handler):
    from PIL import Image,ImageOps,UnidentifiedImageError
    label,raw=receive_upload(handler)
    try:
        Image.MAX_IMAGE_PIXELS=12000000
        with Image.open(io.BytesIO(raw)) as original:
            original.verify()
        with Image.open(io.BytesIO(raw)) as original:
            if original.width>5000 or original.height>5000:fail('Image dimensions exceed limit.',413)
            img=ImageOps.exif_transpose(original)
            img.thumbnail((2400,2400))
            if img.mode not in ('RGB','RGBA'):img=img.convert('RGB')
            out=io.BytesIO()
            img.save(out,format='WEBP',quality=88,method=4)
            data=out.getvalue()
    except (UnidentifiedImageError,Image.DecompressionBombError,ValueError):
        fail('Could not validate this image.',415)
    aid=str(uuid.uuid4())
    key='comedy/assets/'+actor['id']+'/'+aid+'.webp'
    sha=f.store(key,data,'image/webp')
    rows=f.db('comedy_assets','POST',{'id':aid,'owner_id':actor['id'],'object_key':key,
        'label':label,'mime_type':'image/webp','bytes':len(data),'sha256':sha,
        'consent_confirmed':True},select='id,label,bytes,created_at')
    return {'ok':True,'asset':rows[0]}

def asset_url(f,actor,aid):
    try:aid=f.uid(aid)
    except Exception:fail('Invalid asset reference.',404)
    rows=f.db('comedy_assets',filters={'id':'eq.'+aid,'owner_id':'eq.'+actor['id']},
        select='id,object_key',limit=1)
    if not rows:fail('Asset does not belong to this account.',404)
    if not rows[0]['object_key'].startswith('comedy/assets/'+actor['id']+'/'):
        fail('Asset path is not authorized.',403)
    return f.signed(rows[0]['object_key'])

def list_private(f,actor):
    drafts=f.db('comedy_routines',filters={'owner_id':'eq.'+actor['id']},
        select='id,comedian_id,title,script,rating,state,rights_confirmed,duration_ms,audio_b2_key,created_at',
        order='created_at.desc',limit=200)
    for draft in drafts:
        draft['audio_ready']=bool(draft.pop('audio_b2_key',None))
        draft['live_take_ready']=draft['id']=='026c0be2-62e3-41b3-886f-7f3a9b427980' and draft['state']=='needs_review'
    plans=f.db('comedy_batch_plans',filters={'owner_id':'eq.'+actor['id']},
        select='id,request_id,routine_ids,status,created_at',order='created_at.desc',limit=100)
    assets=f.db('comedy_assets',filters={'owner_id':'eq.'+actor['id']},
        select='id,label,bytes,created_at',order='created_at.desc',limit=100)
    return {'routines':drafts,'batches':plans,'assets':assets,'verified':True}

def plan_batch(f,actor,b):
    raw=b.get('routine_ids')
    if not isinstance(raw,list) or not 1<=len(raw)<=10:fail('Choose 1–10 actual saved routines.')
    try:ids=[f.uid(x) for x in raw];request_id=f.uid(b.get('request_id'))
    except Exception:fail('Invalid batch or routine identifier.')
    if len(set(ids))!=len(ids):fail('Do not select a routine twice.')
    drafts=f.db('comedy_routines',filters={'owner_id':'eq.'+actor['id'],
        'id':'in.('+','.join(ids)+')'},select='id,title,rating,comedian_id,state,rights_confirmed',limit=10)
    if len(drafts)!=len(ids) or any(not r['rights_confirmed'] or r['state'] not in ('draft','script_approved','approved') for r in drafts):
        fail('The selected routines must be owned and rights-confirmed.',403)
    seen={r['id']:r for r in drafts}
    settings=b.get('studio_settings') or {}
    if not isinstance(settings,dict):fail('Invalid studio settings.')
    capacity=settings.get('audience_size',100)
    if type(capacity) is not int or capacity not in (25,50,100,150,250):fail('Invalid audience capacity.')
    if settings.get('room_tone','intimate') not in ('intimate','warm','lively'):fail('Invalid club acoustics.')
    if settings.get('laugh_intensity','natural') not in ('subtle','natural','lively'):fail('Invalid laughter intensity.')
    if type(settings.get('crowd_work',True)) is not bool or type(settings.get('callback',True)) is not bool:
        fail('Invalid audience interaction settings.')
    photo_id=settings.get('asset_id')
    if photo_id:
        asset=f.db('comedy_assets',filters={'id':'eq.'+f.uid(photo_id),
          'owner_id':'eq.'+actor['id']},select='id',limit=1)
        if not asset:fail('Choose an uploaded asset belonging to your account.')
    target_id=str(b.get('station_id') or '').strip()
    destination={'mode':'private'} if not target_id else {'mode':'manual_stage_request','station_id':target_id}
    if target_id:
        eligible={v['id'] for v in eligible_station_list(f,actor)['stations']}
        if target_id not in eligible:fail('Station is not eligible for this account.',403)
        if any(seen[i]['rating']=='R' for i in ids):fail('R-rated routines require an independently protected adult station.',403)
    manifest={'version':'comedy-production-v1','stage':'planned_only','created_for':actor['id'],
        'studio_settings':{'audience_size':capacity,
            'room_tone':settings.get('room_tone','intimate'),
            'laugh_intensity':settings.get('laugh_intensity','natural'),
            'crowd_work':settings.get('crowd_work',True),
            'callback':settings.get('callback',True),'asset_id':photo_id},
        'destination':destination,
        'routine_order':[{'id':i,'title':seen[i]['title'],'rating':seen[i]['rating'],
            'comedian_id':seen[i]['comedian_id'],'target_duration_seconds':180} for i in ids],
        'intro_seconds':5,'ambient_room':'configured_in_studio',
        'stems':['comedian','audience_reply','laughter','room_tone','liner'],
        'callback_required':True,'audio_rendered':False,
        'external_provider_dispatch':False,'maestro_published':False,
        'cost_cap_cents':0}
    prior=f.db('comedy_batch_plans',filters={'owner_id':'eq.'+actor['id'],
        'request_id':'eq.'+request_id},select='id,request_id,routine_ids,status',limit=1)
    if prior:
        if prior[0]['routine_ids']!=ids:fail('A previous batch used this request ID for different routines.',409)
        return {'ok':True,'batch':prior[0],'replayed':True}
    try:
        saved=f.db('comedy_batch_plans','POST',{'owner_id':actor['id'],
            'request_id':request_id,'routine_ids':ids,'prompt_manifest':manifest,
            'status':'planned','external_spend_authorized':False,'provider_spend_cap_cents':0},
            select='id,request_id,routine_ids,status,created_at')
        return {'ok':True,'batch':saved[0],'replayed':False}
    except Exception:
        recovered=f.db('comedy_batch_plans',filters={'owner_id':'eq.'+actor['id'],
            'request_id':'eq.'+request_id},select='id,request_id,routine_ids,status',limit=1)
        if recovered and recovered[0]['routine_ids']==ids:return {'ok':True,'batch':recovered[0],'replayed':True}
        fail('Batch creation outcome uncertain; check saved batches before retrying.',409)

def eligible_station_list(f,actor):
    from station_libraries import allowed,entitlement,settings
    all_stations=f.db('stations',filters={} if actor['admin'] else {'owner_id':'eq.'+actor['id']},
        select='id,owner_id,name,status,visibility,azuracast_station_id',limit=100)
    allowed_stations=[]
    for st in all_stations:
        if not st.get('azuracast_station_id') or st.get('status')!='live':continue
        try:allowed(f,actor,st,'upload')
        except Exception:continue
        allowed_stations.append({'id':st['id'],'name':st['name'],
            'max_rating':'PG-13','adult_content_enabled':False,
            'may_request_staging':True,
            'note':'Verified stage eligibility only. Does not schedule broadcast.'})
    return {'stations':allowed_stations,'verified':True,'adult_stations_disabled':True}

def handle(handler,method,f):
    path=urlsplit(handler.path).path
    try:
        if path=='/comedy/public':
            if method!='GET':return handler.respond(405,{'error':'Use GET.'})
            return handler.respond(200,published(f))
        if path.startswith('/comedy/media/'):
            if method!='GET':return handler.respond(405,{'error':'Use GET.'})
            identifier=path.rsplit('/',1)[-1]
            try:identifier=f.uid(identifier)
            except Exception:fail('Invalid routine ID.',404)
            rows=f.db('comedy_routines',filters={'id':'eq.'+identifier,
                'state':'eq.published','rights_confirmed':'is.true',
                'rating':'in.(PG,PG-13)','audio_b2_key':'not.is.null'},
                select='id,audio_b2_key',limit=1)
            if not rows:fail('Approved audio is not available.',404)
            key=rows[0]['audio_b2_key']
            if not key.startswith('comedy/approved/'):fail('Audio path is not approved.',403)
            url=f.signed(key)
            handler.send_response(302)
            handler.send_header('Location',url)
            handler.send_header('Cache-Control','no-store')
            handler.send_header('Content-Length','0')
            handler.end_headers()
            return
        actor=auth(f,handler)
        if path.startswith('/comedy/live-take/') and method=='GET':
            return handler.respond(200,live_take_review(f,actor,path.rsplit('/',1)[-1]))
        if path.startswith('/comedy/review/') and method=='GET':
            return handler.respond(200,review_audio(f,actor,path.rsplit('/',1)[-1]))
        if path=='/comedy/assets' and method=='POST':
            return handler.respond(201,create_image(f,actor,handler))
        if path.startswith('/comedy/assets/') and method=='GET':
            url=asset_url(f,actor,path.rsplit('/',1)[-1])
            handler.send_response(302)
            handler.send_header('Location',url)
            handler.send_header('Cache-Control','no-store')
            handler.send_header('Content-Length','0')
            handler.end_headers()
            return
        if path=='/comedy/private' and method=='GET':
            return handler.respond(200,list_private(f,actor))
        if path=='/comedy/stations' and method=='GET':
            return handler.respond(200,eligible_station_list(f,actor))
        if path=='/comedy/drafts':
            body=receive(handler)
            if body.get('action')!='create':fail('Unsupported action.')
            return handler.respond(201,create_draft(f,actor,body))
        if path=='/comedy/batches/plan':
            body=receive(handler)
            return handler.respond(201,plan_batch(f,actor,body))
        return handler.respond(404,{'error':'Not found.'})
    except AccessError as e:return handler.respond(e.status,{'error':str(e)})
    except Exception:return handler.respond(500,{'error':'Comedy service unavailable; no changes were made.'})
