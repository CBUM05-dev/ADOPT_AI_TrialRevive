"""Pilule 3D (three.js, fonctionne hors ligne) : capsule bicolore brillante qui tourne, ombre portée, molécules en orbite.

La bibliothèque three.js est lue depuis static/three.min.js et injectée dans la page : aucun accès réseau nécessaire.
"""
from pathlib import Path

import streamlit.components.v1 as components

THREE_JS = Path(__file__).resolve().parent.parent / "static" / "three.min.js"

PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<style>
  html,body{margin:0;height:100%;background:transparent;overflow:hidden}
  #c{width:100%;height:100%;display:block}
</style></head><body><canvas id="c"></canvas>
<script>__THREE__</script>
<script>
(function(){
  var canvas = document.getElementById('c');
  var W = canvas.clientWidth || 520, H = canvas.clientHeight || 360;
  var renderer = new THREE.WebGLRenderer({canvas: canvas, antialias: true, alpha: true});
  renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
  renderer.setSize(W, H, false);
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  var scene = new THREE.Scene();
  var camera = new THREE.PerspectiveCamera(32, W / H, 0.1, 100);
  // recule la caméra si la zone est étroite : rien n'est coupé sur les bords
  var back = Math.max(1, 1.5 / (W / H));
  camera.position.set(0, 3.2 * back, 9.2 * back);
  camera.lookAt(0, 0.2, 0);

  // lumières : clé chaude, contre-jour turquoise, remplissage doux
  scene.add(new THREE.HemisphereLight(0xffffff, 0x9fd8d4, 0.75));
  var key = new THREE.DirectionalLight(0xffffff, 1.1);
  key.position.set(-4, 8, 5); key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024); key.shadow.radius = 6;
  key.shadow.camera.left = -6; key.shadow.camera.right = 6; key.shadow.camera.top = 6; key.shadow.camera.bottom = -6;
  scene.add(key);
  var rim = new THREE.PointLight(0x14b8a6, 1.2, 30); rim.position.set(5, 2, -3); scene.add(rim);
  var fill = new THREE.PointLight(0xffffff, 0.6, 30); fill.position.set(4, 1, 6); scene.add(fill);

  // sol qui ne montre que l'ombre
  var ground = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({opacity: 0.28}));
  ground.rotation.x = -Math.PI / 2; ground.position.y = -1.9; ground.receiveShadow = true; scene.add(ground);

  function glossy(color){
    return new THREE.MeshPhysicalMaterial({color: color, roughness: 0.22, metalness: 0.0, clearcoat: 1.0, clearcoatRoughness: 0.08});
  }
  function capsule(r, len, colA, colB){
    var g = new THREE.Group();
    var matA = glossy(colA), matB = glossy(colB);
    var half = len / 2;
    var cylA = new THREE.Mesh(new THREE.CylinderGeometry(r, r, half, 48, 1, true), matA); cylA.position.y = half / 2;
    var cylB = new THREE.Mesh(new THREE.CylinderGeometry(r, r, half, 48, 1, true), matB); cylB.position.y = -half / 2;
    var capA = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 24, 0, Math.PI * 2, 0, Math.PI / 2), matA); capA.position.y = half;
    var capB = new THREE.Mesh(new THREE.SphereGeometry(r, 48, 24, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), matB); capB.position.y = -half;
    [cylA, cylB, capA, capB].forEach(function(m){ m.castShadow = true; g.add(m); });
    var ring = new THREE.Mesh(new THREE.TorusGeometry(r * 1.002, r * 0.035, 16, 64), new THREE.MeshStandardMaterial({color: 0xdfeeee, roughness: 0.4}));
    ring.rotation.x = Math.PI / 2; g.add(ring);
    return g;
  }

  var pill = capsule(0.95, 2.2, 0x0f9d8f, 0xf8fbfb);
  pill.rotation.z = Math.PI / 4.2;
  var holder = new THREE.Group(); holder.add(pill); scene.add(holder);

  // petites molécules / pilules en orbite
  var minis = [], palette = [0x14b8a6, 0x0b3b5b, 0xf59e0b, 0xffffff, 0x38bdf8];
  for (var i = 0; i < 7; i++){
    var m;
    if (i % 2 === 0){ m = new THREE.Mesh(new THREE.SphereGeometry(0.2 + Math.random() * 0.14, 32, 24), glossy(palette[i % palette.length])); }
    else { m = capsule(0.17, 0.42, palette[(i + 1) % palette.length], 0xffffff); }
    m.castShadow = true;
    m.userData = {a: Math.random() * 6.28, r: 1.9 + Math.random() * 0.8, s: 0.25 + Math.random() * 0.35, y: -0.8 + Math.random() * 2.4};
    scene.add(m); minis.push(m);
  }

  var mx = 0, my = 0;
  window.addEventListener('pointermove', function(e){ mx = (e.clientX / window.innerWidth - 0.5); my = (e.clientY / window.innerHeight - 0.5); });

  var t0 = performance.now(), raf = 0, alive = true;
  // libère proprement la ressource graphique quand la page ou le cadre disparaît (évite de figer le navigateur)
  function stop(){
    if (!alive) return; alive = false;
    cancelAnimationFrame(raf);
    try { renderer.dispose(); renderer.forceContextLoss(); } catch (err) {}
  }
  window.addEventListener('pagehide', stop);
  window.addEventListener('beforeunload', stop);
  window.addEventListener('unload', stop);
  document.addEventListener('visibilitychange', function(){ if (document.hidden) { cancelAnimationFrame(raf); } else if (alive) { tick(); } });
  function tick(){
    if (!alive) return;
    var t = (performance.now() - t0) / 1000;
    var bob = Math.sin(t * 1.3) * 0.18;
    holder.position.y = 0.15 + bob;
    pill.rotation.y = t * 0.7 + mx * 1.2;
    holder.rotation.x = my * 0.4;
    ground.material.opacity = 0.30 - bob * 0.25;  // l'ombre s'éclaircit quand la pilule monte
    minis.forEach(function(m){
      var d = m.userData; d.a += d.s * 0.01;
      m.position.set(Math.cos(d.a) * d.r, d.y + Math.sin(t + d.a) * 0.15, Math.sin(d.a) * d.r * 0.55);
      m.rotation.x = t * d.s; m.rotation.z = t * d.s * 0.7;
    });
    renderer.render(scene, camera);
    raf = requestAnimationFrame(tick);
  }
  tick();
})();
</script></body></html>
"""


def render_pill(height: int = 360) -> None:
    """Affiche la pilule 3D. Si three.js est absent, n'affiche rien (le reste de la page reste utilisable)."""
    if not THREE_JS.exists():
        return
    components.html(PAGE.replace("__THREE__", THREE_JS.read_text(encoding="utf-8")), height=height)
