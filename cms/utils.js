/* ── UTILITIES & SHARED DATA ───────────────────── */

const API_BASE_URL = 'https://notify.basehub.me';

const compChip = {
    organik: '<span class="chip chip-organic">🌿 Organik</span>',
    organic: '<span class="chip chip-organic">🌿 Organik</span>',
    orgaic: '<span class="chip chip-organic">🌿 Organik</span>',
    anorganik: '<span class="chip chip-inorganic">♻️ Anorganik</span>',
    b3: '<span class="chip chip-b3">⚠️ B3</span>',
};

const pages = {
    reward: {pid: 'page-reward', title: 'Point Reward', sub: 'Manajemen Poin'},
    upload: {pid: 'page-upload', title: 'Upload Model ML', sub: 'Model Management'},
    device: {pid: 'page-device', title: 'Kelola Device', sub: 'Lokasi & Kapasitas'},
};

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
    // eslint-disable-next-line no-undef
    new QRCode(container, {text: text, width: size, height: size, correctLevel: QRCode.CorrectLevel.M});
}

function openModal(id, mode, editData = null) {
    const ov = document.getElementById(id);
    const titleEl = id === 'modal-reward' ? document.getElementById('mtitle-reward') : document.getElementById('mtitle-device');

    if (mode === 'add') {
        ov.querySelectorAll('input:not([type="hidden"]),select').forEach(e => e.value = '');
        ov.querySelector('[id$="-edit-id"]').value = '';
        if (id === 'modal-reward') titleEl.textContent = '⭐ Tambah Reward';
        if (id === 'modal-device') {
            titleEl.textContent = '🗑️ Tambah Device';
            if (typeof updateQRModalPreview === 'function') updateQRModalPreview('');
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
            titleEl.textContent = '✏️ Edit Device';
            if (typeof updateQRModalPreview === 'function') updateQRModalPreview(editData.qr);
        }
    }
    ov.classList.add('open');
}

function closeModal(id) {
    document.getElementById(id).classList.remove('open');
}
