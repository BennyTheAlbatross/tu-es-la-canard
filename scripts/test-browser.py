import json,time,os,ipaddress
from urllib.parse import urlparse
from pathlib import Path
from playwright.sync_api import sync_playwright
out=Path(os.environ.get('CANARD_EVIDENCE','build/browser-evidence'));out.mkdir(parents=True,exist_ok=True)
probe_code='''import asyncio,json,platform
_canard_frames=[]
for _task in asyncio.all_tasks():
    _coro=_task.get_coro()
    while _coro is not None:
        _frame=getattr(_coro,'cr_frame',None)
        if _frame is not None:
            _locals=_frame.f_locals
            _item={'function':_frame.f_code.co_name}
            if 'title' in _locals: _item['title']=_locals['title']
            if 'selected' in _locals: _item['selected']=_locals['selected']
            if 'options' in _locals: _item['options']=_locals['options']
            if 'player' in _locals: _item.update(position=list(_locals['player'].position),torch=_locals['player'].torch_active)
            if 'position' in _locals: _item.update(position=_locals['position'],direction=_locals.get('direction'),torch=_locals.get('torch_active'))
            if 'clock' in _locals: _item['fps']=_locals['clock'].get_fps()
            if 'map_file' in _locals: _item['map']=str(_locals['map_file'])
            if 'map_path' in _locals: _item['map']=str(_locals['map_path'])
            if 'wall_style' in _locals: _item['wall_style']=_locals['wall_style']
            _canard_frames.append(_item)
        _coro=getattr(_coro,'cr_await',None)
platform.window.canardProbe=json.dumps(_canard_frames)
'''
with sync_playwright() as p:
 public_ip=os.environ.get('CANARD_PUBLIC_IP')
 if public_ip:ipaddress.ip_address(public_ip)
 cases=[('chromium',False),('firefox',False),('chromium',True)] if not public_ip else [('chromium',False),('chromium',True)]
 for browser_name,mobile in cases:
  label=browser_name+('-mobile' if mobile else '')
  args=[]
  if public_ip:
   public_host=urlparse(os.environ['CANARD_URL']).hostname
   args=['--host-resolver-rules=MAP '+public_host+' '+public_ip]
  b=getattr(p,browser_name).launch(headless=True,args=args)
  context=b.new_context(viewport={'width':844 if mobile else 1280,'height':390 if mobile else 900},is_mobile=mobile if browser_name=='chromium' else False,has_touch=mobile)
  page=context.new_page();events=[];network=[]
  page.on('console',lambda m:events.append({'type':m.type,'text':m.text}))
  page.on('request',lambda r:network.append(r.url))
  page.on('pageerror',lambda e:events.append({'type':'pageerror','text':str(e)}))
  page.on('requestfailed',lambda r:events.append({'type':'requestfailed','text':r.url+' '+str(r.failure)}))
  started=time.monotonic();response=page.goto(os.environ.get('CANARD_URL','http://127.0.0.1:18000'),wait_until='domcontentloaded')
  endpoint=response.server_addr()
  if public_ip:assert endpoint['ipAddress']==public_ip,endpoint
  print(label,'HTTPS endpoint',endpoint,flush=True)
  page.locator('#game-tab').click()
  f=page.locator('#game').element_handle().content_frame();f.wait_for_url('**/game/index.html')
  f.wait_for_function('document.querySelector("#canvas").width > 1 || document.querySelector("#infobox").innerText.includes("Ready to start")',timeout=90000)
  if f.locator('#canvas').evaluate('(c)=>c.width') == 1:f.locator('#canvas').click(force=True)
  f.wait_for_function('document.querySelector("#canvas").width > 1',timeout=15000)
  f.locator('#canvas').click();page.wait_for_timeout(1200)
  def probe():
   f.evaluate('window.canardProbe=null')
   f.evaluate('(code)=>python.PyRun_SimpleString(code)',probe_code)
   f.wait_for_function('window.canardProbe !== null',timeout=5000)
   return json.loads(f.evaluate('window.canardProbe'))
  def menu():return next((x for x in probe() if x['function']=='choose_menu'),{})
  def key(k):
   if mobile:
    button=page.locator('[data-key="'+k+'"]');button.scroll_into_view_if_needed();box=button.bounding_box();page.touchscreen.tap(box['x']+box['width']/2,box['y']+box['height']/2)
   else:page.keyboard.press({'enter':'Enter','up':'ArrowUp','down':'ArrowDown','escape':'Escape','torch':'Space','music':'m','walls':'v'}.get(k,k))
   page.wait_for_timeout(350)
  load_seconds=time.monotonic()-started
  transfers=page.evaluate('performance.getEntriesByType("resource").map(x=>({url:x.name,encoded:x.encodedBodySize,transfer:x.transferSize}))')+f.evaluate('performance.getEntriesByType("resource").map(x=>({url:x.name,encoded:x.encodedBodySize,transfer:x.transferSize}))')
  print(label,'cold load seconds',round(load_seconds,2),'encoded bytes',sum(x['encoded'] for x in transfers),flush=True)
  print(label,'initial',menu(),flush=True)
  key('enter');print(label,'levels',menu(),flush=True)
  for _ in range(4):key('down')
  key('enter');print(label,'modes',menu(),flush=True)
  assert ('Ray-cast dungeon' in menu()['options']) != mobile
  key('enter');page.wait_for_timeout(1500)
  state=next(x for x in probe() if x['function']=='main_async' and 'position' in x)
  print(label,'2d before',state,flush=True)
  if mobile:
   button=page.locator('[data-key="right"]');button.scroll_into_view_if_needed();box=button.bounding_box();page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.wait_for_timeout(250);page.mouse.up()
  else:
   page.keyboard.down('ArrowRight');page.wait_for_timeout(250);page.keyboard.up('ArrowRight')
  after=next(x for x in probe() if x['function']=='main_async' and 'position' in x)
  assert after['position']!=state['position'],(label,'movement did not change position')
  key('torch');after=next(x for x in probe() if x['function']=='main_async' and 'position' in x);assert after['torch'] is True
  assert after['wall_style']=='pseudo3d',after
  page.screenshot(path=str(out/(label+'-2d-pseudo3d.png')),full_page=not mobile)
  key('walls');classic=next(x for x in probe() if x['function']=='main_async' and 'position' in x);assert classic['wall_style']=='classic',classic
  page.screenshot(path=str(out/(label+'-2d-classic.png')),full_page=not mobile)
  print(label,'2d after',after,flush=True)
  key('escape');print(label,'returned',menu(),flush=True)
  if not mobile:
   key('down');key('enter');page.wait_for_timeout(1800)
   state=next(x for x in probe() if x['function']=='main_async' and 'direction' in x)
   page.keyboard.down('ArrowRight');page.wait_for_timeout(250);page.keyboard.up('ArrowRight')
   after=next(x for x in probe() if x['function']=='main_async' and 'direction' in x)
   assert after['direction']!=state['direction']
   f.locator('#canvas').click()
   before_mouse=next(x for x in probe() if x['function']=='main_async' and 'direction' in x)
   # Headless pointer-lock warping creates cancelling native movements.
   # Send a deterministic DOM relative-motion event through the SDL listener.
   f.locator('#canvas').dispatch_event('mousemove',{'movementX':120,'movementY':0,'bubbles':True});page.wait_for_timeout(300)
   mouse_state=next(x for x in probe() if x['function']=='main_async' and 'direction' in x)
   assert mouse_state['direction']!=before_mouse['direction'],(label,'mouse turning did not work')
   print(label,'DOM mouse motion turning verified',flush=True)
   page.screenshot(path=str(out/(label+'-raycast.png')),full_page=True)
   print(label,'raycast',after,flush=True)
   key('escape');assert menu().get('title')=='Choose a mode'
  level_probe="""import json,platform
from pathlib import Path
from tuer_le_canard.game_data import load_level
levels=sorted(Path('maps/game').glob('*.csv'))
for path in levels: load_level(path,Path('rules/objects.csv'))
platform.window.canardLevels=json.dumps([str(path) for path in levels])
"""
  f.evaluate('(code)=>python.PyRun_SimpleString(code)',level_probe)
  f.wait_for_function('window.canardLevels !== undefined')
  loaded_levels=json.loads(f.evaluate('window.canardLevels'));assert len(loaded_levels)==6
  print(label,'browser-loaded levels',loaded_levels,flush=True)
  audio=f.evaluate('Object.keys(MM).filter(k=>/^\\d+$/.test(k)).map(k=>({id:k,time:MM[k].media?.currentTime,paused:MM[k].media?.paused,error:MM[k].media?.error?.code}))')
  print(label,'audio',audio,flush=True)
  (out/(label+'-verification.json')).write_text(json.dumps({'endpoint':endpoint,'loaded_levels':loaded_levels,'load_seconds':load_seconds,'transfers':transfers,'audio':audio,'events':events,'network':network},indent=2))
  print(label,'errors',[e for e in events if e['type'] in ('error','pageerror','requestfailed')],flush=True)
  b.close()
