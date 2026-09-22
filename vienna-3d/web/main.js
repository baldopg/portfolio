// Vienna · portfolio 3D, estética Quai Network en blanco y negro.
// Ciudad modelada en Blender (city.glb) + recorrido de cámara (camera_path.json).
// El scroll mueve la cámara por dos curvas (posición y objetivo) con una pausa en cada parada.
// Edificios con el material "Light 2" de Blender: base negra con barniz y emisión que depende
// del ángulo de visión (Layer Weight · Facing invertido, Blend 0.83). El monumento de la parada
// activa sube su emisión y su halo; bloom, bruma, polvo, estelas de tranvía por el Ring y grano.

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { Pass, FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { ShaderPass } from 'three/addons/postprocessing/ShaderPass.js';
import { FXAAShader } from 'three/addons/shaders/FXAAShader.js';
import Lenis from 'lenis';
import { setupVideo, ensureLoaded } from './video.js?v=20260922144106';
import { initDetail } from './detail.js?v=20260922144106';

// ------------------------------------------------------------------ constantes
const SEG = 1.5;          // alturas de ventana de scroll entre dos paradas
const HOLD = 0.3;         // fracción de cada tramo en la que la cámara se queda en la parada
const S = 0.6;            // compresión del plano (igual que en Blender)
const WHEEL_R = 60.96 / 2;
const HUB_Y = 34.0;
const GLOW = new THREE.Color(1.0, 0.9825, 0.964);   // ColorRamp de "Light 2" en la posición 0
const PLACES = [
  ['WIENER_RIESENRAD', 'PRATER · 1897 · 64.75 M'],
  ['STEPHANSDOM', 'STEPHANSPLATZ · 136.4 M'],
  ['WIENER_STAATSOPER', 'OPERNRING · 1869'],
  ['KARLSKIRCHE', 'KARLSPLATZ · 1737'],
  ['PARLAMENT', 'RINGSTRASSE · 1883'],
  ['RATHAUS', 'RATHAUSPLATZ · 1883 · 98 M'],
  ['BURGTHEATER', 'UNIVERSITÄTSRING · 1888'],
  ['WIEN', '48.2082° N · 16.3738° E'],
];
// qué parada ilumina a cada monumento (la última, vista aérea, los enciende todos)
const FOCUS_STOP = {
  RR_Root: 0, LM_Stephansdom: 1, LM_Staatsoper: 2, LM_Secession: 2.5, LM_Karlskirche: 3,
  LM_Parlament: 4, LM_Rathaus: 5, LM_Burgtheater: 6, LM_Votivkirche: 6.5, LM_Donauturm: 99,
};
const LIGHT = { blocks: 0.3, trees: 0.045, lmBase: 0.6, lmFinale: 1.1 };
// pico de "Light 2" en la parada: las fachadas grandes y planas que miran a cámara necesitan menos
const PEAK = { RR_Root: 1.6, LM_Stephansdom: 1.8, LM_Staatsoper: 1.15, LM_Secession: 1.3, LM_Karlskirche: 1.4,
  LM_Parlament: 1.15, LM_Rathaus: 1.05, LM_Burgtheater: 1.2, LM_Votivkirche: 1.5, LM_Donauturm: 1.2 };

const isSmall = matchMedia('(max-width: 820px), (pointer: coarse)').matches;
const B2T = (v) => new THREE.Vector3(v[0], v[2], -v[1]);           // Blender Z-up -> three Y-up
const MAP = (e, n, h = 0) => new THREE.Vector3(e * S, h, -n * S);  // metros reales -> escena
const clamp01 = (x) => Math.min(1, Math.max(0, x));
const smooth = (a, b, x) => { const t = clamp01((x - a) / (b - a)); return t * t * (3 - 2 * t); };
const easeInOut = (t) => (t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2);

// ------------------------------------------------------------------ renderer + escena
const canvas = document.getElementById('city');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: false, powerPreference: 'high-performance' });
let DPR = Math.min(devicePixelRatio, isSmall ? 1.4 : 1.6);
renderer.setPixelRatio(DPR);
renderer.setSize(innerWidth, innerHeight, false);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
renderer.setClearColor(0x050506);

const scene = new THREE.Scene();
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.22;
scene.add(new THREE.HemisphereLight(0xffffff, 0x000000, 0.12));

const camera = new THREE.PerspectiveCamera(40, innerWidth / innerHeight, 2, 9000);

// ------------------------------------------------------------------ materiales
const TIME = { value: 0 };
const NOISE_GLSL = /* glsl */`
  float hash13(vec3 p){ p = fract(p * 0.1031); p += dot(p, p.zyx + 31.32); return fract((p.x + p.y) * p.z); }
  float vnoise(vec3 p){
    vec3 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
    float n000 = hash13(i), n100 = hash13(i + vec3(1,0,0)), n010 = hash13(i + vec3(0,1,0)), n110 = hash13(i + vec3(1,1,0));
    float n001 = hash13(i + vec3(0,0,1)), n101 = hash13(i + vec3(1,0,1)), n011 = hash13(i + vec3(0,1,1)), n111 = hash13(i + vec3(1,1,1));
    return mix(mix(mix(n000, n100, f.x), mix(n010, n110, f.x), f.y), mix(mix(n001, n101, f.x), mix(n011, n111, f.x), f.y), f.z);
  }
`;
function injectWorldPos(shader) {
  shader.vertexShader = shader.vertexShader
    .replace('#include <common>', '#include <common>\nvarying vec3 vWPos; varying vec3 vLPos;')
    .replace('#include <project_vertex>', `#include <project_vertex>
      vLPos = position;
      #ifdef USE_INSTANCING
        vWPos = (modelMatrix * instanceMatrix * vec4(transformed, 1.0)).xyz;
      #else
        vWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;
      #endif`);
  shader.fragmentShader = shader.fragmentShader
    .replace('#include <common>', '#include <common>\nvarying vec3 vWPos; varying vec3 vLPos;\n' + NOISE_GLSL);
}

// "Light 2": emisión = GLOW * |N·V|^2.94 * fuerza, con la textura de ruido FBM del original
function light2(strength, { roof = false, bulbs = false } = {}) {
  const m = new THREE.MeshPhysicalMaterial({ color: 0x000000, roughness: 0.5, metalness: 0, clearcoat: 0.25, clearcoatRoughness: 0.03 });
  const uStrength = { value: strength };
  m.userData.uStrength = uStrength;
  m.onBeforeCompile = (shader) => {
    shader.uniforms.uStrength = uStrength;
    shader.uniforms.uGlow = { value: GLOW };
    shader.uniforms.uTime = TIME;
    injectWorldPos(shader);
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', '#include <common>\nuniform float uStrength; uniform vec3 uGlow; uniform float uTime;')
      .replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
        float facing = pow(abs(dot(normalize(normal), normalize(vViewPosition))), 2.94);
        float grain = 0.72 + 0.28 * vnoise(vWPos * 0.9) * (0.6 + 0.4 * vnoise(vWPos * 3.7));
        totalEmissiveRadiance += uGlow * facing * grain * uStrength ${roof ? '* 0.55' : ''};
        ${bulbs ? `
        vec2 q = vLPos.xy - vec2(0.0, ${HUB_Y.toFixed(1)});
        float r = length(q), a = atan(q.y, q.x);
        float ring = 1.0 - smoothstep(0.35, 0.9, abs(r - 27.9));
        float dots = step(0.8, fract(a / 6.2831853 * 150.0));
        float chase = 0.55 + 0.45 * sin(a * 15.0 - uTime * 1.3);
        totalEmissiveRadiance += uGlow * ring * dots * chase * (0.9 + uStrength * 0.35);` : ''}`);
  };
  m.customProgramCacheKey = () => `light2-${roof}-${bulbs}`;
  return m;
}

// ventanas de las manzanas: encendidas al azar (vida en la ciudad)
function windowsMat() {
  const m = new THREE.MeshStandardMaterial({ color: 0x020202, roughness: 0.4 });
  m.onBeforeCompile = (shader) => {
    injectWorldPos(shader);
    shader.fragmentShader = shader.fragmentShader.replace('#include <emissivemap_fragment>', `#include <emissivemap_fragment>
      float cell = hash13(floor(vWPos * vec3(0.55, 0.3, 0.55)) + 7.0);
      float on = step(0.72, cell) * (0.7 + 0.8 * hash13(floor(vWPos * 0.21) + 3.0));
      totalEmissiveRadiance += vec3(1.0, 0.97, 0.92) * on * 1.9;`);
  };
  m.customProgramCacheKey = () => 'windows';
  return m;
}

const dark = (color, rough = 0.9, extra = {}) => new THREE.MeshStandardMaterial({ color, roughness: rough, metalness: 0, ...extra });
const FLAT = {
  Road: dark('#101012', 0.85),
  Water: dark('#030304', 0.06, { envMapIntensity: 2.2 }),
  Park: dark('#07070a', 1.0),
  Ground: dark('#050507', 1.0),
};
const INK_DARK = dark('#000000', 0.35, { envMapIntensity: 0.6 });
const BLOCK_LIGHT = light2(LIGHT.blocks);
const BLOCK_ROOF = light2(LIGHT.blocks, { roof: true });
const BLOCK_WINDOWS = windowsMat();
const TREE_LIGHT = light2(LIGHT.trees);

// ------------------------------------------------------------------ postproceso
const EdgeFogShader = {
  uniforms: {
    tColor: { value: null }, tDepth: { value: null },
    uRes: { value: new THREE.Vector2() }, uNear: { value: camera.near }, uFar: { value: camera.far },
    uSkyTop: { value: new THREE.Color('#010102') }, uSkyHorizon: { value: new THREE.Color('#121215') },
    uFog: { value: new THREE.Color('#0b0b0e') }, uEdge: { value: new THREE.Color('#000000') }, uEdgeStrength: { value: 0.85 },
    uFogNear: { value: 280 }, uFogFar: { value: 2200 }, uThick: { value: 1 },
  },
  vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
  fragmentShader: /* glsl */`
    uniform sampler2D tColor; uniform sampler2D tDepth;
    uniform vec2 uRes; uniform float uNear, uFar, uEdgeStrength, uFogNear, uFogFar, uThick;
    uniform vec3 uSkyTop, uSkyHorizon, uFog, uEdge;
    varying vec2 vUv;
    float linz(float d){ float z = d * 2.0 - 1.0; return (2.0 * uNear * uFar) / (uFar + uNear - z * (uFar - uNear)); }
    void main(){
      vec2 px = uThick / uRes;
      float d0 = texture2D(tDepth, vUv).x;
      vec4 col = texture2D(tColor, vUv);
      vec3 sky = mix(uSkyHorizon, uSkyTop, smoothstep(0.3, 0.95, vUv.y));
      if (d0 >= 0.99999) { gl_FragColor = vec4(sky + col.rgb, 1.0); return; }     // cielo (+ lo aditivo: polvo, halos)
      float dl = texture2D(tDepth, vUv - vec2(px.x, 0.0)).x;
      float dr = texture2D(tDepth, vUv + vec2(px.x, 0.0)).x;
      float dd = texture2D(tDepth, vUv - vec2(0.0, px.y)).x;
      float du = texture2D(tDepth, vUv + vec2(0.0, px.y)).x;
      float z0 = linz(d0), zl = linz(dl), zr = linz(dr), zd = linz(dd), zu = linz(du);
      float sil = max(max(abs(zl - z0), abs(zr - z0)), max(abs(zu - z0), abs(zd - z0))) / z0;
      float w0 = 1.0 / z0;
      float lap = abs(1.0/zl + 1.0/zr + 1.0/zu + 1.0/zd - 4.0 * w0) / w0;
      float edge = max(smoothstep(0.015, 0.05, sil), smoothstep(0.0025, 0.012, lap));
      float fog = smoothstep(uFogNear, uFogFar, z0);
      col.rgb = mix(col.rgb, uEdge, edge * uEdgeStrength * (1.0 - fog));
      // bruma: se come la distancia y deja una luz baja en el horizonte
      col.rgb = mix(col.rgb, uFog + sky * 0.4, fog * 0.92);
      gl_FragColor = col;
    }`,
};
class EdgeFogPass extends Pass {
  constructor() {
    super();
    this.material = new THREE.ShaderMaterial({ ...EdgeFogShader, uniforms: THREE.UniformsUtils.clone(EdgeFogShader.uniforms), depthTest: false, depthWrite: false });
    this.quad = new FullScreenQuad(this.material);
  }
  render(renderer, writeBuffer, readBuffer) {
    this.material.uniforms.tColor.value = readBuffer.texture;
    this.material.uniforms.tDepth.value = readBuffer.depthTexture;
    renderer.setRenderTarget(this.renderToScreen ? null : writeBuffer);
    this.quad.render(renderer);
  }
}
// grano, viñeta y aberración cromática (crece mientras la cámara viaja)
const FilmShader = {
  uniforms: { tDiffuse: { value: null }, uTime: { value: 0 }, uCA: { value: 0 }, uGrain: { value: 0.055 }, uVignette: { value: 0.42 } },
  vertexShader: /* glsl */`varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: /* glsl */`
    uniform sampler2D tDiffuse; uniform float uTime, uCA, uGrain, uVignette; varying vec2 vUv;
    float rnd(vec2 p){ return fract(sin(dot(p, vec2(12.9898, 78.233)) + uTime * 61.0) * 43758.5453); }
    void main(){
      vec2 c = vUv - 0.5;
      vec2 off = c * uCA * 0.012;
      vec3 col = vec3(texture2D(tDiffuse, vUv + off).r, texture2D(tDiffuse, vUv).g, texture2D(tDiffuse, vUv - off).b);
      col *= 1.0 - uVignette * smoothstep(0.25, 0.85, length(c * vec2(1.1, 1.0)));
      col += (rnd(vUv * 1000.0) - 0.5) * uGrain;
      gl_FragColor = vec4(col, 1.0);
    }`,
};

const rt = new THREE.WebGLRenderTarget(1, 1, { type: THREE.HalfFloatType, depthTexture: new THREE.DepthTexture(1, 1) });
const composer = new EffectComposer(renderer, rt);
// el clon interno comparte la fuente de la textura de profundidad: cada búfer necesita la suya
composer.renderTarget2.depthTexture = new THREE.DepthTexture(1, 1);
composer.addPass(new RenderPass(scene, camera));
const edgePass = new EdgeFogPass();
composer.addPass(edgePass);
const bloom = new UnrealBloomPass(new THREE.Vector2(256, 256), 0.55, 0.4, 1.0);
composer.addPass(bloom);
composer.addPass(new OutputPass());
const fxaa = new ShaderPass(FXAAShader);
composer.addPass(fxaa);
const film = new ShaderPass(FilmShader);
composer.addPass(film);

// ------------------------------------------------------------------ polvo flotante (sigue a la cámara)
const DUST_BOX = new THREE.Vector3(420, 180, 420);
const dust = (() => {
  const n = isSmall ? 900 : 1800;
  const pos = new Float32Array(n * 3), seed = new Float32Array(n);
  for (let i = 0; i < n; i++) {
    pos[i * 3] = Math.random() * DUST_BOX.x; pos[i * 3 + 1] = Math.random() * DUST_BOX.y; pos[i * 3 + 2] = Math.random() * DUST_BOX.z;
    seed[i] = Math.random();
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  g.setAttribute('seed', new THREE.BufferAttribute(seed, 1));
  const m = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { uTime: TIME, uCam: { value: new THREE.Vector3() }, uBox: { value: DUST_BOX }, uPx: { value: DPR } },
    vertexShader: /* glsl */`
      attribute float seed; uniform float uTime; uniform vec3 uCam, uBox; uniform float uPx; varying float vA;
      void main(){
        vec3 p = position + vec3(sin(uTime * 0.07 + seed * 40.0) * 6.0, uTime * (0.6 + seed) , cos(uTime * 0.05 + seed * 30.0) * 6.0);
        p = mod(p - uCam + uBox * 0.5, uBox) - uBox * 0.5 + uCam;   // caja que envuelve a la cámara
        p.y = max(p.y, 1.0);
        vec4 mv = modelViewMatrix * vec4(p, 1.0);
        float big = step(0.93, seed);
        gl_PointSize = uPx * mix(1.6, 5.0, big) * (120.0 / -mv.z);
        vA = (0.35 + 0.65 * seed) * (0.6 + 0.4 * sin(uTime * (0.8 + seed * 2.0) + seed * 60.0)) * mix(1.0, 0.35, big) * smoothstep(900.0, 60.0, -mv.z);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: /* glsl */`
      varying float vA;
      void main(){ float d = length(gl_PointCoord - 0.5); float a = smoothstep(0.5, 0.0, d); gl_FragColor = vec4(vec3(1.0), a * vA * 0.9); }`,
  });
  const pts = new THREE.Points(g, m);
  pts.frustumCulled = false;
  pts.renderOrder = 5;
  scene.add(pts);
  return m;
})();

// ------------------------------------------------------------------ estelas de luz (tranvías del Ring, canal, calles)
const TRAIL_PATHS = [
  { real: [[-133, 1034], [-500, 860], [-808, 690], [-897, 500], [-945, 167], [-960, -33], [-900, -300], [-822, -500], [-600, -640], [-378, -700], [-67, -801], [215, -834], [438, -500], [511, -222], [697, 167], [808, 356]], lanes: [-7, -3, 3, 7], speed: 1.0 },
  { real: [[-1500, 2400], [-700, 1500], [-133, 1034], [348, 367], [808, 356], [1300, 50], [1900, -500]], lanes: [-26, 26], speed: 0.6 },
  { real: [[348, 367], [1000, 640], [1500, 830], [1692, 901]], lanes: [-4, 4], speed: 0.8 },
  { real: [[0, -40], [-120, -350], [-230, -660]], lanes: [0], speed: 0.5 },
  { real: [[-60, 40], [-260, 110], [-330, 160]], lanes: [0], speed: 0.5 },
];
const trailMat = new THREE.ShaderMaterial({
  transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide,
  uniforms: { uTime: TIME },
  vertexShader: /* glsl */`
    attribute float along; attribute float lane; attribute float side;
    varying float vAlong; varying float vLane; varying float vSide;
    void main(){ vAlong = along; vLane = lane; vSide = side; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
  fragmentShader: /* glsl */`
    uniform float uTime; varying float vAlong; varying float vLane; varying float vSide;
    float h(float x){ return fract(sin(x * 91.7) * 43758.5453); }
    void main(){
      float dir = mod(vLane, 2.0) < 1.0 ? 1.0 : -1.0;
      float spd = 22.0 + 10.0 * h(vLane + 1.0);
      float t = (vAlong - dir * uTime * spd) / 140.0 + h(vLane) * 13.0;
      float cell = floor(t), f = fract(t);
      float on = step(0.45, h(cell + vLane * 7.0));
      float len = 0.18 + 0.25 * h(cell * 3.1);
      float head = dir > 0.0 ? 1.0 - f : f;                        // la cabeza va hacia delante
      float streak = smoothstep(len, 0.0, head) * smoothstep(0.0, 0.015, head);
      float core = 1.0 - smoothstep(0.0, 1.0, abs(vSide));
      float base = 0.05 * core;                                     // raíl tenue siempre visible
      gl_FragColor = vec4(vec3(1.0, 0.985, 0.96) * (base + on * streak * core * 3.2), 1.0);
    }`,
});
function buildTrails() {
  const positions = [], along = [], laneA = [], sideA = [], index = [];
  let laneId = 0, v = 0;
  for (const tp of TRAIL_PATHS) {
    const curve = new THREE.CatmullRomCurve3(tp.real.map(([e, n]) => MAP(e, n, 0)), false, 'centripetal');
    const len = curve.getLength();
    const N = Math.max(8, Math.round(len / 6));
    const pts = curve.getSpacedPoints(N);
    for (const off of tp.lanes) {
      laneId++;
      let acc = 0;
      for (let i = 0; i <= N; i++) {
        const p = pts[i], q = pts[Math.min(i + 1, N)], o = pts[Math.max(i - 1, 0)];
        const tan = new THREE.Vector3().subVectors(q, o).setY(0).normalize();
        const nor = new THREE.Vector3(-tan.z, 0, tan.x);
        if (i > 0) acc += p.distanceTo(pts[i - 1]);
        const c = p.clone().addScaledVector(nor, off).setY(0.9);
        for (const s of [-1, 1]) {
          const w = c.clone().addScaledVector(nor, s * 0.9);
          positions.push(w.x, w.y, w.z); along.push(acc); laneA.push(laneId); sideA.push(s);
        }
        if (i < N) index.push(v, v + 1, v + 2, v + 1, v + 3, v + 2);
        v += 2;
      }
    }
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  g.setAttribute('along', new THREE.Float32BufferAttribute(along, 1));
  g.setAttribute('lane', new THREE.Float32BufferAttribute(laneA, 1));
  g.setAttribute('side', new THREE.Float32BufferAttribute(sideA, 1));
  g.setIndex(index);
  const mesh = new THREE.Mesh(g, trailMat);
  mesh.frustumCulled = false;
  mesh.renderOrder = 4;
  scene.add(mesh);
}

// ------------------------------------------------------------------ halos detrás de los monumentos
const haloTex = (() => {
  const c = document.createElement('canvas'); c.width = c.height = 256;
  const x = c.getContext('2d');
  const gr = x.createRadialGradient(128, 128, 0, 128, 128, 128);
  gr.addColorStop(0, 'rgba(255,255,255,0.55)'); gr.addColorStop(0.35, 'rgba(255,255,255,0.16)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
  x.fillStyle = gr; x.fillRect(0, 0, 256, 256);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const halos = [];   // { sprite, stop, base }

// ------------------------------------------------------------------ recorrido
let camCurve, tgtCurve, stopKeys = [], stopCount = PLACES.length, keyCount = 1;
const camPos = new THREE.Vector3(), camTgt = new THREE.Vector3();
const wantPos = new THREE.Vector3(), wantTgt = new THREE.Vector3();

function sampleAt(scrollY) {
  const P = Math.max(0, scrollY / (SEG * innerHeight));
  const i = Math.min(Math.floor(P), stopCount - 1);
  const f = P - i;
  let t = 0;
  if (i < stopCount - 1 && f > HOLD) t = easeInOut((f - HOLD) / (1 - HOLD));
  const ka = stopKeys[i], kb = stopKeys[Math.min(i + 1, stopCount - 1)];
  const u = (ka + (kb - ka) * t) / (keyCount - 1);
  camCurve.getPoint(u, wantPos);
  tgtCurve.getPoint(u, wantTgt);
  return i + t;
}
const stopY = (i) => i * SEG * innerHeight;

function resize() {
  const w = innerWidth, h = innerHeight;
  camera.aspect = w / h;
  const tanH = 18 / 35;                                  // 35 mm sobre sensor de 36 mm (como en Blender)
  const vfov = 2 * Math.atan(tanH / Math.max(camera.aspect, 1)) * (camera.aspect < 1 ? 1.3 : 1);
  camera.fov = THREE.MathUtils.radToDeg(Math.min(vfov, THREE.MathUtils.degToRad(74)));
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(DPR);
  renderer.setSize(w, h, false);
  composer.setPixelRatio(DPR);
  composer.setSize(w, h);
  edgePass.material.uniforms.uRes.value.set(w * DPR, h * DPR);
  edgePass.material.uniforms.uThick.value = Math.max(1, DPR * 0.8);
  fxaa.material.uniforms.resolution.value.set(1 / (w * DPR), 1 / (h * DPR));
  dust.uniforms.uPx.value = DPR;
  document.getElementById('track').style.height = `${(stopCount - 1) * SEG * h + h}px`;
}

// ------------------------------------------------------------------ interfaz
document.querySelectorAll('.panel').forEach((el) => el.setAttribute('data-lenis-prevent', ''));   // scroll interno en móvil
const panels = [...document.querySelectorAll('.panel')].map((el) => ({ el, stop: +el.dataset.stop, videos: [...el.querySelectorAll('video')], vis: -1 }));
const navLinks = [...document.querySelectorAll('[data-goto]')];
const placeName = document.getElementById('place-name');
const placeMeta = document.getElementById('place-meta');
const floorsEl = document.getElementById('floors');
const floorBars = PLACES.map(() => { const i = document.createElement('i'); floorsEl.prepend(i); return i; });
let currentPlace = -1;

// vídeos de los paneles: controles de play / pausa, progreso y sonido (video.js)
document.querySelectorAll('.panel video').forEach(setupVideo);

// vistas de detalle: cada sección se abre a pantalla completa (detail.js)
const SECTION_STOP = { motion: 1, works: 2, built: 3, architect: 4, vienna: 5, world: 6, about: 7 };
const detailView = initDetail({
  onOpen: () => { lenis.stop(); panels.forEach((p) => playVideos(p, false)); },
  onClose: () => { lenis.start(); panels.forEach((p) => { if (p.vis > 0.6) playVideos(p, true); }); },
});

// al llegar a una parada, sus vídeos arrancan en silencio (salvo que el usuario los haya pausado)
function playVideos(p, on) {
  for (const v of p.videos) {
    if (on) {
      ensureLoaded(v);
      if (v.paused && !v.dataset.userPaused) v.play().catch(() => {});
    } else if (!v.paused) v.pause();
  }
}

function updateUI(s) {
  for (const p of panels) {
    const d = s - p.stop;
    const vis = clamp01(1 - Math.abs(d) * 3.2);
    if (Math.abs(vis - p.vis) < 0.001) continue;
    p.el.style.opacity = vis.toFixed(3);
    p.el.style.setProperty('--shift', `${(-d * 80).toFixed(1)}px`);
    p.el.classList.toggle('is-on', vis > 0.01);
    p.el.style.pointerEvents = vis > 0.6 ? 'auto' : 'none';
    if (vis > 0.6 && p.vis <= 0.6) playVideos(p, true);
    if (vis < 0.2 && p.vis >= 0.2) playVideos(p, false);
    p.vis = vis;
  }
  const nearest = Math.round(s);
  if (nearest !== currentPlace) {
    currentPlace = nearest;
    placeName.textContent = PLACES[nearest][0];
    placeMeta.textContent = PLACES[nearest][1];
    navLinks.forEach((a) => a.classList.toggle('active', +a.dataset.goto === nearest && nearest > 0));
    floorBars.forEach((b, i) => b.classList.toggle('on', i <= nearest));
  }
  // indicador "scroll to start": solo mientras nadie ha empezado a moverse
  const atStart = lenis.scroll < 40;
  if (atStart !== wasAtStart) { document.body.classList.toggle('at-start', atStart); wasAtStart = atStart; }
}
let wasAtStart = true;

// ------------------------------------------------------------------ carga
const loaderEl = document.getElementById('loader');
const fillEl = document.getElementById('loader-fill');
const pctEl = document.getElementById('loader-pct');
const setPct = (p) => { fillEl.style.width = `${p}%`; pctEl.textContent = String(Math.round(p)).padStart(3, '0'); };

const draco = new DRACOLoader().setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.169.0/examples/jsm/libs/draco/gltf/');
const gltfLoader = new GLTFLoader().setDRACOLoader(draco);

let wheelPivot = null;
const gondolas = [];            // { mesh, base: [ángulos] }
const landmarks = [];           // { name, stop, mats: [uStrength], peak }

function ownerOf(o) {
  let p = o;
  while (p) { if (p.name in FOCUS_STOP) return p.name; p = p.parent; }
  return null;
}

async function init() {
  const [path, gltf] = await Promise.all([
    fetch(new URL('camera_path.json', import.meta.url)).then((r) => r.json()),
    gltfLoader.loadAsync(new URL('city.glb', import.meta.url).href, (e) => { if (e.total) setPct((e.loaded / e.total) * 90); }),
  ]);
  keyCount = path.keys.length;
  camCurve = new THREE.CatmullRomCurve3(path.keys.map((k) => B2T(k.cam)), false, 'centripetal');
  tgtCurve = new THREE.CatmullRomCurve3(path.keys.map((k) => B2T(k.tgt)), false, 'centripetal');
  stopKeys = path.keys.map((k, i) => (k.stop ? i : -1)).filter((i) => i >= 0);
  stopCount = stopKeys.length;

  const city = gltf.scene;
  const lmMats = new Map();     // monumento -> { paper, roof, bulbs }
  const matsFor = (name) => {
    if (!lmMats.has(name)) {
      const isWheel = name === 'RR_Root';
      const base = LIGHT.lmBase;
      const set = { paper: light2(base), roof: light2(base, { roof: true }), bulbs: isWheel ? light2(base, { bulbs: true }) : null };
      lmMats.set(name, set);
      landmarks.push({ name, stop: FOCUS_STOP[name], uniforms: [set.paper, set.roof, set.bulbs].filter(Boolean).map((m) => m.userData.uStrength), peak: PEAK[name] ?? 1.3 });
    }
    return lmMats.get(name);
  };
  city.traverse((o) => {
    if (!o.isMesh) return;
    const name = o.material?.name || '';
    const owner = ownerOf(o);
    let inPivot = false; for (let p = o.parent; p; p = p.parent) if (p.name === 'RR_WheelPivot') inPivot = true;
    let inBlocks = false, inTrees = false;
    for (let p = o.parent; p; p = p.parent) { if (p.name.startsWith('CITY_BLOCKS')) inBlocks = true; if (p.name.startsWith('CITY_TREES')) inTrees = true; }
    if (FLAT[name]) o.material = FLAT[name];
    else if (inTrees) o.material = name === 'Ink' ? INK_DARK : TREE_LIGHT;
    else if (inBlocks) o.material = name === 'Ink' ? BLOCK_WINDOWS : name === 'Roof' ? BLOCK_ROOF : BLOCK_LIGHT;
    else if (owner) {
      const set = matsFor(owner);
      if (owner === 'RR_Root' && name === 'Ink') o.material = inPivot ? set.bulbs : set.paper;   // acero del Riesenrad
      else if (name === 'Ink') o.material = INK_DARK;                                              // huecos y ventanas: negro
      else o.material = name === 'Roof' ? set.roof : set.paper;                                   // Paper, Roof, "Light 2"
    } else o.material = BLOCK_LIGHT;
    if (o.isInstancedMesh) o.frustumCulled = false;
  });
  scene.add(city);

  // halos: detrás de cada monumento, más fuertes cuando es la parada activa
  city.updateMatrixWorld(true);
  for (const lm of landmarks) {
    const obj = city.getObjectByName(lm.name);
    const box = new THREE.Box3().setFromObject(obj);
    const size = box.getSize(new THREE.Vector3());
    const c = box.getCenter(new THREE.Vector3());
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: haloTex, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, opacity: 0 }));
    const sc = Math.max(size.x, size.y, size.z) * 1.7;
    sp.scale.set(sc, sc, 1);
    sp.position.copy(c);
    sp.renderOrder = 3;
    scene.add(sp);
    halos.push({ sprite: sp, lm });
  }

  // Riesenrad: pivote que gira y vagones instanciados que cuelgan siempre verticales
  wheelPivot = city.getObjectByName('RR_WheelPivot');
  city.getObjectByName('RR_Root')?.traverse((o) => {
    if (o.isInstancedMesh && o.count === 15) {
      const m = new THREE.Matrix4(), p = new THREE.Vector3(), base = [];
      for (let i = 0; i < o.count; i++) { o.getMatrixAt(i, m); p.setFromMatrixPosition(m); base.push(Math.atan2(p.y - HUB_Y, p.x)); }
      gondolas.push({ mesh: o, base });
    }
  });

  buildTrails();
  resize();
  window.scrollTo(0, 0);
  lenis.scrollTo(0, { immediate: true, force: true });
  sampleAt(0);
  camPos.copy(wantPos).add(new THREE.Vector3(-110, 70, 40));   // entrada: llega al hero desde lejos
  camTgt.copy(wantTgt);
  setPct(100);
  setTimeout(() => loaderEl.classList.add('done'), 250);
  lenis.start();
  const [deep, sub] = decodeURIComponent(location.hash.slice(1)).split('/');
  if (deep in SECTION_STOP) {
    // la entrada base queda sin hash: así "atrás" cierra la sección y vuelve a la ciudad
    history.replaceState(null, '', location.pathname + location.search);
    lenis.scrollTo(stopY(SECTION_STOP[deep]), { immediate: true, force: true });
    sampleAt(stopY(SECTION_STOP[deep]));
    camPos.copy(wantPos); camTgt.copy(wantTgt);
    setTimeout(() => detailView.open(deep, null, sub), 600);
  }
}

// ------------------------------------------------------------------ scroll + bucle
const lenis = new Lenis({ duration: 1.25, smoothWheel: true, wheelMultiplier: 0.9, touchMultiplier: 1.4 });
lenis.stop();
navLinks.forEach((a) => a.addEventListener('click', (e) => { e.preventDefault(); lenis.scrollTo(stopY(+a.dataset.goto), { duration: 2.6 }); }));
document.getElementById('scroll-cue').addEventListener('click', () => lenis.scrollTo(stopY(1), { duration: 2.6 }));
document.getElementById('skip').addEventListener('click', () => {
  const next = Math.min(Math.floor(lenis.scroll / (SEG * innerHeight) + 0.02) + 1, stopCount - 1);
  lenis.scrollTo(stopY(next), { duration: 2.4 });
});

const pointer = new THREE.Vector2();
addEventListener('pointermove', (e) => pointer.set((e.clientX / innerWidth) * 2 - 1, (e.clientY / innerHeight) * 2 - 1));
addEventListener('resize', resize);
// enlace con hash con la página ya abierta (p. ej. #works/puntigamer): abre la sección.
// Si la vista ya está abierta, quien manda es popstate (atrás / adelante).
addEventListener('hashchange', () => {
  const [key, sub] = decodeURIComponent(location.hash.slice(1)).split('/');
  if (!(key in SECTION_STOP) || detailView.isOpen() || !camCurve) return;
  history.replaceState(null, '', location.pathname + location.search);
  lenis.scrollTo(stopY(SECTION_STOP[key]), { immediate: true, force: true });
  detailView.open(key, null, sub);
});
// al volver con atrás/adelante desde otra página (caché del navegador), el scroll sigue vivo
addEventListener('pageshow', (e) => { if (e.persisted && !detailView.isOpen()) lenis.start(); });

const clock = new THREE.Clock();
let wheelAngle = 0, ca = 0;
const up = new THREE.Vector3(0, 1, 0), right = new THREE.Vector3(), tmpM = new THREE.Matrix4(), prevPos = new THREE.Vector3();
let slowFrames = 0, frames = 0;

function frame(time) {
  const dt = Math.min(clock.getDelta(), 0.05);
  TIME.value += dt;
  lenis.raf(time);
  if (camCurve) {
    const s = sampleAt(lenis.scroll);
    right.subVectors(wantTgt, wantPos).cross(up).normalize();
    wantPos.addScaledVector(right, pointer.x * 2.5).addScaledVector(up, -pointer.y * 1.4);
    const k = 1 - Math.exp(-dt * 4.2);
    prevPos.copy(camPos);
    camPos.lerp(wantPos, k);
    camTgt.lerp(wantTgt, k);
    camera.position.copy(camPos);
    camera.lookAt(camTgt);

    // foco: el monumento de la parada activa sube su Light 2 y su halo; al final se encienden todos
    const finale = smooth(6.4, 7.0, s);
    for (const lm of landmarks) {
      const f = Math.pow(clamp01(1 - Math.abs(s - lm.stop) * 1.15), 1.6);
      const target = Math.max(LIGHT.lmBase + (lm.peak - LIGHT.lmBase) * f, LIGHT.lmBase + (LIGHT.lmFinale - LIGHT.lmBase) * finale);
      for (const u of lm.uniforms) u.value += (target - u.value) * (1 - Math.exp(-dt * 3));
      lm.focus = f;
    }
    for (const h of halos) h.sprite.material.opacity = 0.02 + 0.14 * (h.lm.focus || 0) + 0.06 * finale;

    updateUI(s);

    // Riesenrad: una vuelta cada 255 s, como el real
    wheelAngle += dt * (Math.PI * 2 / 255);
    if (wheelPivot) wheelPivot.rotation.z = wheelAngle;
    for (const g of gondolas) {
      for (let i = 0; i < g.base.length; i++) {
        const a = g.base[i] + wheelAngle;
        tmpM.makeTranslation(WHEEL_R * Math.cos(a), HUB_Y + WHEEL_R * Math.sin(a), 0);
        g.mesh.setMatrixAt(i, tmpM);
      }
      g.mesh.instanceMatrix.needsUpdate = true;
    }

    dust.uniforms.uCam.value.copy(camPos);
    const speed = prevPos.distanceTo(camPos) / Math.max(dt, 1e-3);
    ca += (clamp01(speed / 90) - ca) * (1 - Math.exp(-dt * 6));
    film.uniforms.uCA.value = 0.1 + ca * 0.85;
    film.uniforms.uTime.value = TIME.value;
    composer.render(dt);

    frames++;
    if (frames > 90 && dt > 1 / 36) slowFrames++;
    if (slowFrames > 60 && DPR > 1) { DPR = 1; resize(); slowFrames = -9999; }
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

init().catch((err) => {
  console.error(err);
  pctEl.textContent = 'ERR';
  document.querySelector('#loader .mono').textContent = '/ ' + err.message;
});
