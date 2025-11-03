// Simple demo app to simulate data and navigation.
// No backend — in-memory data only.

let state = {
  loggedIn: false,
  products: [],
  suppliers: [],
  batches: [],
  sales: [],
  currentProductId: null
};

// --- Sample data generator (kept small) ---
function seedData(){
  // suppliers
  state.suppliers = [
    {id:1, name:'Supplier A', lead_time_days:4},
    {id:2, name:'Supplier B', lead_time_days:7},
    {id:3, name:'Supplier C', lead_time_days:3}
  ];

  // products
  for(let i=1;i<=12;i++){
    state.products.push({
      id:i,
      name:`Product ${i}`,
      generic_name:`Generic ${i}`,
      unit: i%2? 'strip':'bottle',
      category: ['Painkiller','Antibiotic','Vitamin','Cough Syrup'][i%4]
    });
  }

  // batches: 3 per product
  let bid=1;
  const today = new Date();
  state.products.forEach(p=>{
    for(let j=0;j<3;j++){
      // expiry random 10-300 days ahead
      const days = Math.floor(Math.random()*290)+10;
      const expiry = new Date(today);
      expiry.setDate(today.getDate() + days);
      state.batches.push({
        batch_id: bid++,
        product_id: p.id,
        batch_no: 'B' + Math.floor(Math.random()*9000 + 1000),
        expiry_date: expiry.toISOString().slice(0,10),
        qty: Math.floor(Math.random()*90)+10,
        purchase_price: (Math.random()*40+5).toFixed(2),
        supplier_id: state.suppliers[(p.id + j) % state.suppliers.length].id
      });
    }
  });

  // sales: random small records per batch
  let sid=1;
  state.batches.forEach(b=>{
    const salesCount = Math.floor(Math.random()*6)+2;
    for(let s=0;s<salesCount;s++){
      const daysAgo = Math.floor(Math.random()*90);
      const date = new Date();
      date.setDate(date.getDate() - daysAgo);
      state.sales.push({
        sale_id: sid++,
        batch_id: b.batch_id,
        date: date.toISOString().slice(0,10),
        qty_sold: Math.floor(Math.random()*6)+1,
        price: (parseFloat(b.purchase_price) * (1.2 + Math.random()*0.6)).toFixed(2),
        pharmacist_id: Math.floor(Math.random()*3)+1
      });
    }
  });
}

// --- Helpers ---
function $(id){ return document.getElementById(id); }

function formatDate(d){
  const dt = new Date(d);
  return dt.toLocaleDateString();
}

function nearestExpiryForProduct(pid){
  const batches = state.batches.filter(b=>b.product_id===pid);
  if(!batches.length) return '—';
  batches.sort((a,b)=>new Date(a.expiry_date)-new Date(b.expiry_date));
  return formatDate(batches[0].expiry_date);
}

function totalStockForProduct(pid){
  return state.batches.filter(b=>b.product_id===pid).reduce((s,b)=>s + (b.qty||0), 0);
}

// --- Navigation ---
function nav(view){
  // require login for protected views
  if(!state.loggedIn && view !== 'login'){
    showView('login'); return;
  }
  showView(view);
}

function showView(view){
  const screens = ['login','dashboard','inventory','productDetail','po'];
  screens.forEach(s => {
    const el = $(s);
    if(el) el.classList.toggle('hidden', s !== view);
  });
  if(view === 'dashboard') renderDashboard();
  if(view === 'inventory') renderInventory();
  if(view === 'productDetail') renderProductDetail(state.currentProductId);
  if(view === 'po') renderPO();
}

// --- Login ---
function doLogin(){
  const user = $('username').value || 'demo';
  // simple demo: accept any
  state.loggedIn = true;
  nav('dashboard');
}

// --- Dashboard render ---
function renderDashboard(){
  // KPI 1: count items expiring in next 30 days
  const now = new Date();
  const cutoff = new Date(); cutoff.setDate(now.getDate()+30);
  let expiring = 0;
  state.batches.forEach(b=>{
    const exp = new Date(b.expiry_date);
    if(exp <= cutoff) expiring++;
  });
  $('kpi-expiring').innerText = expiring;

  // KPI 2: fake MAPE (placeholder)
  $('kpi-mape').innerText = (Math.random()*15+2).toFixed(1) + '%';

  // KPI 3: active users this week (placeholder)
  $('kpi-active').innerText = Math.floor(Math.random()*10)+1;
}

// --- Inventory render ---
function populateCategoryFilter(){
  const sel = $('filterCategory');
  const cats = [...new Set(state.products.map(p=>p.category))];
  sel.innerHTML = '<option value="">All categories</option>' + cats.map(c=>`<option value="${c}">${c}</option>`).join('');
}
function renderInventory(){
  populateCategoryFilter();
  const tbody = $('inventoryTable').querySelector('tbody');
  const filter = $('filterCategory').value;
  let rows = state.products;
  if(filter) rows = rows.filter(r=>r.category===filter);
  if(rows.length === 0){
    $('inventoryTable').classList.add('hidden');
    $('inventoryEmpty').classList.remove('hidden');
    return;
  } else {
    $('inventoryTable').classList.remove('hidden');
    $('inventoryEmpty').classList.add('hidden');
  }
  tbody.innerHTML = rows.map(p=>{
    return `<tr>
      <td>${p.name}</td>
      <td>${p.category}</td>
      <td>${totalStockForProduct(p.id)}</td>
      <td>${nearestExpiryForProduct(p.id)}</td>
      <td>
        <button class="secondary" onclick="openProduct(${p.id})">View</button>
      </td>
    </tr>`;
  }).join('');
}

// --- Product detail ---
function openProduct(pid){
  state.currentProductId = pid;
  nav('productDetail');
}
function renderProductDetail(pid){
  const prod = state.products.find(p=>p.id===pid);
  $('pdTitle').innerText = prod ? `Product: ${prod.name}` : 'Product: —';
  const tbody = $('batchesTable').querySelector('tbody');
  const batches = state.batches.filter(b=>b.product_id===pid).sort((a,b)=>new Date(a.expiry_date)-new Date(b.expiry_date));
  if(batches.length===0){
    $('batchesTable').classList.add('hidden');
    $('batchesEmpty').classList.remove('hidden');
    return;
  } else {
    $('batchesTable').classList.remove('hidden');
    $('batchesEmpty').classList.add('hidden');
  }
  tbody.innerHTML = batches.map(b=>{
    const supplier = state.suppliers.find(s=>s.id === b.supplier_id);
    return `<tr>
      <td>${b.batch_no}</td>
      <td>${formatDate(b.expiry_date)}</td>
      <td>${b.qty}</td>
      <td>${b.purchase_price}</td>
      <td>${supplier ? supplier.name : '—'}</td>
      <td><button class="secondary" onclick="alert('Mark picked from batch ${b.batch_no}')">Pick</button></td>
    </tr>`;
  }).join('');
}

// --- FEFO modal ---
function openFEFOModal(){
  const pid = state.currentProductId;
  if(!pid) return;
  const batches = state.batches.filter(b=>b.product_id===pid).sort((a,b)=>new Date(a.expiry_date)-new Date(b.expiry_date));
  const container = $('fefoContent');
  if(batches.length===0){
    container.innerHTML = '<div class="empty">No batches available.</div>';
  } else {
    container.innerHTML = `<table class="table"><thead><tr><th>Batch</th><th>Expiry</th><th>Qty</th></tr></thead><tbody>` +
      batches.map(b=>`<tr><td>${b.batch_no}</td><td>${formatDate(b.expiry_date)}</td><td>${b.qty}</td></tr>`).join('') +
      `</tbody></table>`;
  }
  $('fefoModal').classList.remove('hidden');
}
function closeFEFOModal(){ $('fefoModal').classList.add('hidden'); }
function confirmFEFO(){
  alert('FEFO picklist confirmed (demo).');
  closeFEFOModal();
}

// --- PO suggestions (simple placeholder logic) ---
function renderPO(){
  const tbody = $('poTable').querySelector('tbody');
  // naive logic: if stock < 60, recommend reorder
  tbody.innerHTML = state.products.map(p=>{
    const stock = totalStockForProduct(p.id);
    const avgDailyDemand = (Math.random()*2 + 0.5).toFixed(2);
    const suggested = stock < 60 ? Math.max(10, Math.round((60 - stock) + Math.random()*20)) : 0;
    return `<tr>
      <td>${p.name}</td>
      <td>${avgDailyDemand}</td>
      <td>${stock}</td>
      <td>${suggested}</td>
    </tr>`;
  }).join('');
}

// --- Logout modal---
function showLogout(){ $('logoutModal').classList.remove('hidden'); }
function hideLogout(){ $('logoutModal').classList.add('hidden'); }
function doLogout(){ state.loggedIn=false; hideLogout(); nav('login'); }

// --- small helpers for add product / batch (not fully functional, placeholders) ---
function showAddProduct(){ alert('Add Product dialog (not implemented in wireframe)'); }
function showAddBatch(){ alert('Add Batch dialog (not implemented in wireframe)'); }

// --- Init ---
seedData();
nav('login');
