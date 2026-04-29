/* ── DEVICE LOGIC ──────────────────────── */

let devices = [];

async function fetchDevices() {
    try {
        const res = await fetch(`${API_BASE_URL}/admin/device/`);
        const json = await res.json();
        if (json.data) {
            devices = json.data.map(d => ({
                id: d.id, 
                qr: d.qr_code, 
                loc: d.location_name, 
                org: d.capacity_organic, 
                inorg: d.capacity_inorganic, 
                b3: d.capacity_b3
            }));
        }
    } catch (e) {
        console.error(e);
        toast('Gagal memuat data device', 'error');
    }
}

async function renderDevices(rows = null) {
    if (!rows) {
        await fetchDevices();
        rows = devices;
    }

    const tb = document.getElementById('device-tbody');
    document.getElementById('cnt-device').textContent = rows.length + ' data';
    document.getElementById('s-d-total').textContent = String(devices.length);
    
    // Hitung persentase rata-rata untuk statistik atas
    const avgOrg = devices.length ? Math.round(devices.reduce((a, d) => a + (d.org || 0), 0) / devices.length) : 0;
    const avgInorg = devices.length ? Math.round(devices.reduce((a, d) => a + (d.inorg || 0), 0) / devices.length) : 0;
    const avgB3 = devices.length ? Math.round(devices.reduce((a, d) => a + (d.b3 || 0), 0) / devices.length) : 0;

    document.getElementById('s-d-org').textContent = avgOrg + '%';
    document.getElementById('s-d-inorg').textContent = avgInorg + '%';
    document.getElementById('s-d-b3').textContent = avgB3 + '%';

    if (!rows || !rows.length) {
        tb.innerHTML = `<tr><td colspan="6"><div class="empty-state"><div class="empty-icon">🗑️</div><div class="empty-text">Belum ada data device</div></div></td></tr>`;
        return;
    }

    tb.innerHTML = rows.map((d, i) => {
        // Karena kapasitas di database sudah berupa persentase 0-100, 
        // kita langsung menjadikannya sebagai value untuk progress bar
        const pO = d.org || 0, pI = d.inorg || 0, pB = d.b3 || 0;
        return `<tr>
            <td class="td-number">${String(i + 1).padStart(2, '0')}</td>
            <td><span class="td-qr-badge">${d.qr}</span></td>
            <td><div class="qr-cell" id="qr-cell-${d.id}"></div></td>
            <td><div class="td-loc-name">${d.loc || '—'}</div></td>
            <td><div class="cap-bar-wrap">
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:var(--green-li)">🌿 Organik</div><div class="cap-bar"><div class="cap-bar-fill fill-org" style="width:${pO}%"></div></div><div class="cap-bar-val">${pO}%</div></div>
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:#84b0d8">♻️ Anorg.</div><div class="cap-bar"><div class="cap-bar-fill fill-inorg" style="width:${pI}%"></div></div><div class="cap-bar-val">${pI}%</div></div>
                <div class="cap-bar-row"><div class="cap-bar-label" style="color:#e08077">⚠️ B3</div><div class="cap-bar"><div class="cap-bar-fill fill-b3" style="width:${pB}%"></div></div><div class="cap-bar-val">${pB}%</div></div>
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
        // Tambah fitur klik perbesar QR
        const cellBox = document.getElementById(`qr-cell-${d.id}`);
        if (cellBox) {
            cellBox.style.cursor = 'pointer';
            cellBox.title = 'Klik untuk memperbesar & download';
            cellBox.addEventListener('click', () => viewLargeQR(d.qr, d.loc));
        }
    });
}

function viewLargeQR(qr, loc) {
    document.getElementById('qr-large-title').textContent = loc || 'Tanpa Lokasi';
    document.getElementById('qr-large-subtitle').textContent = qr;
    
    // Gunakan utility renderQRDirect untuk me-render ukuran besar (256px)
    renderQRDirect(qr, 'qr-large-box', 256);
    
    // Set up fungsionalitas button download
    const btnDown = document.getElementById('btn-download-qr');
    btnDown.onclick = () => {
        const canvas = document.querySelector('#qr-large-box canvas');
        if (canvas) {
            const url = canvas.toDataURL('image/png');
            const a = document.createElement('a');
            a.href = url;
            a.download = `QR_${qr}.png`;
            a.click();
        } else {
            const img = document.querySelector('#qr-large-box img');
            if (img && img.src) {
                const a = document.createElement('a');
                a.href = img.src;
                a.download = `QR_${qr}.png`;
                a.click();
            }
        }
    };
    
    // Gunakan fungsi utils openModal (mode view akan mem-bypass kondisi add/edit dan hanya membuka modal)
    openModal('modal-qr-view', 'view');
}

function filterDevice(q) {
    const query = q.toLowerCase().trim();
    renderDevices(query ? devices.filter(d => 
        (d.qr || '').toLowerCase().includes(query) || (d.loc || '').toLowerCase().includes(query)
    ) : devices).catch(console.error);
}

async function saveDevice() {
    const qr = document.getElementById('d-qr').value.trim();
    const loc = document.getElementById('d-location').value.trim();
    const eid = document.getElementById('d-edit-id').value;

    if (!qr) {
        toast('QR Code wajib diisi!', 'error');
        return;
    }

    try {
        const payload = { qr_code: qr, location_name: loc || null };
        if (eid) {
            const res = await fetch(`${API_BASE_URL}/admin/device/${eid}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (res.ok) toast('Device diupdate ✅', 'success');
            else toast(json.message || 'Gagal update device', 'error');
        } else {
            const res = await fetch(`${API_BASE_URL}/admin/device/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const json = await res.json();
            if (res.ok && !json.error) toast('Device ditambahkan ✅', 'success');
            else toast(json.message || 'Gagal tambah device', 'error');
        }
    } catch (e) {
        console.error(e);
        toast('Terjadi kesalahan jaringan', 'error');
    }

    await renderDevices();
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
    document.getElementById('device-tbody').addEventListener('click', async e => {
        const btnEdit = e.target.closest('.btn-edit-device');
        const btnDel = e.target.closest('.btn-del-device');

        if (btnEdit) {
            const d = devices.find(x => x.id === parseInt(btnEdit.dataset.id, 10));
            if (d) openModal('modal-device', 'edit', d);
        }
        if (btnDel) {
            if (!confirm('Hapus device ini?')) return;
            const did = parseInt(btnDel.dataset.id, 10);
            try {
                const res = await fetch(`${API_BASE_URL}/admin/device/${did}`, { method: 'DELETE' });
                const json = await res.json();
                if (res.ok && !json.error) {
                    toast('Device dihapus', 'success');
                    await renderDevices();
                } else {
                    toast(json.message || 'Gagal hapus device', 'error');
                }
            } catch (err) {
                console.error(err);
                toast('Network error', 'error');
            }
        }
    });
});
