// === GRAPH STATE ===
let vertices = [];
let adj = [];  // adjacency list: adj[i] = [{to, dist}]
let totalV = 0, totalE = 0;

// === VIEWPORT ===
let camX = 0, camY = 0, camScale = 1;
let dragging = false, dragStart = null, camStart = null;

// === SELECTION STATE ===
let originV = -1, destV = -1;
let pathNodes = [], pathSet = new Set();
let exploredCount = 0;
let addEdgeFirst = -1;

// === MODE ===
let mode = 'origin'; // origin | dest | add-vertex | add-edge | delete | pan
let showLabelV = false, showLabelE = false;

// === DISPLAY PARAMS ===
let vertexSize = 1.5, edgeWidth = 0.5;

// === CANVAS ===
const wrap = document.getElementById('canvas-wrap');
const canvas = document.getElementById('c');
const ctx = canvas.getContext('2d');
const tooltip = document.getElementById('tooltip');

function log(msg, cls='info'){
  const d = document.createElement('div');
  d.className = `log-entry ${cls}`;
  d.textContent = `> ${msg}`;
  const log = document.getElementById('log');
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}
function setStatus(s){document.getElementById('status').textContent = s;}

// === INIT ===
function initGraph(){
  const v = GRAPH_DATA.v;
  const e = GRAPH_DATA.e;
  totalV = v.length;
  adj = Array.from({length: totalV}, ()=>[]);
  vertices = v.map(([id, x, y]) => ({id, x, y, label: String(id)}));

  for(const [src, dst, dir] of e){
    const d = dist(vertices[src], vertices[dst]);
    adj[src].push({to: dst, dist: d});
    if(dir === 0) adj[dst].push({to: src, dist: d});
    totalE += dir === 0 ? 1 : 1;
  }
  // Recalculate totalE properly
  totalE = e.length;
  
  document.getElementById('hdr-stats').textContent = `V:${totalV} E:${totalE}`;
  log(`Grafo carregado: ${totalV} vÃ©rtices, ${totalE} arestas`, 'ok');
  
  // Fit to screen
  fitToScreen();
  render();
}

function dist(a, b){
  return Math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2);
}

function fitToScreen(){
  if(vertices.length===0) return;
  let minX=Infinity,maxX=-Infinity,minY=Infinity,maxY=-Infinity;
  for(const v of vertices){
    if(v.x<minX)minX=v.x; if(v.x>maxX)maxX=v.x;
    if(v.y<minY)minY=v.y; if(v.y>maxY)maxY=v.y;
  }
  const pw = wrap.clientWidth, ph = wrap.clientHeight;
  const gw = maxX-minX||1, gh = maxY-minY||1;
  camScale = Math.min(pw/gw, ph/gh) * 0.9;
  camX = (pw - gw*camScale)/2 - minX*camScale;
  camY = (ph - gh*camScale)/2 - minY*camScale;
}

// === COORDINATE TRANSFORMS ===
function toScreen(vx, vy){ return [vx*camScale+camX, vy*camScale+camY]; }
function toWorld(sx, sy){ return [(sx-camX)/camScale, (sy-camY)/camScale]; }

// === FIND NEAREST VERTEX ===
function findNearest(sx, sy, maxScreenDist=15){
  const [wx, wy] = toWorld(sx, sy);
  let best = -1, bestD = Infinity;
  for(let i=0; i<vertices.length; i++){
    const v = vertices[i];
    const d2 = (v.x-wx)**2 + (v.y-wy)**2;
    if(d2 < bestD){ bestD=d2; best=i; }
  }
  if(best >= 0){
    const [sx2,sy2] = toScreen(vertices[best].x, vertices[best].y);
    const sd = Math.sqrt((sx-sx2)**2+(sy-sy2)**2);
    if(sd <= maxScreenDist) return best;
  }
  return -1;
}

// === DIJKSTRA ===
function dijkstra(start, end){
  const t0 = performance.now();
  const INF = Infinity;
  const dist_arr = new Float64Array(totalV).fill(INF);
  const prev = new Int32Array(totalV).fill(-1);
  const visited = new Uint8Array(totalV);
  dist_arr[start] = 0;
  
  // Min-heap (priority queue)
  // Simple binary heap implementation
  const heap = [[0, start]];
  let explored = 0;

  while(heap.length > 0){
    const [d, u] = heapPop(heap);
    if(visited[u]) continue;
    visited[u] = 1;
    explored++;
    if(u === end) break;
    for(const {to, dist:w} of adj[u]){
      if(!visited[to]){
        const nd = d + w;
        if(nd < dist_arr[to]){
          dist_arr[to] = nd;
          prev[to] = u;
          heapPush(heap, [nd, to]);
        }
      }
    }
  }
  
  const t1 = performance.now();
  exploredCount = explored;
  
  if(dist_arr[end] === INF) return {path:[], dist:INF, time:t1-t0, explored};
  
  const path = [];
  for(let v=end; v!==-1; v=prev[v]) path.push(v);
  path.reverse();
  return {path, dist: dist_arr[end], time:t1-t0, explored};
}

// Min-heap helpers
function heapPush(h, item){
  h.push(item);
  let i = h.length-1;
  while(i>0){
    const parent = (i-1)>>1;
    if(h[parent][0] <= h[i][0]) break;
    [h[parent],h[i]]=[h[i],h[parent]];
    i = parent;
  }
}
function heapPop(h){
  const top = h[0];
  const last = h.pop();
  if(h.length>0){
    h[0]=last;
    let i=0;
    while(true){
      let min=i, l=2*i+1, r=2*i+2;
      if(l<h.length && h[l][0]<h[min][0]) min=l;
      if(r<h.length && h[r][0]<h[min][0]) min=r;
      if(min===i) break;
      [h[min],h[i]]=[h[i],h[min]];
      i=min;
    }
  }
  return top;
}

// === RENDER ===
function resize(){
  canvas.width = wrap.clientWidth;
  canvas.height = wrap.clientHeight;
  render();
}

function render(){
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0,0,W,H);
  
  // Background
  ctx.fillStyle = '#0a0f1a';
  ctx.fillRect(0,0,W,H);
  
  // Clip
  const pad = 50;
  
  // Draw edges
  ctx.lineWidth = edgeWidth;
  
  for(let u=0; u<vertices.length; u++){
    const v = vertices[u];
    const [sx, sy] = toScreen(v.x, v.y);
    if(sx < -100 || sx > W+100 || sy < -100 || sy > H+100) continue;
    
    for(const {to, dist:w} of adj[u]){
      if(to < u) continue; // draw each edge once
      const vt = vertices[to];
      const [tx, ty] = toScreen(vt.x, vt.y);
      
      // Color: path edge = cyan, normal = dark blue
      const isPath = pathSet.has(u) && pathSet.has(to) && 
        isConsecutiveInPath(u, to);
      
      ctx.strokeStyle = isPath ? '#00d4ff' : '#1a2e4a';
      ctx.lineWidth = isPath ? Math.max(2, edgeWidth*2) : edgeWidth;
      ctx.beginPath();
      ctx.moveTo(sx, sy);
      ctx.lineTo(tx, ty);
      ctx.stroke();
      
      if(showLabelE && camScale > 0.2){
        const mx = (sx+tx)/2, my = (sy+ty)/2;
        ctx.fillStyle = '#304050';
        ctx.font = `${Math.max(8, camScale*8)}px monospace`;
        ctx.fillText(w.toFixed(1), mx, my);
      }
    }
  }
  
  // Draw vertices
  for(let i=0; i<vertices.length; i++){
    const v = vertices[i];
    const [sx, sy] = toScreen(v.x, v.y);
    if(sx < -10 || sx > W+10 || sy < -10 || sy > H+10) continue;
    
    let color = '#1a3a5a';
    let r = vertexSize;
    
    if(i === originV){ color = '#4ad48a'; r = Math.max(4, vertexSize*2); }
    else if(i === destV){ color = '#d45a4a'; r = Math.max(4, vertexSize*2); }
    else if(pathSet.has(i)){ color = '#00d4ff'; r = Math.max(2.5, vertexSize*1.5); }
    
    if(r < 0.3) continue; // too small to see
    
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.arc(sx, sy, r, 0, Math.PI*2);
    ctx.fill();
    
    if(showLabelV && camScale > 0.3 && r > 1){
      ctx.fillStyle = '#8aa0b0';
      ctx.font = `${Math.max(8, r*2.5)}px monospace`;
      ctx.fillText(v.id, sx+r+2, sy+3);
    }
  }
  
  // Origin/dest markers
  if(originV >= 0) drawMarker(originV, '#4ad48a', 'O');
  if(destV >= 0) drawMarker(destV, '#d45a4a', 'D');
}

function drawMarker(idx, color, label){
  const v = vertices[idx];
  const [sx, sy] = toScreen(v.x, v.y);
  const r = Math.max(6, vertexSize*3);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(sx, sy, r, 0, Math.PI*2);
  ctx.stroke();
  ctx.fillStyle = color;
  ctx.font = `bold ${Math.max(10, r*1.5)}px monospace`;
  ctx.fillText(label, sx - r*0.3, sy + r*0.4);
}

function isConsecutiveInPath(a, b){
  for(let i=0; i<pathNodes.length-1; i++){
    if((pathNodes[i]===a && pathNodes[i+1]===b)||
       (pathNodes[i]===b && pathNodes[i+1]===a)) return true;
  }
  return false;
}

// === EVENT HANDLERS ===
wrap.addEventListener('mousedown', e => {
  if(mode === 'pan' || e.button === 1){
    dragging = true;
    dragStart = {x: e.clientX, y: e.clientY};
    camStart = {x: camX, y: camY};
    wrap.style.cursor = 'grabbing';
    return;
  }
  
  const rect = wrap.getBoundingClientRect();
  const sx = e.clientX - rect.left;
  const sy = e.clientY - rect.top;
  
  if(mode === 'origin'){
    const v = findNearest(sx, sy);
    if(v >= 0){ originV = v; log(`Origem: vÃ©rtice ${v}`, 'ok'); }
    else { const [wx,wy]=toWorld(sx,sy); log(`Nenhum vÃ©rtice prÃ³ximo (${wx.toFixed(0)}, ${wy.toFixed(0)})`,'warn'); }
  } else if(mode === 'dest'){
    const v = findNearest(sx, sy);
    if(v >= 0){ destV = v; log(`Destino: vÃ©rtice ${v}`, 'ok'); }
  } else if(mode === 'add-vertex'){
    const [wx,wy] = toWorld(sx, sy);
    const nid = vertices.length;
    vertices.push({id: nid, x: wx, y: wy, label: String(nid)});
    adj.push([]);
    totalV++;
    log(`VÃ©rtice ${nid} adicionado em (${wx.toFixed(1)}, ${wy.toFixed(1)})`, 'ok');
  } else if(mode === 'add-edge'){
    const v = findNearest(sx, sy, 20);
    if(v >= 0){
      if(addEdgeFirst < 0){ addEdgeFirst = v; log(`Aresta: primeiro vÃ©rtice = ${v}`, 'info'); }
      else {
        const d = dist(vertices[addEdgeFirst], vertices[v]);
        adj[addEdgeFirst].push({to:v, dist:d});
        adj[v].push({to:addEdgeFirst, dist:d});
        totalE++;
        log(`Aresta ${addEdgeFirst}â†”${v} adicionada (dist=${d.toFixed(1)})`, 'ok');
        addEdgeFirst = -1;
      }
    }
  } else if(mode === 'delete'){
    const v = findNearest(sx, sy, 20);
    if(v >= 0){
      vertices[v] = {...vertices[v], deleted: true};
      adj[v] = [];
      for(let i=0; i<adj.length; i++) adj[i] = adj[i].filter(e=>e.to!==v);
      log(`VÃ©rtice ${v} removido`, 'warn');
      if(originV===v) originV=-1;
      if(destV===v) destV=-1;
    }
  }
  
  document.getElementById('st-orig').textContent = originV >= 0 ? originV : 'â€”';
  document.getElementById('st-dest').textContent = destV >= 0 ? destV : 'â€”';
  document.getElementById('hdr-mode').textContent = `MODO: ${mode.toUpperCase()}`;
  render();
});

wrap.addEventListener('mousemove', e => {
  if(dragging){
    camX = camStart.x + (e.clientX - dragStart.x);
    camY = camStart.y + (e.clientY - dragStart.y);
    render();
    return;
  }
  
  const rect = wrap.getBoundingClientRect();
  const sx = e.clientX - rect.left;
  const sy = e.clientY - rect.top;
  const v = findNearest(sx, sy, 12);
  
  if(v >= 0){
    const vx = vertices[v];
    tooltip.style.display = 'block';
    tooltip.style.left = (sx+12)+'px';
    tooltip.style.top = (sy-10)+'px';
    const neighbors = adj[v].length;
    tooltip.innerHTML = `ID: ${vx.id}<br>x: ${vx.x.toFixed(1)}, y: ${vx.y.toFixed(1)}<br>Vizinhos: ${neighbors}`;
  } else {
    tooltip.style.display = 'none';
  }
  
  setStatus(`Cursor: (${((sx-camX)/camScale).toFixed(0)}, ${((sy-camY)/camScale).toFixed(0)}) | Zoom: ${(camScale*100).toFixed(0)}%`);
});

wrap.addEventListener('mouseup', () => {
  dragging = false;
  wrap.style.cursor = mode === 'pan' ? 'grab' : 'crosshair';
});

wrap.addEventListener('wheel', e => {
  e.preventDefault();
  const rect = wrap.getBoundingClientRect();
  const mx = e.clientX - rect.left;
  const my = e.clientY - rect.top;
  const factor = e.deltaY < 0 ? 1.15 : 1/1.15;
  const newScale = Math.max(0.01, Math.min(50, camScale * factor));
  camX = mx - (mx - camX) * newScale / camScale;
  camY = my - (my - camY) * newScale / camScale;
  camScale = newScale;
  render();
}, {passive: false});

// === BUTTONS ===
function setMode(m){
  mode = m;
  addEdgeFirst = -1;
  document.querySelectorAll('.mode-btn').forEach(b=>b.classList.remove('active'));
  const btnMap = {'origin':'btn-orig','dest':'btn-dest','add-vertex':'btn-add-v',
                  'add-edge':'btn-add-e','delete':'btn-del','pan':'btn-pan'};
  const btn = document.getElementById(btnMap[m]);
  if(btn) btn.classList.add('active');
  wrap.style.cursor = m === 'pan' ? 'grab' : 'crosshair';
  document.getElementById('hdr-mode').textContent = `MODO: ${m.toUpperCase()}`;
}

document.getElementById('btn-orig').onclick = ()=>setMode('origin');
document.getElementById('btn-dest').onclick = ()=>setMode('dest');
document.getElementById('btn-add-v').onclick = ()=>setMode('add-vertex');
document.getElementById('btn-add-e').onclick = ()=>setMode('add-edge');
document.getElementById('btn-del').onclick = ()=>setMode('delete');
document.getElementById('btn-pan').onclick = ()=>setMode('pan');

document.getElementById('btn-clear').onclick = ()=>{
  originV=-1; destV=-1; pathNodes=[]; pathSet=new Set();
  document.getElementById('st-orig').textContent='â€”';
  document.getElementById('st-dest').textContent='â€”';
  document.getElementById('st-dist').textContent='â€”';
  document.getElementById('st-explored').textContent='â€”';
  document.getElementById('st-path').textContent='â€”';
  document.getElementById('st-time').textContent='â€”';
  log('SeleÃ§Ã£o limpa','warn');
  render();
};

document.getElementById('btn-dijkstra').onclick = runDijkstra;

document.getElementById('btn-lbl-v').onclick = function(){
  showLabelV=!showLabelV;
  this.classList.toggle('active',showLabelV);
  render();
};
document.getElementById('btn-lbl-e').onclick = function(){
  showLabelE=!showLabelE;
  this.classList.toggle('active',showLabelE);
  render();
};

document.getElementById('sz-v').oninput = function(){
  vertexSize = parseFloat(this.value);
  document.getElementById('sz-v-lbl').textContent = this.value;
  render();
};
document.getElementById('sz-e').oninput = function(){
  edgeWidth = parseFloat(this.value);
  document.getElementById('sz-e-lbl').textContent = this.value;
  render();
};

document.getElementById('btn-go-id').onclick = ()=>{
  const id = parseInt(document.getElementById('go-id').value);
  if(id >= 0 && id < vertices.length){
    const v = vertices[id];
    const [sx,sy] = toScreen(v.x, v.y);
    const cx = wrap.clientWidth/2, cy = wrap.clientHeight/2;
    camX += cx - sx;
    camY += cy - sy;
    render();
    log(`Centralizando em vÃ©rtice ${id}`,'info');
  }
};

document.getElementById('btn-copy').onclick = ()=>{
  canvas.toBlob(blob => {
    const item = new ClipboardItem({'image/png': blob});
    navigator.clipboard.write([item]).then(()=>log('Imagem copiada!','ok')).catch(()=>log('Erro ao copiar','err'));
  });
};

// === KEYBOARD ===
document.addEventListener('keydown', e => {
  if(e.target.tagName==='INPUT') return;
  if(e.key==='o'||e.key==='O') setMode('origin');
  else if(e.key==='d'||e.key==='D') setMode('dest');
  else if(e.key==='c'||e.key==='C') runDijkstra();
  else if(e.key==='p'||e.key==='P') setMode('pan');
  else if(e.key==='f'||e.key==='F') fitToScreen(), render();
  else if(e.key==='+') { camScale*=1.2; render(); }
  else if(e.key==='-') { camScale/=1.2; render(); }
});

function runDijkstra(){
  if(originV < 0 || destV < 0){
    log('Defina origem (O) e destino (D) primeiro','err');
    return;
  }
  if(originV === destV){
    log('Origem e destino sÃ£o iguais','warn');
    return;
  }
  
  log(`Calculando rota ${originV} â†’ ${destV}...`,'info');
  setStatus('Executando Dijkstra...');
  
  setTimeout(()=>{
    const result = dijkstra(originV, destV);
    
    if(result.path.length === 0){
      log(`Sem caminho entre ${originV} e ${destV}`,'err');
      setStatus('Sem caminho encontrado.');
      return;
    }
    
    pathNodes = result.path;
    pathSet = new Set(pathNodes);
    
    document.getElementById('st-dist').textContent = result.dist.toFixed(2) + ' u.';
    document.getElementById('st-explored').textContent = result.explored;
    document.getElementById('st-path').textContent = pathNodes.length;
    document.getElementById('st-time').textContent = result.time.toFixed(1);
    
    log(`Rota encontrada! ${pathNodes.length} nÃ³s, distÃ¢ncia: ${result.dist.toFixed(1)} u.`,'ok');
    log(`NÃ³s explorados: ${result.explored} | Tempo: ${result.time.toFixed(1)}ms`,'info');
    log(`Caminho: ${pathNodes.slice(0,8).join('â†’')}${pathNodes.length>8?'...':''}`, 'ok');
    
    setStatus(`Rota traÃ§ada: ${pathNodes.length} vÃ©rtices, dist. ${result.dist.toFixed(1)} u. | Tempo: ${result.time.toFixed(1)}ms`);
    render();
  }, 10);
}

// === RESIZE ===
new ResizeObserver(resize).observe(wrap);

// === START ===
window.addEventListener('load', ()=>{
  resize();
  initGraph();
  setMode('origin');
});