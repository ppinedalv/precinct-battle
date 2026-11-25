#!/usr/bin/env python3
"""Builds the iPhone version of Precinct Battle: mobile/index.html, generated from the desktop index.html.

Run after every desktop change:  python3 tools/build_mobile.py
Then push; the phone picks up the new build the next time the app opens online.

Phone version = 1 player VS COMPUTER only, landscape, touch controls:
  left thumb  = movement stick (forward/back, side-step; run/boost only from the RUN button)
  right thumb = drag anywhere on the right half to aim the crosshairs
  buttons     = GUN, CANNON, MISSILE, JUMP, TRANSFORM (+ small EMP and pause)
Three.js is served from mobile/vendor so the game also runs offline (service worker in mobile/sw.js).
"""
import pathlib, re, sys, hashlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / 'index.html', ROOT / 'mobile' / 'index.html'
html = SRC.read_text()


def sub(old, new, count=1):
    """Replace an exact snippet; fail loudly if the desktop file changed so the snippet no longer matches."""
    global html
    n = html.count(old)
    if n != count:
        sys.exit(f'build_mobile: expected {count} match(es), found {n}, for:\n  {old[:120]}')
    html = html.replace(old, new)


HEAD = '''<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Precinct Battle">
<meta name="theme-color" content="#000000">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="icon" href="icons/icon-192.png">
<link rel="manifest" href="manifest.json">'''

CSS = '''
/* ---------------- iPhone build (tools/build_mobile.py) */
html,body{overscroll-behavior:none;-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent;touch-action:none}
.overlay{touch-action:pan-y}
#modeBox,#pvpBox,#guestBox,#musicHud,#mode,#emp{display:none!important}
.dhint{display:none}
/* landscape phone HUD: smaller, and moved off the thumb zones */
#minimap{left:calc(8px + env(safe-area-inset-left)*.4);top:10px;width:78px;height:122px}
#lowleft{left:calc(94px + env(safe-area-inset-left)*.4);top:8px;bottom:auto;transform:scale(.62);transform-origin:top left}
#hq{top:6px;transform:translateX(-50%) scale(.72);transform-origin:top center;gap:24px}
#counters{top:6px;right:114px;transform:scale(.6);transform-origin:top right}
.vbar{top:auto;bottom:40px;height:88px;width:7px}
#hull{left:calc(12px + env(safe-area-inset-left)*.4)}#heat{left:calc(40px + env(safe-area-inset-left)*.4);right:auto}   /* heat sits right next to hull (user 2026-11-25) */
.vlbl{top:auto;bottom:132px;font-size:8px}
.vlbl[style*="left"]{left:calc(4px + env(safe-area-inset-left)*.4)!important}.vlbl[style*="right"]{right:auto!important;left:calc(32px + env(safe-area-inset-left)*.4)!important}
#feed{top:54px;font-size:12px}
#respawn{font-size:20px}#repairMsg{font-size:16px}
#cross{width:52px;height:52px;margin:-26px 0 0 -26px}
.overlay{padding:12px calc(16px + env(safe-area-inset-right)) 70px calc(16px + env(safe-area-inset-left)*.4)}
.panel h1.logo img{max-width:min(360px,48vw)}
/* start screen: logo, difficulty and DEPLOY first so they fit without scrolling; story + controls below */
#start .panel{display:flex;flex-direction:column;align-items:center}
#start .panel>*{width:100%}#start .panel>.btn{width:auto;order:3;margin-bottom:12px}
#start h1.logo{order:0}#start .panel h2{order:1}#diffBox{order:2}#start .panel p{order:4}#start .keys{order:5}#credits{order:6}
body:not(.pz) #musicCtl{display:none!important}   /* music settings only on the pause screen */
.panel h2{margin:2px 0 8px;font-size:12px}.panel p{font-size:13px;margin-bottom:10px;line-height:1.4}
#diffBox{padding:8px 12px;margin-bottom:10px}#dVal{font-size:34px}#diffBox .dbtn{width:46px;height:46px}
#musicCtl{bottom:8px;padding:6px 10px;font-size:11px}
.keys{font-size:12px;gap:4px 12px;margin-bottom:12px}
/* touch controls */
#touch{position:fixed;inset:0;z-index:3;display:none;touch-action:none}
#touch .tb{position:absolute;border-radius:50%;display:flex;align-items:center;justify-content:center;
  font:400 24px/1 system-ui;color:#fff;background:radial-gradient(circle at 50% 35%,rgba(70,90,130,.55),rgba(14,20,34,.6));
  border:2px solid rgba(220,232,250,.55);box-shadow:0 0 10px rgba(0,0,0,.5),inset 0 0 10px rgba(120,170,255,.25);text-shadow:0 1px 3px #000}
#tGun.on,#tCan.on,#tMis.on{box-shadow:0 0 18px 4px rgba(255,200,60,.85)}
#touch .tb.on{background:radial-gradient(circle,rgba(255,215,90,.75),rgba(180,120,0,.6));border-color:#ffd75a}
#touch .tb span{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:1px;white-space:nowrap;
  font:700 9px ui-monospace,Menlo,monospace;letter-spacing:.06em;color:#e6eefa;text-shadow:0 1px 2px #000,0 0 4px #000}
#touch .tb b{position:absolute;top:-4px;right:-4px;min-width:17px;height:17px;border-radius:9px;background:#7a4dff;font:700 10px/17px ui-monospace,Menlo,monospace;text-align:center}
/* layout after the user's reference (2026-11-25): big main GUN in the corner, the other weapons in an arc around it, utility buttons in a row along the bottom */
#tGun{width:58px;height:58px;right:202px;bottom:31px;font-size:26px;border:3px solid rgba(255,210,90,.85)}
#tCan{width:58px;height:58px;right:186px;bottom:112px;border-color:rgba(255,150,80,.8)}
#tMode{width:58px;height:58px;right:36px;bottom:112px;border-color:rgba(47,208,255,.85)}
#tMis{width:58px;height:58px;right:111px;bottom:149px;border-color:rgba(255,90,90,.8)}
#tAim{width:96px;height:96px;right:92px;bottom:36px;font-size:40px;border:3px solid rgba(93,255,160,.8)}
#tAim i{position:absolute;width:40px;height:40px;border-radius:50%;background:radial-gradient(circle at 50% 35%,rgba(140,255,190,.7),rgba(30,120,70,.7));border:2px solid rgba(255,255,255,.7);pointer-events:none;font-style:normal;transition:transform .05s}
#tEmp{width:46px;height:46px;right:27px;bottom:196px;font-size:20px;border-color:rgba(160,120,255,.85)}
#tRun{width:58px;height:58px;right:20px;bottom:31px;border-color:rgba(255,176,46,.85)}
#tMute{width:38px;height:38px;right:68px;top:8px;border-radius:8px;font-size:17px}
#tPause{width:38px;height:38px;right:24px;top:8px;border-radius:8px;font:800 13px ui-monospace,Menlo,monospace}
/* joystick: always visible at its home spot; it jumps under your thumb anywhere on the left side and returns home on release */
#tStick,#tKnob{position:absolute;border-radius:50%;pointer-events:none;left:calc(148px + env(safe-area-inset-left)*.4);top:calc(100% - 104px)}
#tStick{width:132px;height:132px;margin:-66px 0 0 -66px;border:2px solid rgba(220,232,250,.45);background:radial-gradient(circle,rgba(20,28,44,.15),rgba(60,90,140,.35))}
#tStick::before{content:"";position:absolute;inset:0;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><g fill='rgba(220,232,250,.55)'><path d='M50 5l6 8H44z'/><path d='M50 95l6-8H44z'/><path d='M5 50l8-6v12z'/><path d='M95 50l-8-6v12z'/></g></svg>") center/100% 100% no-repeat}
#tStick.boost{border-color:#ffb02e;box-shadow:0 0 14px rgba(255,170,40,.7)}
#tKnob{width:56px;height:56px;margin:-28px 0 0 -28px;background:radial-gradient(circle at 50% 35%,rgba(140,200,255,.8),rgba(40,90,160,.75));border:2px solid rgba(255,255,255,.75)}
#buildTag{position:fixed;left:calc(8px + env(safe-area-inset-left)*.4);bottom:3px;z-index:6;font:600 9px ui-monospace,Menlo,monospace;color:#8a94a6;pointer-events:none}
body.playing #buildTag{display:none}
#rotate{position:fixed;inset:0;z-index:20;background:#000;display:none;flex-direction:column;align-items:center;justify-content:center;gap:18px;
  font:700 16px system-ui;letter-spacing:.12em;color:#f2b51d;text-align:center;padding:24px}
#rotate img{width:120px;height:120px;border-radius:26px}
@media (orientation:portrait){#rotate{display:flex}}
'''

TOUCH_HTML = '''<div id="touch">
  <div id="tStick"></div><div id="tKnob"></div>
  <div class="tb" id="tGun" data-key="KeyJ" data-toggle="1">✸<span>GUN</span></div>
  <div class="tb" id="tCan" data-key="KeyK" data-toggle="1">◉<span>CANNON</span></div>
  <div class="tb" id="tMis" data-key="KeyL" data-toggle="1">➶<span>MISSILE</span></div>
  <div class="tb" id="tMode" data-key="KeyF" data-tap="1">⇅<span>HOVER</span></div>
  <div class="tb" id="tAim" data-aim="1"><i></i><span>AIM · TAP = JUMP</span></div>
  <div class="tb" id="tEmp" data-key="KeyH" data-tap="1">ϟ<span>EMP</span><b>5</b></div>
  <div class="tb" id="tRun" data-key="ShiftLeft">»<span>RUN</span></div>
  <div class="tb" id="tMute" data-key="KeyM" data-tap="1">🔊</div>
  <div class="tb" id="tPause" data-key="KeyP" data-tap="1">II</div>
</div>
<div id="buildTag">BUILD __BUILD__</div>
<div id="rotate"><img src="icons/icon-180.png" alt=""><div>TURN YOUR PHONE SIDEWAYS</div></div>
'''

HELP = '''<div class="keys" style="margin-top:14px">
      <b>Left thumb</b><span>Joystick: up / down = forward / back, left / right = side-step (Walker) or float sideways (Hover). The left stick never turns the view; the AIM joystick does.</span>
      <b>Right thumb</b><span>Drag the big AIM button (or anywhere empty on the right side) to aim. You can also drag while holding a weapon button</span>
      <b>GUN</b><span>Rotary gun: tap once to start firing (button stays lit), tap again to stop. Watch the heat</span>
      <b>CANNON</b><span>Cannon: tap once to keep firing (button stays lit), tap again to stop</span>
      <b>MISSILE</b><span>Homing missiles: tap once to keep firing (button stays lit), tap again to stop</span>
      <b>AIM</b><span>Big button is an aim joystick: hold it left / right to keep turning the mech (the view swings round), up / down to aim up / down. Tap it to JUMP (Walker mode only): just high enough to reach the nearest rooftop</span>
      <b>HOVER / WALK</b><span>Transform: Walker (armored) / Hover (fast)</span>
      <b>EMP</b><span>EMP shockwave: freezes nearby enemy tanks, rollers and hover robots and shields you for 7 s (5 per game)</span>
      <b></b><span>Yellow diamond = target locked; all weapons auto-aim at it</span>
      <b>RUN / BOOST</b><span>Hold: run in Walker, turbo boost in Hover (uses System Energy).</span>
      <b>🔊</b><span>Mute / unmute all sound</span>
      <b>II</b><span>Pause. The pause screen has music on/off, music volume and load your own track</span>
    </div>
    <div id="credits">'''

TOUCH_JS = r'''
// ---------------- headlight pool on the ground ahead of the player's mech (iPhone build)
const HEAD_POOL=new THREE.Mesh(new THREE.PlaneGeometry(19,30),new THREE.MeshBasicMaterial({map:GLOW,color:0xeaf4ff,transparent:true,opacity:.75,blending:THREE.AdditiveBlending,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2}));
HEAD_POOL.rotation.order='YXZ';HEAD_POOL.renderOrder=1;scene.add(HEAD_POOL);
function updateHeadPool(){const P=player;HEAD_POOL.visible=P.alive;if(!P.alive)return;
  HEAD_POOL.position.set(P.pos.x+Math.sin(yaw)*12,P.pos.y+.07,P.pos.z+Math.cos(yaw)*12);HEAD_POOL.rotation.set(-Math.PI/2,0,0);HEAD_POOL.rotation.y=yaw;
  HEAD_POOL.material.opacity=P.onGround?.75:.25;}
// ---------------- iPhone touch controls (tools/build_mobile.py)
{
const T=$('touch'),stick=$('tStick'),knob=$('tKnob');
const R=60,BOOST_R=88,DEAD=.14,AIM_X=.0058,AIM_Y=.0046;
const press=(code,down)=>dispatchEvent(new KeyboardEvent(down?'keydown':'keyup',{code}));
const own=new Map();   // touch id -> {kind:'stick'|'aim'|'btn', x, y, el}
const isPlaying=()=>started&&!paused&&!over;
function setStick(o){
  if(!o){TOUCH.mx=TOUCH.my=0;TOUCH.boost=false;stick.style.left=stick.style.top=knob.style.left=knob.style.top='';stick.classList.remove('boost');return;}
  let dx=o.cx-o.x,dy=o.cy-o.y;const d=Math.hypot(dx,dy),k=d>R?R/d:1;
  knob.style.left=(o.x+dx*k)+'px';knob.style.top=(o.y+dy*k)+'px';
  const m=Math.min(d,R)/R;
  if(m<DEAD){TOUCH.mx=TOUCH.my=0;return;}
  TOUCH.mx=dx/d*m;TOUCH.my=-dy/d*m;if(Math.abs(TOUCH.mx)<.2)TOUCH.mx=0;if(Math.abs(TOUCH.my)<.2)TOUCH.my=0;}   // per-axis dead zone: pushing straight ahead doesn't drift the turn
T.addEventListener('touchstart',e=>{e.preventDefault();
  for(const t of e.changedTouches){
    const b=t.target.closest&&t.target.closest('.tb');
    if(b&&b.dataset.aim){own.set(t.identifier,{kind:'aim',el:b,x:t.clientX,y:t.clientY,sx:t.clientX,sy:t.clientY,t0:performance.now(),far:0});b.classList.add('on');continue;}
    if(b&&b.dataset.toggle){const on=!b.classList.contains('on');b.classList.toggle('on',on);press(b.dataset.key,on);own.set(t.identifier,{kind:'btn',el:b,x:t.clientX,y:t.clientY});continue;}
    if(b){own.set(t.identifier,{kind:'btn',el:b,x:t.clientX,y:t.clientY});b.classList.add('on');
      if(b.dataset.tap){press(b.dataset.key,true);press(b.dataset.key,false);}else press(b.dataset.key,true);continue;}
    if(t.clientX<innerWidth*.45&&![...own.values()].some(o=>o.kind==='stick')){
      const o={kind:'stick',x:t.clientX,y:t.clientY,cx:t.clientX,cy:t.clientY};own.set(t.identifier,o);
      stick.style.left=o.x+'px';stick.style.top=o.y+'px';setStick(o);continue;}
    own.set(t.identifier,{kind:'aim',x:t.clientX,y:t.clientY});}
},{passive:false});
T.addEventListener('touchmove',e=>{e.preventDefault();
  for(const t of e.changedTouches){const o=own.get(t.identifier);if(!o)continue;
    if(o.kind==='stick'){o.cx=t.clientX;o.cy=t.clientY;setStick(o);continue;}
    if(o.kind==='btn'&&o.el.dataset.tap)continue;   // tap buttons don't aim
    const dx=t.clientX-o.x,dy=t.clientY-o.y;o.x=t.clientX;o.y=t.clientY;
    if(o.sx!==undefined){const ox=t.clientX-o.sx,oy=t.clientY-o.sy,d=Math.hypot(ox,oy),k=d>26?26/d:1;o.far=Math.max(o.far,d);o.el.firstChild.style.transform=`translate(${ox*k}px,${oy*k}px)`;
      const m=Math.min(d,34)/34,ax=d?ox/d*m:0,ay=d?oy/d*m:0;TOUCH.ax=Math.abs(ax)<.15?0:ax;TOUCH.ay=Math.abs(ay)<.25?0:ay;continue;}
    if(isPlaying()&&player.alive){yaw-=dx*AIM_X;pitch=clamp(pitch+dy*AIM_Y,-.7118,.65);}}
},{passive:false});
function end(e){e.preventDefault();
  for(const t of e.changedTouches){const o=own.get(t.identifier);if(!o)continue;own.delete(t.identifier);
    if(o.kind==='stick')setStick(null);
    if(o.kind==='btn'&&!o.el.dataset.toggle){o.el.classList.remove('on');if(!o.el.dataset.tap)press(o.el.dataset.key,false);}
    if(o.kind==='aim'&&o.el){o.el.classList.remove('on');o.el.firstChild.style.transform='';TOUCH.ax=TOUCH.ay=0;
      if(o.far<12&&performance.now()-o.t0<350){press('Space',true);press('Space',false);}}}}   // quick tap on AIM = jump
T.addEventListener('touchend',end,{passive:false});T.addEventListener('touchcancel',end,{passive:false});
function releaseAll(){for(const g of T.querySelectorAll('.tb[data-toggle].on')){g.classList.remove('on');press(g.dataset.key,false);}for(const o of own.values()){if(o.kind==='btn'&&!o.el.dataset.toggle){o.el.classList.remove('on');if(!o.el.dataset.tap)press(o.el.dataset.key,false);}if(o.kind==='aim'&&o.el){o.el.classList.remove('on');o.el.firstChild.style.transform='';}}own.clear();TOUCH.ax=TOUCH.ay=0;setStick(null);}
// show the controls only while a match is running; keep button labels in sync with the game state
let lastShow=null;
setInterval(()=>{document.body.classList.toggle('pz',started&&paused&&!over);document.body.classList.toggle('playing',started&&!paused&&!over);const show=started&&!over;if(show!==lastShow){T.style.display=show?'block':'none';lastShow=show;if(!show)releaseAll();}
  if(!show)return;if(paused&&own.size)releaseAll();
  $('tMode').querySelector('span').textContent=player.modeTarget?'WALK':'HOVER';$('tRun').querySelector('span').textContent=player.mode>.5?'BOOST':'RUN';$('tMute').textContent=muted?'🔇':'🔊';
  const em=$('emp').textContent.match(/\d+/),eb=$('tEmp').querySelector('b');eb.textContent=em?em[0]:'0';$('tEmp').style.opacity=em&&!/\ds$/.test($('emp').textContent.trim())?1:.45;},120);
// leaving the app (home button, call, lock screen) pauses the match
document.addEventListener('visibilitychange',()=>{if(document.hidden){releaseAll();if(isPlaying())press('KeyP',true);}});
document.addEventListener('gesturestart',e=>e.preventDefault());
window.__pb={get player(){return player},get yaw(){return yaw},get pitch(){return pitch},get keys(){return keys},get started(){return started},get over(){return over},hit:a=>damage(player,a,RED,false,true),get paused(){return paused},get scene(){return scene},get pool(){return HEAD_POOL}};   // read-only test hook
if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js',{updateViaCache:'none'}).then(r=>r.update()).catch(()=>{});
function checkUpdate(){if(started&&!over)return;fetch('version.txt?'+Date.now(),{cache:'no-store'}).then(x=>x.ok?x.text():'').then(v=>{v=v.trim();if(v&&v!=='__BUILD__'){const k='pbReload',t=+sessionStorage.getItem(k)||0;if(Date.now()-t>60000){sessionStorage.setItem(k,Date.now());location.reload();}}}).catch(()=>{});}
document.addEventListener('visibilitychange',()=>{if(!document.hidden)checkUpdate();});checkUpdate();
}
'''

# head: phone viewport, home-screen app tags, icon, manifest
sub('<meta name="viewport" content="width=device-width,initial-scale=1">', HEAD)
sub('</style>\n</head>', CSS + '</style>\n</head>')
# Three.js from local copies (offline play); no 2-player library
sub('<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>',
    '<script type="importmap">{"imports":{"three":"./vendor/three.module.js","three/addons/":"./vendor/addons/"}}</script>')
sub('<script src="https://cdn.jsdelivr.net/npm/peerjs@1.5.5/dist/peerjs.min.js"></script>\n', '')
# 1 player only: never act as a 2-player guest
sub("const JOIN_ID=new URLSearchParams(location.search).get('join');", 'const JOIN_ID=null;')
# no pointer lock on a phone (it would also auto-pause the match)
sub('function lockPointer(){', 'function lockPointer(){return;')
# iPhone Safari has no pointer-lock API: document.exitPointerLock is undefined there, and endGame() calls it,
# so the DEFEAT / VICTORY screen never appeared and the match kept running in slow motion (user 2026-11-25)
sub("const $=id=>document.getElementById(id);", "const $=id=>document.getElementById(id);\nif(!document.exitPointerLock)document.exitPointerLock=()=>{};")
# touch stick feeds movement (analog) and run/boost
sub('const keys={};let mouseL', 'const keys={},TOUCH={mx:0,my:0,ax:0,ay:0,boost:false};let mouseL')
sub("_m.set(0,0,0).addScaledVector(f,(keys.KeyW?1:0)-(keys.KeyS?1:0)).addScaledVector(r,(keys.KeyD?1:0)-(keys.KeyA?1:0));\n  if(_m.lengthSq()>0)_m.normalize();",
    "_m.set(0,0,0).addScaledVector(f,(keys.KeyW?1:0)-(keys.KeyS?1:0)+TOUCH.my).addScaledVector(r,(keys.KeyD?1:0)-(keys.KeyA?1:0)+TOUCH.mx);\n  if(_m.lengthSq()>1)_m.normalize();")
sub('yaw+=((keys.ArrowLeft?1:0)-(keys.ArrowRight?1:0))*2.3*dt;', 'yaw+=((keys.ArrowLeft?1:0)-(keys.ArrowRight?1:0))*2.3*dt-TOUCH.ax*2.8*dt;   /* only the AIM joystick turns the view */')
sub('pitch=clamp(pitch+((keys.ArrowDown?1:0)-(keys.ArrowUp?1:0))*1.1*dt,-.7118,.65);', 'pitch=clamp(pitch+((keys.ArrowDown?1:0)-(keys.ArrowUp?1:0))*1.1*dt+TOUCH.ay*1.2*dt,-.7118,.65);')
# headlights look ON from the player's chase camera (iPhone build only, user 2026-11-25): a soft beam shining forward-down from
# each front hover-pod lamp, bright at the lens and fading out, plus a bigger halo that peeks round the pod from behind
sub("const sl=new THREE.SpotLight(0xeaf4ff,90,40,.42,.55,1.3);sl.position.set(0,0,.7);sl.target.position.set(0,-1.6,9);pod.add(sl);pod.add(sl.target);}",
    "const sl=new THREE.SpotLight(0xeaf4ff,90,40,.42,.55,1.3);sl.position.set(0,0,.7);sl.target.position.set(0,-1.6,9);pod.add(sl);pod.add(sl.target);"
    "const bg=new THREE.CylinderGeometry(.3,3.4,17,24,1,true);bg.translate(0,-8.5,0);"
    "const bm=new THREE.ShaderMaterial({transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,side:THREE.DoubleSide,uniforms:{col:{value:new THREE.Color(0xeaf4ff)}},"
    "vertexShader:'varying float vH;void main(){vH=uv.y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',"
    "fragmentShader:'uniform vec3 col;varying float vH;void main(){gl_FragColor=vec4(col,.2*(.4+.6*vH));}'});"
    "const beam=new THREE.Mesh(bg,bm);beam.position.set(0,0,.72);beam.rotation.x=-Math.PI/2+.13;beam.renderOrder=2;pod.add(beam);"
    "glowAt(0xdfeeff,0,.05,1.15,2.6,pod);}")
# ...and a pool of headlight on the ground ahead of the player's mech, following it every frame
sub('updatePlayer(dt,gt);updateHoverHum();', 'updatePlayer(dt,gt);updateHeadPool();updateHoverHum();')
# start / pause screens: touch instructions instead of keyboard keys
html, n = re.subn(r'<div class="keys" style="margin-top:22px">.*?</div>\s*<div id="credits">', lambda m: HELP, html, flags=re.S)
if n != 1: sys.exit('build_mobile: keyboard help block not found')
sub('<h2>PRESS P OR CLICK TO RESUME</h2>', '<h2>TAP RESUME TO KEEP FIGHTING</h2>')
# touch layer + rotate-your-phone screen, and the touch controller at the end of the game module
sub('<div id="netMsg"></div>', '<div id="netMsg"></div>\n' + TOUCH_HTML)
last = html.rindex('</script>')
html = html[:last] + TOUCH_JS + html[last:]

import datetime
BUILD = datetime.datetime.now().strftime('%m%d-%H%M')
html = html.replace('__BUILD__', BUILD)
OUT.write_text(html)
(ROOT / 'mobile' / 'version.txt').write_text(BUILD + '\n')
# bump the offline cache version so phones fetch the new build
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
sw = (ROOT / 'mobile' / 'sw.js')
sw.write_text(re.sub(r"const VERSION='[^']*';", f"const VERSION='{ver}';", sw.read_text()))
print(f'built {OUT.relative_to(ROOT)} ({len(html)//1024} KB), cache {ver}')
