"""Native Maestro Comedy Club adapter. Reuses existing factory identity, DB and B2.
Public reads are conservative: no sample records; no adult audio without age gate.
Private editing is admin-only pending audited customer entitlements.
"""
import json
import re
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
        if path=='/comedy/drafts':
            body=receive(handler)
            if body.get('action')!='create':fail('Unsupported action.')
            return handler.respond(201,create_draft(f,actor,body))
        return handler.respond(404,{'error':'Not found.'})
    except AccessError as e:return handler.respond(e.status,{'error':str(e)})
    except Exception:return handler.respond(500,{'error':'Comedy service unavailable; no changes were made.'})
