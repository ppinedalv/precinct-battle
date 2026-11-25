#!/usr/bin/env python3
"""Builds the iPhone version of Precinct Battle: mobile/index.html, generated from the desktop index.html.

Run after every desktop change:  python3 tools/build_mobile.py
Then push; the phone picks up the new build the next time the app opens online.

Phone version = 1 player VS COMPUTER only, landscape, touch controls:
  left thumb  = movement stick (push past the ring to run / turbo boost)
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
#minimap{left:calc(8px + env(safe-area-inset-left));top:8px;width:78px;height:122px}
#lowleft{left:calc(94px + env(safe-area-inset-left));top:8px;bottom:auto;transform:scale(.62);transform-origin:top left}
#hq{top:6px;transform:translateX(-50%) scale(.72);transform-origin:top center;gap:24px}
#counters{top:6px;right:calc(98px + env(safe-area-inset-right));transform:scale(.6);transform-origin:top right}
.vbar{bottom:auto;top:160px;height:70px;width:7px}
#hull{left:calc(12px + env(safe-area-inset-left))}#heat{left:calc(40px + env(safe-area-inset-left));right:auto}   /* heat sits right next to hull (user 2026-11-25) */
.vlbl{bottom:auto;top:146px;font-size:8px}
.vlbl[style*="left"]{left:calc(4px + env(safe-area-inset-left))!important}.vlbl[style*="right"]{right:auto!important;left:calc(32px + env(safe-area-inset-left))!important}
#feed{top:54px;font-size:12px}
#respawn{font-size:20px}#repairMsg{font-size:16px}
#cross{width:52px;height:52px;margin:-26px 0 0 -26px}
.overlay{padding:12px calc(16px + env(safe-area-inset-right)) 70px calc(16px + env(safe-area-inset-left))}
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
#touch .tb.on{background:radial-gradient(circle,rgba(255,215,90,.75),rgba(180,120,0,.6));border-color:#ffd75a}
#touch .tb span{position:absolute;top:100%;left:50%;transform:translateX(-50%);margin-top:1px;white-space:nowrap;
  font:700 9px ui-monospace,Menlo,monospace;letter-spacing:.06em;color:#e6eefa;text-shadow:0 1px 2px #000,0 0 4px #000}
#touch .tb b{position:absolute;top:-4px;right:-4px;min-width:17px;height:17px;border-radius:9px;background:#7a4dff;font:700 10px/17px ui-monospace,Menlo,monospace;text-align:center}
/* layout after the user's reference (2026-11-25): big main GUN in the corner, the other weapons in an arc around it, utility buttons in a row along the bottom */
#tGun{width:96px;height:96px;right:calc(130px + env(safe-area-inset-right));bottom:22px;font-size:38px;border:3px solid rgba(255,210,90,.85)}
#tCan{width:62px;height:62px;right:calc(263px + env(safe-area-inset-right));bottom:39px;border-color:rgba(255,150,80,.8)}
#tMode{width:56px;height:56px;right:calc(180px + env(safe-area-inset-right));bottom:154px;border-color:rgba(47,208,255,.85)}
#tMis{width:62px;height:62px;right:calc(236px + env(safe-area-inset-right));bottom:114px;border-color:rgba(255,90,90,.8)}
#tJump{width:54px;height:54px;right:calc(6px + env(safe-area-inset-right));bottom:16px;border-color:rgba(93,255,160,.8)}
#tEmp{width:46px;height:46px;right:calc(4px + env(safe-area-inset-right));top:56px;font-size:20px;border-color:rgba(160,120,255,.85)}
#tRun{width:50px;height:50px;right:calc(70px + env(safe-area-inset-right));bottom:45px;border-color:rgba(255,176,46,.85)}
#tMute{width:38px;height:38px;right:calc(52px + env(safe-area-inset-right));top:8px;border-radius:8px;font-size:17px}
#tPause{width:38px;height:38px;right:calc(8px + env(safe-area-inset-right));top:8px;border-radius:8px;font:800 13px ui-monospace,Menlo,monospace}
/* joystick: always visible at its home spot; it jumps under your thumb anywhere on the left side and returns home on release */
#tStick,#tKnob{position:absolute;border-radius:50%;pointer-events:none;left:calc(118px + env(safe-area-inset-left));top:calc(100% - 104px)}
#tStick{width:132px;height:132px;margin:-66px 0 0 -66px;border:2px solid rgba(220,232,250,.45);background:radial-gradient(circle,rgba(20,28,44,.15),rgba(60,90,140,.35))}
#tStick::before{content:"";position:absolute;inset:0;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><g fill='rgba(220,232,250,.55)'><path d='M50 5l6 8H44z'/><path d='M50 95l6-8H44z'/><path d='M5 50l8-6v12z'/><path d='M95 50l-8-6v12z'/></g></svg>") center/100% 100% no-repeat}
#tStick.boost{border-color:#ffb02e;box-shadow:0 0 14px rgba(255,170,40,.7)}
#tKnob{width:56px;height:56px;margin:-28px 0 0 -28px;background:radial-gradient(circle at 50% 35%,rgba(140,200,255,.8),rgba(40,90,160,.75));border:2px solid rgba(255,255,255,.75)}
#rotate{position:fixed;inset:0;z-index:20;background:#000;display:none;flex-direction:column;align-items:center;justify-content:center;gap:18px;
  font:700 16px system-ui;letter-spacing:.12em;color:#f2b51d;text-align:center;padding:24px}
#rotate img{width:120px;height:120px;border-radius:26px}
@media (orientation:portrait){#rotate{display:flex}}
'''

TOUCH_HTML = '''<div id="touch">
  <div id="tStick"></div><div id="tKnob"></div>
  <div class="tb" id="tGun" data-key="KeyJ">✸<span>GUN</span></div>
  <div class="tb" id="tCan" data-key="KeyK">◉<span>CANNON</span></div>
  <div class="tb" id="tMis" data-key="KeyL">➶<span>MISSILE</span></div>
  <div class="tb" id="tMode" data-key="KeyF" data-tap="1">⇅<span>HOVER</span></div>
  <div class="tb" id="tJump" data-key="Space" data-tap="1">⤒<span>JUMP</span></div>
  <div class="tb" id="tEmp" data-key="KeyH" data-tap="1">ϟ<span>EMP</span><b>5</b></div>
  <div class="tb" id="tRun" data-key="ShiftLeft">»<span>RUN</span></div>
  <div class="tb" id="tMute" data-key="KeyM" data-tap="1">🔊</div>
  <div class="tb" id="tPause" data-key="KeyP" data-tap="1">II</div>
</div>
<div id="rotate"><img src="icons/icon-180.png" alt=""><div>TURN YOUR PHONE SIDEWAYS</div></div>
'''

HELP = '''<div class="keys" style="margin-top:14px">
      <b>Left thumb</b><span>Drag anywhere on the left side to move. Push past the ring to run (Walker) or turbo boost (Hover)</span>
      <b>Right thumb</b><span>Drag anywhere on the right side to aim the crosshairs (you can also drag while holding a weapon button)</span>
      <b>GUN</b><span>Rotary gun (hold; watch the heat)</span>
      <b>CANNON</b><span>Cannon (hold)</span>
      <b>MISSILE</b><span>Homing missile</span>
      <b>JUMP</b><span>Jump (Walker mode only): just high enough to reach the nearest rooftop</span>
      <b>HOVER / WALK</b><span>Transform: Walker (armored) / Hover (fast)</span>
      <b>EMP</b><span>EMP shockwave: freezes nearby enemy tanks, rollers and hover robots and shields you for 7 s (5 per game)</span>
      <b></b><span>Yellow diamond = target locked; all weapons auto-aim at it</span>
      <b>RUN / BOOST</b><span>Hold: run in Walker, turbo boost in Hover (uses System Energy). Pushing the stick past its ring does the same</span>
      <b>🔊</b><span>Mute / unmute all sound</span>
      <b>II</b><span>Pause. The pause screen has music on/off, music volume and load your own track</span>
    </div>
    <div id="credits">'''

TOUCH_JS = r'''
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
  const m=Math.min(d,R)/R;TOUCH.boost=d>BOOST_R;stick.classList.toggle('boost',TOUCH.boost);
  if(m<DEAD){TOUCH.mx=TOUCH.my=0;return;}
  TOUCH.mx=dx/d*m;TOUCH.my=-dy/d*m;}
T.addEventListener('touchstart',e=>{e.preventDefault();
  for(const t of e.changedTouches){
    const b=t.target.closest&&t.target.closest('.tb');
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
    if(isPlaying()&&player.alive){yaw-=dx*AIM_X;pitch=clamp(pitch+dy*AIM_Y,-.7118,.65);}}
},{passive:false});
function end(e){e.preventDefault();
  for(const t of e.changedTouches){const o=own.get(t.identifier);if(!o)continue;own.delete(t.identifier);
    if(o.kind==='stick')setStick(null);
    if(o.kind==='btn'){o.el.classList.remove('on');if(!o.el.dataset.tap)press(o.el.dataset.key,false);}}}
T.addEventListener('touchend',end,{passive:false});T.addEventListener('touchcancel',end,{passive:false});
function releaseAll(){for(const o of own.values())if(o.kind==='btn'){o.el.classList.remove('on');if(!o.el.dataset.tap)press(o.el.dataset.key,false);}own.clear();setStick(null);}
// show the controls only while a match is running; keep button labels in sync with the game state
let lastShow=null;
setInterval(()=>{document.body.classList.toggle('pz',started&&paused&&!over);const show=started&&!over;if(show!==lastShow){T.style.display=show?'block':'none';lastShow=show;if(!show)releaseAll();}
  if(!show)return;if(paused&&own.size)releaseAll();
  $('tMode').querySelector('span').textContent=player.modeTarget?'WALK':'HOVER';$('tRun').querySelector('span').textContent=player.mode>.5?'BOOST':'RUN';$('tMute').textContent=muted?'🔇':'🔊';
  $('tJump').style.opacity=player.mode<.5&&!player.modeTarget?1:.35;
  const em=$('emp').textContent.match(/\d+/),eb=$('tEmp').querySelector('b');eb.textContent=em?em[0]:'0';$('tEmp').style.opacity=em&&!/\ds$/.test($('emp').textContent.trim())?1:.45;},120);
// leaving the app (home button, call, lock screen) pauses the match
document.addEventListener('visibilitychange',()=>{if(document.hidden){releaseAll();if(isPlaying())press('KeyP',true);}});
document.addEventListener('gesturestart',e=>e.preventDefault());
window.__pb={get player(){return player},get yaw(){return yaw},get pitch(){return pitch},get keys(){return keys},get started(){return started},get over(){return over},hit:a=>damage(player,a,RED,false,true),get paused(){return paused}};   // read-only test hook
if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{});
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
sub('const keys={};let mouseL', 'const keys={},TOUCH={mx:0,my:0,boost:false};let mouseL')
sub("_m.set(0,0,0).addScaledVector(f,(keys.KeyW?1:0)-(keys.KeyS?1:0)).addScaledVector(r,(keys.KeyD?1:0)-(keys.KeyA?1:0));\n  if(_m.lengthSq()>0)_m.normalize();",
    "_m.set(0,0,0).addScaledVector(f,(keys.KeyW?1:0)-(keys.KeyS?1:0)+TOUCH.my).addScaledVector(r,(keys.KeyD?1:0)-(keys.KeyA?1:0)+TOUCH.mx);\n  if(_m.lengthSq()>1)_m.normalize();")
sub('const shift=keys.ShiftLeft||keys.ShiftRight;', 'const shift=keys.ShiftLeft||keys.ShiftRight||TOUCH.boost;')
# start / pause screens: touch instructions instead of keyboard keys
html, n = re.subn(r'<div class="keys" style="margin-top:22px">.*?</div>\s*<div id="credits">', lambda m: HELP, html, flags=re.S)
if n != 1: sys.exit('build_mobile: keyboard help block not found')
sub('<h2>PRESS P OR CLICK TO RESUME</h2>', '<h2>TAP RESUME TO KEEP FIGHTING</h2>')
# touch layer + rotate-your-phone screen, and the touch controller at the end of the game module
sub('<div id="netMsg"></div>', '<div id="netMsg"></div>\n' + TOUCH_HTML)
last = html.rindex('</script>')
html = html[:last] + TOUCH_JS + html[last:]

OUT.write_text(html)
# bump the offline cache version so phones fetch the new build
ver = hashlib.sha1(html.encode()).hexdigest()[:10]
sw = (ROOT / 'mobile' / 'sw.js')
sw.write_text(re.sub(r"const VERSION='[^']*';", f"const VERSION='{ver}';", sw.read_text()))
print(f'built {OUT.relative_to(ROOT)} ({len(html)//1024} KB), cache {ver}')
