/* global QRCode */

/* ── DATA ────────────────────────── */
const API_BASE_URL = 'http://127.0.0.1:8000';

let rewards = [
    {id: 1, comp: 'organik', sub: 'sisa_makanan', pts: 10},
    {id: 2, comp: 'anorganik', sub: 'plastik', pts: 25},
    {id: 3, comp: 'b3', sub: 'baterai', pts: 50},
];

let devices = [
    {id: 1, qr: 'QR-TPS-001', loc: 'TPS Blok A – Gedung Utama', org: 30, inorg: 20, b3: 10},
    {id: 2, qr: 'QR-TPS-002', loc: 'TPS Blok B – Kantin Timur', org: 25, inorg: 25, b3: 5},
    {id: 3, qr: 'QR-TPS-003', loc: 'TPS Parkiran Utara', org: 20, inorg: 15, b3: 8},
    {id: 4, qr: 'QR-TPS-004', loc: 'TPS Lab Komputer', org: 15, inorg: 15, b3: 10},
    {id: 5, qr: 'QR-TPS-005', loc: 'TPS Lobby Utama', org: 30, inorg: 15, b3: 7},
];

let rId = 4, dId = 6;

const compChip = {
    organik: '<span class="chip chip-organic">🌿 Organik</span>',
    anorganik: '<span class="chip chip-inorganic">♻️ Anorganik</span>',
    b3: '<span class="chip chip-b3">⚠️ B3</span>',
};

const subLabel = {
    plastik: 'Plastik', kertas: 'Kertas', kaca: 'Kaca', logam: 'Logam',
    sisa_makanan: 'Sisa Makanan', daun: 'Daun / Tanaman',
    baterai: 'Baterai', elektronik: 'Elektronik', kimia: 'Kimia Berbahaya',
};

const pages = {
    reward: {pid: 'page-reward', title: 'Point Reward', sub: 'Manajemen Poin'},
    upload: {pid: 'page-upload', title: 'Upload Model ML', sub: 'Model Management'},
    device: {pid: 'page-device', title: 'Kelola Device', sub: 'Lokasi & Kapasitas'},
};

/* ── UTILITIES ───────────────────── */
function debounce(func, delay) {
    let timeout;
    return function (...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), delay);
    };
}

function toast(msg, type = 'success') {
    const t = document.createElement('div');
    t.className = `toast ${type}`;
    t.innerHTML = `<span>${type === 'success' ? '✅' : '❌'}</span><span>${msg}</span>`;
    document.getElementById('toasts').appendChild(t);
    setTimeout(() => {
        t.style.cssText += 'opacity:0;transform:translateX(20px);transition:0.3s';
        setTimeout(() => t.remove(), 350);
    }, 3000);
}

function renderQRDirect(text, containerId, size = 56) {
    const container = document.getElementById(containerId);
    if (!container || !text) return;
    container.innerHTML = '';
    new QRCode(container, {text: text, width: size, height: size, correctLevel: QRCode.CorrectLevel.M});
}

/* ── NAV ─────────────────────────── */
function initNav() {
    document.getElementById('sidebar-nav').addEventListener('click', e => {
        const item = e.target.closest('.nav-item');
        if (!item) return;

        const key = item.dataset.page;
        document.querySelectorAll('.page-content').forEach(p => p.classList.remove('active'));
        document.querySelectorAll('.nav-item').forEach(n => n.classList.remove('active'));

        document.getElementById(pages[key].pid).classList.add('active');
        item.classList.add('active');

        document.getElementById('topbar-title').textContent = pages[key].title;
        document.getElementById('topbar-sub').textContent = pages[key].sub;
        document.querySelector('.main').scrollTop = 0;

        if (key === 'reward') renderRewards();
        if (key === 'device') renderDevices();
    });
}

async function fetchRewards() {
    try {
        const res = await fetch(`${API_BASE_URL}/admin/reward-point/`);
        const json = await res.json();
        if (json.data) {
            rewards = json.data.map(r => ({
                id: r.id, comp: r.compartment_type, sub: r.sub_category, pts: r.reward_points
            }));
        }
    } catch (e) {
        console.error(e);
        toast('Gagal memuat data reward', 'error');
    }
}

/* ── REWARD ──────────────────────── */
async function renderRewards(rows = null) {
    if (!rows) {
        await fetchRewards();
        rows = rewards;
    }
        
    const tb = document.getElementById('reward-tbody');
    document.getElementById('cnt-reward').textContent = rows.length + ' data';
    document.getElementById('s-r-total').textContent = rewards.length;
    document.getElementById('badge-reward').textContent = rewards.length;

    if (rewards.length) {
        const pts = rewards.map(r => r.pts);
        const mx = rewards[pts.indexOf(Math.max(...pts))];
        const mn = rewards[pts.indexOf(Math.min(...pts))];
        document.getElementById('s-r-max').textContent = Math.max(...pts);
        document.getElementById('s-r-max-lbl').textContent = subLabel[mx.sub] || mx.sub;
        document.getElementById('s-r-min').textContent = Math.min(...pts);
        document.getElementById('s-r-min-lbl').textContent = subLabel[mn.sub] || mn.sub;
    }

    if (!rows || !rows.length) {
        tb.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">⭐</div><div class="empty-text">Belum ada data reward</div></div></td></tr>`;
        return;
    }

    tb.innerHTML = rows.map((r, i) => `
        <tr>
            <td class="td-number">${String(i + 1).padStart(2, '0')}</td>
            <td>${compChip[r.comp] || r.comp}</td>
            <td><span class="chip chip-general">${subLabel[r.sub] || r.sub}</span></td>
            <td><span class="pts-badge">+${r.pts} pts</span></td>
            <td><div class="td-actions">
                <button class="btn btn-outline btn-sm btn-icon btn-edit-reward" data-id="${r.id}">✏️</button>
                <button class="btn btn-danger btn-sm btn-icon btn-del-reward" data-id="${r.id}">🗑️</button>
            </div></td>
        </tr>`).join('');
}

function filterReward(q) {
    const query = q.toLowerCase().trim();
    renderRewards(query ? rewards.filter(r => r.comp.includes(query) || (subLabel[r.sub] || r.sub).toLowerCase().includes(query) || String(r.pts).includes(query)) : rewards);
}

async function saveReward() {
    const comp = document.getElementById('r-compartment').value;
    const sub = document.getElementById('r-subcategory').value;
    const pts = parseInt(document.getElementById('r-points').value, 10);
    const eid = document.getElementById('r-edit-id').value;

    if (!comp || !sub || !pts) {
        toast('Lengkapi semua field!', 'error');
        return;
    }

    try {
        const payload = { compartment_type: comp, sub_category: sub, reward_points: pts };
        if (eid) {
            const res = await fetch(`${API_BASE_URL}/admin/reward-point/${eid}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) toast('Reward diupdate ✅', 'success');
            else toast('Gagal update reward', 'error');
        } else {
            const res = await fetch(`${API_BASE_URL}/admin/reward-point/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) toast('Reward ditambahkan ✅', 'success');
            else toast('Gagal tambah reward', 'error');
        }
    } catch (e) {
        console.error(e);
        toast('Terjadi kesalahan jaringan', 'error');
    }

    await renderRewards();
    closeModal('modal-reward');
}

/* ── DEVICE ──────────────────────── */
function renderDevices(rows = devices) {
    const tb = document.getElementById('device-tbody');
    document.getElementById('cnt-device').textContent = rows.length + ' data';
    document.getElementById('s-d-total').textContent = devices.length;
    document.getElementById('badge-device').textContent = devices.length;
    document.getElementById('s-d-org').textContent = devices.reduce((a, d) => a + d.org, 0) + ' L';
    document.getElementById('s-d-inorg').textContent = devices.reduce((a, d) => a + d.inorg, 0) + ' L';
    document.getElementById('s-d-b3').textContent = devices.reduce((a, d) => a + d.b3, 0) + ' L';

    if (!rows.length) {
        tb.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">🗑️</div><div class="empty-text">Belum ada data device</div></div></td></tr>`;
        return;
    }

    tb.innerHTML = rows.map((d, i) => {
        const tot = d.org + d.inorg + d.b3 || 1;
        const pO = Math.round(d.org / tot * 100), pI = Math.round(d.inorg / tot * 100),
            pB = Math.round(d.b3 / tot * 100);
        return `<tr>
            <td class="td-number">${String(i + 1).padStart(2, '0')}</td>
            <td><span class="td-qr-badge">${d.qr}</span></td>
            <td><div class="qr-cell" id="qr-cell-${d.id}"></div></td>
            <td><div class="td-loc-name">${d.loc}</div></td>
            <td><div class="cap-bar-wrap">
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:var(--green-li)">🌿 Organik</div><div class="cap-bar"><div class="cap-bar-fill fill-org" style="width:${pO}%"></div></div><div class="cap-bar-val">${d.org}L</div></div>
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:#84b0d8">♻️ Anorg.</div><div class="cap-bar"><div class="cap-bar-fill fill-inorg" style="width:${pI}%"></div></div><div class="cap-bar-val">${d.inorg}L</div></div>
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:#e08077">⚠️ B3</div><div class="cap-bar"><div class="cap-bar-fill fill-b3" style="width:${pB}%"></div></div><div class="cap-bar-val">${d.b3}L</div></div>
            </div></td>
            <td><div class="td-actions">
                <button class="btn btn-outline btn-sm btn-icon btn-edit-device" data-id="${d.id}">✏️</button>
                <button class="btn btn-danger btn-sm btn-icon btn-del-device" data-id="${d.id}">🗑️</button>
            </div></td>
        </tr>`;
    }).join('');

    // Render QR Code Langsung
    rows.forEach(d => {
        renderQRDirect(d.qr, `qr-cell-${d.id}`);
    });
}

function filterDevice(q) {
    const query = q.toLowerCase().trim();
    renderDevices(query ? devices.filter(d => d.qr.toLowerCase().includes(query) || d.loc.toLowerCase().includes(query)) : devices);
}

function saveDevice() {
    const qr = document.getElementById('d-qr').value.trim();
    const loc = document.getElementById('d-location').value.trim();
    const org = parseInt(document.getElementById('d-cap-org').value, 10) || 0;
    const inorg = parseInt(document.getElementById('d-cap-inorg').value, 10) || 0;
    const b3 = parseInt(document.getElementById('d-cap-b3').value, 10) || 0;
    const eid = document.getElementById('d-edit-id').value;

    if (!qr || !loc) {
        toast('QR Code & Nama Lokasi wajib diisi!', 'error');
        return;
    }

    if (eid) {
        const i = devices.findIndex(x => x.id === parseInt(eid, 10));
        if( i > -1) devices[i] = {...devices[i], qr, loc, org, inorg, b3};
        toast('Device diupdate ✅', 'success');
    } else {
        devices.push({id: dId++, qr, loc, org, inorg, b3});
        toast('Device ditambahkan ✅', 'success');
    }
    renderDevices();
    closeModal('modal-device');
}

function updateQRModalPreview(val) {
    const box = document.getElementById('mqr-box');
    document.getElementById('mqr-val').textContent = val || '—';
    box.innerHTML = '';
    if (!val) {
        box.innerHTML = '<span class="qr-preview-text">QR Preview</span>';
        return;
    }
    renderQRDirect(val, 'mqr-box', 64);
}

/* ── MODAL ───────────────────────── */
function openModal(id, mode, editData = null) {
    const ov = document.getElementById(id);
    const titleEl = id === 'modal-reward' ? document.getElementById('mtitle-reward') : document.getElementById('mtitle-device');

    if (mode === 'add') {
        ov.querySelectorAll('input:not([type="hidden"]),select').forEach(e => e.value = '');
        ov.querySelector('[id$="-edit-id"]').value = '';
        if (id === 'modal-reward') titleEl.textContent = '⭐ Tambah Reward';
        if (id === 'modal-device') {
            titleEl.textContent = '🗑️ Tambah Device';
            updateQRModalPreview('');
        }
    } else if (mode === 'edit' && editData) {
        if (id === 'modal-reward') {
            document.getElementById('r-edit-id').value = editData.id;
            document.getElementById('r-compartment').value = editData.comp;
            document.getElementById('r-subcategory').value = editData.sub;
            document.getElementById('r-points').value = editData.pts;
            titleEl.textContent = '✏️ Edit Reward';
        }
        if (id === 'modal-device') {
            document.getElementById('d-edit-id').value = editData.id;
            document.getElementById('d-qr').value = editData.qr;
            document.getElementById('d-location').value = editData.loc;
            document.getElementById('d-cap-org').value = editData.org;
            document.getElementById('d-cap-inorg').value = editData.inorg;
            document.getElementById('d-cap-b3').value = editData.b3;
            titleEl.textContent = '✏️ Edit Device';
            updateQRModalPreview(editData.qr);
        }
    }
    ov.classList.add('open');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}

/* ── UPLOAD ──────────────────────── */
let selFile = null;

function fmtB(b) {
    if (b < 1024) return b + ' B';
    if (b < 1048576) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1048576).toFixed(1) + ' MB';
}

function clearUpload() {
    selFile = null;
    document.getElementById('file-input').value = '';
    document.getElementById('upload-subcat').value = '';
    document.getElementById('file-info').classList.remove('visible');
    const prog = document.getElementById('uprog');
    prog.classList.remove('show');
    document.getElementById('ufill').style.width = '0%';
    document.getElementById('upct').textContent = '0%';
}

/* ── INIT EVENT LISTENERS ────────── */
document.addEventListener('DOMContentLoaded', () => {
    initNav();

    // Search Filters dengan Debounce
    document.getElementById('search-reward').addEventListener('input', debounce(e => filterReward(e.target.value), 300));
    document.getElementById('search-device').addEventListener('input', debounce(e => filterDevice(e.target.value), 300));

    // QR Preview Modal
    document.getElementById('d-qr').addEventListener('input', debounce(e => updateQRModalPreview(e.target.value.trim()), 300));

    // Modal Triggers
    document.querySelectorAll('.btn-open-modal').forEach(btn => {
        btn.addEventListener('click', e => openModal(e.target.dataset.modal, 'add'));
    });
    document.querySelectorAll('.btn-close-modal').forEach(btn => {
        btn.addEventListener('click', e => closeModal(e.target.dataset.modal));
    });
    document.querySelectorAll('.modal-overlay').forEach(o => {
        o.addEventListener('click', e => {
            if (e.target === o) closeModal(o.id);
        });
    });

    // Form Submits
    document.getElementById('btn-save-reward').addEventListener('click', saveReward);
    document.getElementById('btn-save-device').addEventListener('click', saveDevice);

    // Event Delegation untuk Tabel (Edit & Delete)
    document.getElementById('reward-tbody').addEventListener('click', async e => {
        const btnEdit = e.target.closest('.btn-edit-reward');
        const btnDel = e.target.closest('.btn-del-reward');

        if (btnEdit) {
            const r = rewards.find(x => x.id === parseInt(btnEdit.dataset.id, 10));
            if (r) openModal('modal-reward', 'edit', r);
        }
        if (btnDel) {
            if (!confirm('Hapus reward ini?')) return;
            const rid = parseInt(btnDel.dataset.id, 10);
            try {
                const res = await fetch(`${API_BASE_URL}/admin/reward-point/${rid}`, { method: 'DELETE' });
                if (res.ok) {
                    toast('Reward dihapus', 'success');
                    await renderRewards();
                } else {
                    toast('Gagal hapus reward', 'error');
                }
            } catch (err) {
                console.error(err);
                toast('Network error', 'error');
            }
        }
    });

    document.getElementById('device-tbody').addEventListener('click', e => {
        const btnEdit = e.target.closest('.btn-edit-device');
        const btnDel = e.target.closest('.btn-del-device');

        if (btnEdit) {
            const d = devices.find(x => x.id === parseInt(btnEdit.dataset.id, 10));
            if (d) openModal('modal-device', 'edit', d);
        }
        if (btnDel) {
            if (!confirm('Hapus device ini?')) return;
            devices = devices.filter(x => x.id !== parseInt(btnDel.dataset.id, 10));
            renderDevices();
            toast('Device dihapus', 'success');
        }
    });

    // Upload Logic
    const fInput = document.getElementById('file-input');
    fInput.addEventListener('change', e => {
        const f = e.target.files[0];
        if (!f) return;
        selFile = f;
        document.getElementById('fname').textContent = f.name;
        document.getElementById('fsize').textContent = fmtB(f.size);
        document.getElementById('file-info').classList.add('visible');
    });

    document.getElementById('btn-upload-submit').addEventListener('click', () => {
        if (!document.getElementById('upload-subcat').value.trim()) {
            toast('Isi sub category!', 'error');
            return;
        }
        if (!selFile) {
            toast('Pilih file model!', 'error');
            return;
        }

        const prog = document.getElementById('uprog'), fill = document.getElementById('ufill'),
            pct = document.getElementById('upct');
        prog.classList.add('show');
        let p = 0;
        const iv = setInterval(() => {
            p += Math.random() * 18;
            if (p >= 100) {
                p = 100;
                clearInterval(iv);
            }
            fill.style.width = p + '%';
            pct.textContent = Math.round(p) + '%';
            if (p === 100) {
                setTimeout(() => {
                    prog.classList.remove('show');
                    toast('File berhasil diupload & replace ✅', 'success');
                    clearUpload();
                }, 700);
            }
        }, 200);
    });

    document.getElementById('btn-upload-reset').addEventListener('click', clearUpload);

    const dz = document.getElementById('dropzone');
    ['dragenter', 'dragover'].forEach(ev => dz.addEventListener(ev, e => {
        e.preventDefault();
        dz.classList.add('drag-over');
    }));
    ['dragleave', 'drop'].forEach(ev => dz.addEventListener(ev, e => {
        e.preventDefault();
        dz.classList.remove('drag-over');
    }));
    dz.addEventListener('drop', e => {
        const f = e.dataTransfer.files[0];
        if (f) {
            selFile = f;
            document.getElementById('fname').textContent = f.name;
            document.getElementById('fsize').textContent = fmtB(f.size);
            document.getElementById('file-info').classList.add('visible');
        }
    });

    // Render Awal
    renderRewards();
    renderDevices();
});

