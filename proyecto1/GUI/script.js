const CFG_KEY = 'edificio_iot_cfg';

function loadConfig(){
  try{ return JSON.parse(localStorage.getItem(CFG_KEY)) || {}; }catch(e){ return {}; }
}

function toggleConfig(){
  document.getElementById('configPanel').classList.toggle('open');
}

function fillConfigForm(cfg){
  document.getElementById('cfg-mqtt-url').value = cfg.mqttUrl || '';
  document.getElementById('cfg-mqtt-user').value = cfg.mqttUser || '';
  document.getElementById('cfg-mqtt-pass').value = cfg.mqttPass || '';
  document.getElementById('cfg-mqtt-prefix').value = cfg.prefix || 'edificio';
  document.getElementById('cfg-mongo-url').value = cfg.mongoUrl || '';
  document.getElementById('cfg-mongo-key').value = cfg.mongoKey || '';
  document.getElementById('cfg-mongo-source').value = cfg.mongoSource || '';
  document.getElementById('cfg-mongo-db').value = cfg.mongoDb || '';
}

function saveConfig(){
  const cfg = {
    mqttUrl: document.getElementById('cfg-mqtt-url').value.trim(),
    mqttUser: document.getElementById('cfg-mqtt-user').value.trim(),
    mqttPass: document.getElementById('cfg-mqtt-pass').value,
    prefix: document.getElementById('cfg-mqtt-prefix').value.trim() || 'edificio',
    mongoUrl: document.getElementById('cfg-mongo-url').value.trim(),
    mongoKey: document.getElementById('cfg-mongo-key').value.trim(),
    mongoSource: document.getElementById('cfg-mongo-source').value.trim(),
    mongoDb: document.getElementById('cfg-mongo-db').value.trim(),
  };
  localStorage.setItem(CFG_KEY, JSON.stringify(cfg));
  toggleConfig();
  connectMqtt(cfg);
  refreshHistorial(cfg);
  clearInterval(window._histInterval);
  window._histInterval = setInterval(()=>refreshHistorial(cfg), 15000);
}

/*GRAFICAS*/
function makeChart(ctx,label,color){
  return new Chart(ctx,{
    type:'line',
    data:{labels:[],datasets:[{label,data:[],borderColor:color,backgroundColor:color+'33',tension:.3,pointRadius:0,borderWidth:2}]},
    options:{
      responsive:true,maintainAspectRatio:false,
      animation:false,
      scales:{
        x:{ticks:{color:'#7FA1BC',maxTicksLimit:6},grid:{color:'#1D4867'}},
        y:{ticks:{color:'#7FA1BC'},grid:{color:'#1D4867'}}
      },
      plugins:{legend:{labels:{color:'#E7F1F8'}}}
    }
  });
}

const charts = {
  temp: makeChart(document.getElementById('chartTemp'),'Temperatura (°C)','#F87171'),
  hum: makeChart(document.getElementById('chartHum'),'Humedad (%)','#4FC3E0'),
  gas: makeChart(document.getElementById('chartGas'),'Gas / Humo','#FBBF24'),
  dist: makeChart(document.getElementById('chartDist'),'Distancia (cm)','#4ADE80'),
  luz: makeChart(document.getElementById('chartLuz'),'Nivel de luz','#C084FC'),
  arm: makeChart(document.getElementById('chartArm'),'Promedio ARM64','#4FC3E0'),
};

function pushPoint(chart,value){
  const now = new Date().toLocaleTimeString();
  chart.data.labels.push(now);
  chart.data.datasets[0].data.push(value);
  if(chart.data.labels.length>40){ chart.data.labels.shift(); chart.data.datasets[0].data.shift(); }
  chart.update('none');
}

/*MQTT — conexión por WebSocket a EMQX*/
let mqttClient = null;

function setConn(on,text){
  document.getElementById('connDot').classList.toggle('on',on);
  document.getElementById('connText').textContent = text;
}

function connectMqtt(cfg){
  if(!cfg.mqttUrl){ setConn(false,'Falta configurar MQTT'); return; }
  if(mqttClient){ mqttClient.end(true); }
  setConn(false,'Conectando…');
  mqttClient = mqtt.connect(cfg.mqttUrl,{
    username: cfg.mqttUser || undefined,
    password: cfg.mqttPass || undefined,
    reconnectPeriod: 4000,
  });
  const p = cfg.prefix;
  mqttClient.on('connect',()=>{
    setConn(true,'MQTT conectado');
    [
      `${p}/sensores/temperatura`, `${p}/sensores/humedad`, `${p}/sensores/gas`,
      `${p}/sensores/distancia`, `${p}/sensores/luz`,
      `${p}/actuadores/puerta`, `${p}/actuadores/luces`, `${p}/actuadores/ventilador`, `${p}/actuadores/alarma`,
      `${p}/estado/global`, `${p}/arm64/resultados`
    ].forEach(t=>mqttClient.subscribe(t));
  });
  mqttClient.on('reconnect',()=>setConn(false,'Reconectando…'));
  mqttClient.on('close',()=>setConn(false,'MQTT desconectado'));
  mqttClient.on('error',err=>setConn(false,'Error MQTT: '+err.message));
  mqttClient.on('message',(topic,message)=>{
    const text = message.toString();
    let val = text;
    try{ val = JSON.parse(text); }catch(e){ }
    handleMessage(topic.replace(p+'/',''), val, text);
  });
}

function num(v){
  if(typeof v === 'object' && v !== null) return Number(v.value ?? v.valor ?? v.temperatura ?? v.data);
  return Number(v);
}

function handleMessage(subtopic, val, raw){
  switch(subtopic){
    case 'sensores/temperatura':
      set('r-temp',num(val)); set('z-temp',num(val)+' °C'); pushPoint(charts.temp,num(val)); break;
    case 'sensores/humedad':
      set('r-hum',num(val)); set('z-hum',num(val)+' %'); pushPoint(charts.hum,num(val)); break;
    case 'sensores/gas':
      set('r-gas',num(val)); set('z-gas',num(val)); pushPoint(charts.gas,num(val)); break;
    case 'sensores/distancia':
      set('r-dist',num(val)); set('z-dist',num(val)+' cm'); pushPoint(charts.dist,num(val)); break;
    case 'sensores/luz':
      set('r-luz',num(val)); set('z-luz',num(val)); pushPoint(charts.luz,num(val)); break;
    case 'actuadores/puerta':
      set('z-puerta', raw.toUpperCase().includes('ABI') ? 'ABIERTA' : 'CERRADA'); break;
    case 'actuadores/luces':
      set('z-luces', raw.toUpperCase().includes('ON') || raw.toUpperCase().includes('ENC') ? 'ENCENDIDAS' : 'APAGADAS'); break;
    case 'actuadores/ventilador':
      set('z-vent', raw.toUpperCase().includes('ON') || raw.toUpperCase().includes('ENC') ? 'ACTIVO' : 'INACTIVO'); break;
    case 'actuadores/alarma':
      set('z-alarma', raw.toUpperCase().includes('ON') || raw.toUpperCase().includes('ACTIVA') ? 'ACTIVA' : 'INACTIVA'); break;
    case 'estado/global':
      setGlobalStatus(raw.trim().toUpperCase()); break;
    case 'arm64/resultados':
      handleArmResult(val); break;
  }
}

function set(id,value){ const el=document.getElementById(id); if(el) el.textContent = value; }

function setGlobalStatus(state){
  const badge = document.getElementById('globalStatus');
  const valid = ['NORMAL','ADVERTENCIA','EMERGENCIA'];
  const s = valid.includes(state) ? state : 'NORMAL';
  badge.textContent = s;
  badge.className = 'status-badge '+s;
}

function handleArmResult(val){
  let avg;
  if(typeof val === 'object' && val !== null){
    avg = val.avg ?? val.AVG ?? val.promedio;
  } else {
    const str = String(val);
    avg = (str.match(/AVG=(-?\d+)/i)||[])[1];
  }
  if(avg !== undefined){ set('r-arm-avg',avg); pushPoint(charts.arm,Number(avg)); }
}

/*CONTROLES REMOTOS — publican al topic de comandos*/
function sendCmd(action,value){
  const cfg = loadConfig();
  if(!mqttClient || !mqttClient.connected){ alert('MQTT no está conectado. Revisá la configuración.'); return; }
  const topic = `${cfg.prefix}/control/remoto`;
  const payload = JSON.stringify({action, value, ts:new Date().toISOString()});
  mqttClient.publish(topic,payload);
}

/*MONGODB ATLAS DATA API — historial*/
async function dataApiFind(cfg, collection, limit=8, sortField='timestamp'){
  if(!cfg.mongoUrl || !cfg.mongoKey) return [];
  try{
    const res = await fetch(`${cfg.mongoUrl}/action/find`,{
      method:'POST',
      headers:{
        'Content-Type':'application/json',
        'api-key': cfg.mongoKey,
      },
      body: JSON.stringify({
        dataSource: cfg.mongoSource,
        database: cfg.mongoDb,
        collection,
        sort: {[sortField]: -1},
        limit,
      })
    });
    const json = await res.json();
    return json.documents || [];
  }catch(e){
    console.error('Data API error',collection,e);
    return [];
  }
}

function fillTable(id, docs, rowFn){
  const tbody = document.querySelector(`#${id} tbody`);
  tbody.innerHTML = docs.map(rowFn).join('') || `<tr><td colspan="2" style="color:var(--ink-muted);">Sin datos aún</td></tr>`;
}

async function refreshHistorial(cfg){
  const events = await dataApiFind(cfg,'events',8);
  fillTable('tblEvents', events, d=>`<tr><td>${fmtTs(d.timestamp)}</td><td>${d.tipo||d.type||d.mensaje||JSON.stringify(d).slice(0,40)}</td></tr>`);

  const commands = await dataApiFind(cfg,'commands',8);
  fillTable('tblCommands', commands, d=>`<tr><td>${fmtTs(d.timestamp||d.ts)}</td><td>${d.action||d.accion||''} → ${d.value||d.valor||''}</td></tr>`);

  const arm = await dataApiFind(cfg,'arm64_results',8);
  fillTable('tblArm', arm, d=>`<tr><td>${fmtTs(d.timestamp)}</td><td>${d.max ?? d.MAX ?? '-'} / ${d.min ?? d.MIN ?? '-'} / ${d.avg ?? d.AVG ?? '-'}</td></tr>`);
}

function fmtTs(ts){
  if(!ts) return '--';
  try{ return new Date(ts).toLocaleTimeString(); }catch(e){ return String(ts); }
}

/*INIT*/
window.addEventListener('DOMContentLoaded',()=>{
  const cfg = loadConfig();
  fillConfigForm(cfg);
  if(cfg.mqttUrl){ connectMqtt(cfg); } else { toggleConfig(); }
  refreshHistorial(cfg);
  window._histInterval = setInterval(()=>refreshHistorial(loadConfig()), 15000);
});
