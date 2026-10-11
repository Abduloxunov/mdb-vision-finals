// CarDoctor 3D damage view: a simple car built from primitives; parts turn red where damage was found.
// Marking is per area (photo side + damage type), not an exact position on the panel.
import * as THREE from '/vendor/three.module.min.js';

const box = document.getElementById('car3d');
const canvas = document.getElementById('car3dCanvas');
let renderer, scene, camera, car, parts = {}, damaged = [], angle = 0.7, tilt = 0.45, dragging = false, auto = true, last = 0;

function init() {
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true }); }
  catch { return false; }
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(35, 2, 0.1, 100);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x8899aa, 1.6));
  const sun = new THREE.DirectionalLight(0xffffff, 1.4); sun.position.set(4, 6, 3); scene.add(sun);
  const ground = new THREE.Mesh(new THREE.CircleGeometry(4.2, 48), new THREE.MeshStandardMaterial({ color: 0xe6eef0 }));
  ground.rotation.x = -Math.PI / 2; scene.add(ground);
  car = new THREE.Group(); scene.add(car);
  const paint = () => new THREE.MeshStandardMaterial({ color: 0x2f6f9f, metalness: 0.35, roughness: 0.45 });
  const glass = () => new THREE.MeshStandardMaterial({ color: 0x9fc6dc, metalness: 0.1, roughness: 0.1, transparent: true, opacity: 0.85 });
  const add = (name, geo, mat, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); m.userData.base = mat.color.getHex(); m.name = name; car.add(m); parts[name] = m; return m; };
  // Front of the car is +x; right side is +z; left side is -z.
  add('body', new THREE.BoxGeometry(2.0, 0.62, 1.66), paint(), 0, 0.62, 0);
  add('front', new THREE.BoxGeometry(1.05, 0.55, 1.66), paint(), 1.52, 0.58, 0);
  add('rear', new THREE.BoxGeometry(0.95, 0.6, 1.66), paint(), -1.47, 0.61, 0);
  add('left', new THREE.BoxGeometry(2.0, 0.5, 0.05), paint(), 0, 0.6, -0.86);
  add('right', new THREE.BoxGeometry(2.0, 0.5, 0.05), paint(), 0, 0.6, 0.86);
  add('roof', new THREE.BoxGeometry(1.5, 0.08, 1.4), paint(), -0.15, 1.38, 0);
  add('windshield', new THREE.BoxGeometry(0.06, 0.48, 1.36), glass(), 0.68, 1.15, 0).rotation.z = -0.55;
  add('rearGlass', new THREE.BoxGeometry(0.06, 0.45, 1.36), glass(), -0.96, 1.15, 0).rotation.z = 0.6;
  add('winL', new THREE.BoxGeometry(1.45, 0.42, 0.04), glass(), -0.15, 1.13, -0.71);
  add('winR', new THREE.BoxGeometry(1.45, 0.42, 0.04), glass(), -0.15, 1.13, 0.71);
  const lamp = c => new THREE.MeshStandardMaterial({ color: c, emissive: c, emissiveIntensity: 0.25 });
  add('lampFL', new THREE.BoxGeometry(0.05, 0.14, 0.34), lamp(0xfff1b8), 2.06, 0.68, -0.6);
  add('lampFR', new THREE.BoxGeometry(0.05, 0.14, 0.34), lamp(0xfff1b8), 2.06, 0.68, 0.6);
  add('lampRL', new THREE.BoxGeometry(0.05, 0.14, 0.3), lamp(0xd9483b), -1.96, 0.72, -0.6);
  add('lampRR', new THREE.BoxGeometry(0.05, 0.14, 0.3), lamp(0xd9483b), -1.96, 0.72, 0.6);
  const tyre = () => new THREE.MeshStandardMaterial({ color: 0x23272b, roughness: 0.9 });
  for (const [n, x, z] of [['wheelFL', 1.3, -0.84], ['wheelFR', 1.3, 0.84], ['wheelRL', -1.25, -0.84], ['wheelRR', -1.25, 0.84]]) {
    const w = add(n, new THREE.CylinderGeometry(0.36, 0.36, 0.26, 28), tyre(), x, 0.36, z); w.rotation.x = Math.PI / 2;
  }
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
  const r = 6.2;
  camera.position.set(Math.cos(angle) * r * Math.cos(tilt), r * Math.sin(tilt), Math.sin(angle) * r * Math.cos(tilt));
  camera.lookAt(0, 0.6, 0);
  const pulse = 0.55 + 0.45 * Math.sin(t / 220);
  for (const m of damaged) { m.material.color.setHex(0xe8433a); if (m.material.emissive) { m.material.emissive.setHex(0xe8433a); m.material.emissiveIntensity = pulse; } }
  renderer.render(scene, camera);
  requestAnimationFrame(frame);
}

function show(result) {
  if (!result.photos || !result.photos.length) { box.hidden = true; return; }
  if (!renderer && !init()) { box.hidden = true; return; }
  for (const m of Object.values(parts)) {
    m.material.color.setHex(m.userData.base);
    if (m.material.emissive) { m.material.emissive.setHex(m.name.startsWith('lamp') ? m.userData.base : 0x000000); m.material.emissiveIntensity = m.name.startsWith('lamp') ? 0.25 : 0; }
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
