/* ── DEVICE LOGIC ──────────────────────── */

let devices = [
    {id: 1, qr: 'QR-TPS-001', loc: 'TPS Blok A – Gedung Utama', org: 30, inorg: 20, b3: 10},
    {id: 2, qr: 'QR-TPS-002', loc: 'TPS Blok B – Kantin Timur', org: 25, inorg: 25, b3: 5},
    {id: 3, qr: 'QR-TPS-003', loc: 'TPS Parkiran Utara', org: 20, inorg: 15, b3: 8},
    {id: 4, qr: 'QR-TPS-004', loc: 'TPS Lab Komputer', org: 15, inorg: 15, b3: 10},
    {id: 5, qr: 'QR-TPS-005', loc: 'TPS Lobby Utama', org: 30, inorg: 15, b3: 7},
];

let dId = 6;

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

document.addEventListener('DOMContentLoaded', () => {
    // Search & QR Preview Listeners
    document.getElementById('search-device').addEventListener('input', debounce(e => filterDevice(e.target.value), 300));
    document.getElementById('d-qr').addEventListener('input', debounce(e => updateQRModalPreview(e.target.value.trim()), 300));
    
    // Form Submit
    document.getElementById('btn-save-device').addEventListener('click', saveDevice);

    // Event Delegation (Edit & Delete)
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
});
