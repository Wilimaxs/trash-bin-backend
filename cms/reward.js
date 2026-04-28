/* ── REWARD LOGIC ──────────────────────── */

// Data state untuk menyimpan daftar reward.
// Sebelumnya: Berisi data dummy. 
// Sekarang: Diubah menjadi array kosong karena data akan diambil langsung (fetching) dari database backend API.
let rewards = [];

/**
 * fetchRewards: Mengambil data reward terbaru dari backend API.
 * Proses ini menembak endpoint GET dan memetakan respons JSON ke dalam state `rewards`.
 */
async function fetchRewards() {
    try {
        const res = await fetch(`${API_BASE_URL}/admin/reward-point/`);
        const json = await res.json();
        if (json.data) {
            rewards = json.data.map(r => ({
                id: r.id, 
                comp: r.compartment_type ? r.compartment_type.toLowerCase() : '', 
                sub: r.sub_category, 
                pts: r.reward_points
            }));
        }
    } catch (e) {
        console.error(e);
        toast('Gagal memuat data reward', 'error');
    }
}

/**
 * renderRewards: Me-render (menampilkan) data reward ke dalam elemen tabel HTML.
 * Fungsi ini juga akan menghitung statistik (total data, nilai reward tertinggi & terendah).
 * @param {Array|null} rows - Array data reward yang ingin ditampilkan. Jika null, fungsi akan fetch dari API.
 */
async function renderRewards(rows = null) {
    if (!rows) {
        await fetchRewards();
        rows = rewards;
    }
        
    const tb = document.getElementById('reward-tbody');
    document.getElementById('cnt-reward').textContent = rows.length + ' data';
    document.getElementById('s-r-total').textContent = String(rewards.length);
    document.getElementById('badge-reward').textContent = String(rewards.length);

    if (rewards.length) {
        const pts = rewards.map(r => r.pts);
        const mx = rewards[pts.indexOf(Math.max(...pts))];
        const mn = rewards[pts.indexOf(Math.min(...pts))];
        document.getElementById('s-r-max').textContent = String(Math.max(...pts));
        document.getElementById('s-r-max-lbl').textContent = mx.sub;
        document.getElementById('s-r-min').textContent = String(Math.min(...pts));
        document.getElementById('s-r-min-lbl').textContent = mn.sub;
    }

    if (!rows || !rows.length) {
        tb.innerHTML = `<tr><td colspan="5"><div class="empty-state"><div class="empty-icon">⭐</div><div class="empty-text">Belum ada data reward</div></div></td></tr>`;
        return;
    }

    tb.innerHTML = rows.map((r, i) => `
        <tr>
            <td class="td-number">${String(i + 1).padStart(2, '0')}</td>
            <td>${compChip[r.comp] || r.comp}</td>
            <td><span class="chip chip-general">${r.sub}</span></td>
            <td><span class="pts-badge">+${r.pts} pts</span></td>
            <td><div class="td-actions">
                <button class="btn btn-outline btn-sm btn-icon btn-edit-reward" data-id="${r.id}">✏️</button>
                <button class="btn btn-danger btn-sm btn-icon btn-del-reward" data-id="${r.id}">🗑️</button>
            </div></td>
        </tr>`).join('');
}

/**
 * filterReward: Melakukan pencarian (search) pada data reward di sisi klien (frontend).
 * Menyaring tabel berdasarkan kompartemen, sub kategori, atau jumlah poin.
 * @param {string} q - Kata kunci (query) pencarian.
 */
function filterReward(q) {
    const query = q.toLowerCase().trim();
    // Gunakan await atau tangani promise (misalnya menggunakan then/catch atau membiarkannya dieksekusi secara asinkron tanpa menahan UI)
    renderRewards(query ? rewards.filter(r => r.comp.includes(query) || (r.sub || '').toLowerCase().includes(query) || String(r.pts).includes(query)) : rewards).catch(console.error);
}

/**
 * saveReward: Menangani action submit pada Form Modal Reward.
 * Menentukan apakah ini pembuatan data baru (POST) atau update data (PUT) berdasarkan keberadaan nilai pada hidden input ID.
 */
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

// Menunggu kerangka HTML (DOM) untuk dirender sepenuhnya sebelum menempelkan event listener.
document.addEventListener('DOMContentLoaded', () => {
    // Search Filters: menggunakan listener 'input' beserta utilitas debounce supaya tidak lag (spam fungsi filter).
    document.getElementById('search-reward').addEventListener('input', debounce(e => filterReward(e.target.value), 300));
    
    // Form Submit: saat tombol simpan di klik, fungsi saveReward dieksekusi.
    document.getElementById('btn-save-reward').addEventListener('click', saveReward);

    // Event Delegation (Edit & Delete): Menggunakan satu event listener pada <tbody tabel> 
    // untuk menangkap klik dari berbagai tombol edit/hapus pada rows yang dibuat secara dinamis.
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
});
