// Capsule 3D (three.js local). Elle tourne doucement, et s'ouvre quand on lance l'analyse.
// Sans WebGL ou avec "réduire les animations", on affiche une capsule fixe : rien ne casse.

const COBALT = 0x3fae7f;
const BONE = 0xe8eeea;
const reduced = () => window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
const ease = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

export class Capsule {
  constructor(canvas, fallback) {
    this.canvas = canvas;
    this.fallback = fallback;
    this.openness = 0;      // 0 fermée, 1 ouverte
    this.target = 0;
    this.alive = false;
    try {
      if (!window.THREE) throw new Error("three.js absent");
      this.build();
      this.alive = true;
      if (fallback) fallback.hidden = true;
      this.loop();
    } catch (err) {
      if (fallback) fallback.hidden = false;
      canvas.hidden = true;
    }
  }

  build() {
    const T = window.THREE;
    const r = new T.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: true });
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.shadowMap.enabled = true;
    r.shadowMap.type = T.PCFSoftShadowMap;
    this.renderer = r;

    const scene = (this.scene = new T.Scene());
    const camera = (this.camera = new T.PerspectiveCamera(30, 1, 0.1, 100));
    scene.add(new T.HemisphereLight(0xffffff, 0xaab6d4, 0.85));
    const key = new T.DirectionalLight(0xffffff, 1.15);
    key.position.set(-4, 8, 6);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    key.shadow.radius = 7;
    Object.assign(key.shadow.camera, { left: -7, right: 7, top: 7, bottom: -7 });
    scene.add(key);
    const rim = new T.PointLight(COBALT, 1.4, 30);
    rim.position.set(5, 2, -3);
    scene.add(rim);
    this.glow = new T.PointLight(0xb8ecd2, 0, 12);
    scene.add(this.glow);

    const ground = new T.Mesh(new T.PlaneGeometry(40, 40), new T.ShadowMaterial({ opacity: 0.2 }));
    ground.rotation.x = -Math.PI / 2;
    ground.position.y = -2.3;
    ground.receiveShadow = true;
    scene.add(ground);
    this.ground = ground;

    const mat = (color) =>
      new T.MeshPhysicalMaterial({ color, roughness: 0.2, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.06 });
    const half = (color, up) => {
      const g = new T.Group();
      const R = 0.9, L = 1.15, m = mat(color);
      const cyl = new T.Mesh(new T.CylinderGeometry(R, R, L, 64, 1, true), m);
      cyl.position.y = (up ? 1 : -1) * (L / 2);
      const cap = new T.Mesh(new T.SphereGeometry(R, 64, 32, 0, Math.PI * 2, up ? 0 : Math.PI / 2, Math.PI / 2), m);
      cap.position.y = (up ? 1 : -1) * L;
      const lid = new T.Mesh(new T.CircleGeometry(R, 64), mat(up ? 0xcdeedd : 0xdbe3df));
      lid.rotation.x = up ? Math.PI / 2 : -Math.PI / 2;
      [cyl, cap].forEach((x) => (x.castShadow = true));
      g.add(cyl, cap, lid);
      return g;
    };
    this.top = half(COBALT, true);
    this.bottom = half(BONE, false);
    const body = (this.body = new T.Group());
    body.add(this.top, this.bottom);
    body.rotation.z = Math.PI / 5;
    scene.add(body);

    // petites billes : les essais qui s'échappent à l'ouverture
    this.bits = [];
    const geo = new T.SphereGeometry(0.1, 20, 14);
    for (let i = 0; i < 22; i++) {
      const m = new T.Mesh(geo, mat(i % 3 === 0 ? BONE : COBALT));
      m.visible = false;
      m.userData = { vx: (Math.random() - 0.5) * 1.6, vy: 1.2 + Math.random() * 1.8, vz: (Math.random() - 0.5) * 1.2, s: 0.6 + Math.random() * 0.9 };
      scene.add(m);
      this.bits.push(m);
    }

    this.mx = 0;
    this.my = 0;
    this.onMove = (e) => {
      this.mx = e.clientX / innerWidth - 0.5;
      this.my = e.clientY / innerHeight - 0.5;
    };
    addEventListener("pointermove", this.onMove);
    this.ro = new ResizeObserver(() => this.resize());
    this.ro.observe(this.canvas);
    this.resize();
    this.t0 = performance.now();
    addEventListener("pagehide", () => this.dispose());
  }

  resize() {
    if (!this.renderer) return;
    const w = this.canvas.clientWidth || 480, h = this.canvas.clientHeight || 420;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    const back = Math.max(0.9, 1.45 / (w / h));
    this.camera.position.set(0, 1.8 * back, 7.6 * back);
    this.camera.lookAt(0, 0, 0);
    this.camera.updateProjectionMatrix();
  }

  open() { this.target = 1; this.burst = performance.now(); return new Promise((res) => setTimeout(res, reduced() ? 0 : 950)); }
  close() { this.target = 0; this.bits.forEach((b) => (b.visible = false)); }

  loop = () => {
    if (!this.alive) return;
    const t = (performance.now() - this.t0) / 1000;
    const still = reduced();
    this.openness += (this.target - this.openness) * (still ? 1 : 0.09);
    const o = ease(Math.min(1, Math.max(0, this.openness)));
    const gap = o * 1.15;
    this.top.position.y = gap;
    this.bottom.position.y = -gap;
    this.glow.intensity = o * 2.4;
    this.glow.position.set(0, 0, 0.6);
    this.body.position.y = still ? 0 : Math.sin(t * 1.2) * 0.14;
    this.body.rotation.y = still ? 0.5 : t * 0.5 + this.mx * 1.1;
    this.body.rotation.x = this.my * 0.35;
    this.ground.material.opacity = 0.2 - (still ? 0 : Math.sin(t * 1.2) * 0.03);

    if (this.target === 1 && !still) {
      const dt = (performance.now() - this.burst) / 1000;
      this.bits.forEach((b) => {
        const d = b.userData;
        b.visible = dt > 0.35;
        const k = Math.max(0, dt - 0.35);
        b.position.set(d.vx * k * d.s, d.vy * k * d.s - 0.4 * k * k, d.vz * k * d.s);
        b.scale.setScalar(Math.max(0.01, 1 - k * 0.45));
      });
    }
    this.renderer.render(this.scene, this.camera);
    this.raf = requestAnimationFrame(this.loop);
  };

  dispose() {
    if (!this.alive) return;
    this.alive = false;
    cancelAnimationFrame(this.raf);
    removeEventListener("pointermove", this.onMove);
    this.ro?.disconnect();
    try { this.renderer.dispose(); this.renderer.forceContextLoss(); } catch (e) { /* rien à libérer */ }
  }
}
