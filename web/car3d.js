// CarDoctor 3D damage view: a simple car built from primitives; parts turn red where damage was found.
// Marking is per area (photo side + damage type), not an exact position on the panel.
import * as THREE from '/vendor/three.module.min.js';

const box = document.getElementById('car3d');
const canvas = document.getElementById('car3dCanvas');
let renderer, scene, camera, car, parts = {}, damaged = [], angle = 0.7, tilt = 0.32, dragging = false, auto = true, last = 0;

function init() {
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); }
  catch { return false; }
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(35, 2, 0.1, 100);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(4, 6, 3); scene.add(sun);
  car = new THREE.Group(); scene.add(car);
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  const reg = (name, m) => { m.name = name; m.userData.base = m.material.color.getHex(); parts[name] = m; car.add(m); return m; };
  // Body: a side profile (front = +x) extruded across the width, with wheel arches.
  const prof = new THREE.Shape();
  prof.moveTo(-2.2, 0.36); prof.lineTo(-2.22, 0.82); prof.quadraticCurveTo(-2.15, 1.0, -1.85, 1.02); prof.lineTo(-1.2, 1.04);
  prof.quadraticCurveTo(-0.95, 1.38, -0.62, 1.45); prof.lineTo(0.38, 1.47); prof.quadraticCurveTo(0.7, 1.4, 1.08, 1.06);
  prof.lineTo(1.95, 0.95); prof.quadraticCurveTo(2.26, 0.88, 2.26, 0.6); prof.lineTo(2.22, 0.36); prof.lineTo(1.8, 0.36);
  prof.absarc(1.35, 0.36, 0.45, 0, Math.PI, false); prof.lineTo(-0.9, 0.36); prof.absarc(-1.35, 0.36, 0.45, 0, Math.PI, false); prof.lineTo(-2.2, 0.36);
  const bodyGeo = new THREE.ExtrudeGeometry(prof, { depth: 1.62, bevelEnabled: true, bevelThickness: 0.1, bevelSize: 0.08, bevelSegments: 4, curveSegments: 24 });
  bodyGeo.translate(0, 0, -0.81);
  const paint = new THREE.MeshPhysicalMaterial({ color: 0x3a7cb8, metalness: 0.45, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.08 });
  reg('body', new THREE.Mesh(bodyGeo, paint));
  // Glass: side windows follow the roofline; windshield and rear glass are tilted panes.
  const glassMat = () => new THREE.MeshPhysicalMaterial({ color: 0x1b2a36, metalness: 0.2, roughness: 0.05, transparent: true, opacity: 0.9 });
  const win = new THREE.Shape(); win.moveTo(-1.1, 1.08); win.quadraticCurveTo(-0.9, 1.34, -0.6, 1.4); win.lineTo(0.36, 1.42); win.quadraticCurveTo(0.62, 1.36, 0.98, 1.09); win.lineTo(-1.1, 1.08);
  for (const [n, z] of [['winL', -0.92], ['winR', 0.9]]) { const g = new THREE.ExtrudeGeometry(win, { depth: 0.02, bevelEnabled: false }); const m = reg(n, new THREE.Mesh(g, glassMat())); m.position.z = z; }
  const pane = (n, a, b, w) => { const dx = b[0] - a[0], dy = b[1] - a[1], len = Math.hypot(dx, dy) * 0.92;
    const m = reg(n, new THREE.Mesh(new THREE.BoxGeometry(len, 0.02, w), glassMat())); m.position.set((a[0] + b[0]) / 2 + (dy > 0 ? 0.03 : -0.03) * Math.sign(dx), (a[1] + b[1]) / 2 + 0.035, 0); m.rotation.z = Math.atan2(dy, dx); return m; };
  pane('windshield', [1.08, 1.06], [0.38, 1.47], 1.5); pane('rearGlass', [-1.2, 1.04], [-0.62, 1.45], 1.45);
  // Lamps.
  const lampMat = c => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.4 });
  for (const [n, x, z, c] of [['lampFL', 2.27, -0.6, 0xfff4cc], ['lampFR', 2.27, 0.6, 0xfff4cc], ['lampRL', -2.27, -0.62, 0xd9302c], ['lampRR', -2.27, 0.62, 0xd9302c]]) {
    const m = reg(n, new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.13, 0.38), lampMat(c))); m.position.set(x, x > 0 ? 0.74 : 0.86, z); }
  // Wheels: tyre, alloy rim and hub.
  const tyreMat = new THREE.MeshStandardMaterial({ color: 0x15181b, roughness: 0.85 });
  for (const [n, x, z] of [['wheelFL', 1.35, -0.86], ['wheelFR', 1.35, 0.86], ['wheelRL', -1.35, -0.86], ['wheelRR', -1.35, 0.86]]) {
    const w = reg(n, new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.27, 40), tyreMat.clone())); w.rotation.x = Math.PI / 2; w.position.set(x, 0.38, z);
    const rim = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.28, 24), new THREE.MeshStandardMaterial({ color: 0xc9d1d6, metalness: 0.9, roughness: 0.25 }));
    rim.rotation.x = Math.PI / 2; rim.position.set(x, 0.38, z + Math.sign(z) * 0.005); car.add(rim);
    for (let k = 0; k < 5; k++) { const sp = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.4, 0.02), rim.material); sp.position.set(x, 0.38, z + Math.sign(z) * 0.145); sp.rotation.z = k * Math.PI / 5; car.add(sp); } }
  // Damage overlays for body areas (hidden until damage is found on that side).
  const glow = () => new THREE.MeshStandardMaterial({ color: 0xe8433a, emissive: 0xe8433a, emissiveIntensity: 0.8, transparent: true, opacity: 0.55, depthWrite: false });
  for (const [n, size, pos] of [['front', [0.12, 0.55, 1.7], [2.3, 0.66, 0]], ['rear', [0.12, 0.6, 1.7], [-2.3, 0.68, 0]],
                                  ['left', [2.4, 0.5, 0.06], [0, 0.72, -0.93]], ['right', [2.4, 0.5, 0.06], [0, 0.72, 0.93]]]) {
    const m = reg(n, new THREE.Mesh(new THREE.BoxGeometry(...size), glow())); m.position.set(...pos); m.visible = false; m.userData.overlay = true; }
  const shadow = new THREE.Mesh(new THREE.CircleGeometry(1, 40), new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.18 }));
  shadow.rotation.x = -Math.PI / 2; shadow.scale.set(2.6, 1.15, 1); shadow.position.y = 0.005; scene.add(shadow);
  canvas.addEventListener('pointerdown', e => { dragging = true; auto = false; last = e.clientX; canvas.setPointerCapture(e.pointerId); });
  canvas.addEventListener('pointermove', e => { if (dragging) { angle -= (e.clientX - last) * 0.01; last = e.clientX; } });
  canvas.addEventListener('pointerup', () => { dragging = false; });
  for (const b of box.querySelectorAll('[data-look]')) b.addEventListener('click', () => { auto = false; angle = { front: 0, right: Math.PI / 2, rear: Math.PI, left: -Math.PI / 2 }[b.dataset.look]; });
  requestAnimationFrame(frame);
  return true;
}

// Which parts a finding marks, from the photo side and the damage type.
function targets(view, label) {
  const side = { front: ['front'], rear: ['rear'], left: ['left'], right: ['right'] };
  if (label === 'glass shatter') return { front: ['windshield'], rear: ['rearGlass'], left: ['winL'], right: ['winR'] }[view] || [];
  if (label === 'lamp broken') return { front: ['lampFL', 'lampFR'], rear: ['lampRL', 'lampRR'], left: ['lampFL', 'lampRL'], right: ['lampFR', 'lampRR'] }[view] || [];
  if (label === 'tire flat') return { front: ['wheelFL', 'wheelFR'], rear: ['wheelRL', 'wheelRR'], left: ['wheelFL', 'wheelRL'], right: ['wheelFR', 'wheelRR'] }[view] || [];
  return side[view] || [];
}

function frame(t) {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  if (w && (canvas.width !== Math.round(w * renderer.getPixelRatio()) || canvas.height !== Math.round(h * renderer.getPixelRatio()))) {
    renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  }
  if (auto) angle += 0.004;
  const r = 6.6;
  camera.position.set(Math.cos(angle) * r * Math.cos(tilt), r * Math.sin(tilt), Math.sin(angle) * r * Math.cos(tilt));
  camera.lookAt(0, 0.6, 0);
  const pulse = 0.55 + 0.45 * Math.sin(t / 220);
  for (const m of damaged) { if (m.userData.overlay) { m.visible = true; m.material.opacity = 0.25 + 0.4 * pulse; continue; } m.material.color.setHex(0xe8433a); if (m.material.emissive) { m.material.emissive.setHex(0xe8433a); m.material.emissiveIntensity = pulse; } }
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

function show(result) {
  if (!result.photos || !result.photos.length) { box.hidden = true; return; }
  if (!renderer && !init()) { box.hidden = true; return; }
  for (const m of Object.values(parts)) {
    if (m.userData.overlay) { m.visible = false; continue; }
    m.material.color.setHex(m.userData.base);
    if (m.material.emissive) { m.material.emissive.setHex(m.name.startsWith('lamp') ? m.userData.base : 0x000000); m.material.emissiveIntensity = m.name.startsWith('lamp') ? 0.4 : 0; }
  }
  const names = new Set(result.findings.flatMap(f => targets(f.view, f.label)));
  damaged = [...names].map(n => parts[n]).filter(Boolean);
  const list = document.getElementById('car3dList');
  const nice = { front: 'Front', rear: 'Rear', left: 'Left side', right: 'Right side', windshield: 'Windshield', rearGlass: 'Rear window', winL: 'Left windows', winR: 'Right windows',
    lampFL: 'Front-left lamp', lampFR: 'Front-right lamp', lampRL: 'Rear-left lamp', lampRR: 'Rear-right lamp', wheelFL: 'Front-left wheel', wheelFR: 'Front-right wheel', wheelRL: 'Rear-left wheel', wheelRR: 'Rear-right wheel' };
  list.textContent = damaged.length ? 'Marked: ' + damaged.map(m => nice[m.name] || m.name).join(', ') : 'No damaged area to mark.';
  auto = true; box.hidden = false;
}

window.addEventListener('cardoctor:result', e => show(e.detail));
