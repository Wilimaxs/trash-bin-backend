/* ── UNKNOWN TRASH LOGIC ──────────────────────── */

let currentUnknownPage = 1;
const unknownPageSize = 10;

async function fetchUnknownTrash(page = 1) {
    try {
        const res = await fetch(`${API_BASE_URL}/admin/unknown-disposal/?page=${page}&size=${unknownPageSize}`);
        const result = await res.json();
        
        if (res.ok && result.data) {
            renderUnknownTrash(result.data);
            currentUnknownPage = result.data.page;
        } else {
            toast(result.message || 'Gagal memuat data', 'error');
        }
    } catch (e) {
        toast('Koneksi ke server gagal', 'error');
        console.error(e);
    }
}

function renderUnknownTrash(data) {
    const tbody = document.getElementById('unknown-tbody');
    tbody.innerHTML = '';
    
    document.getElementById('cnt-unknown').textContent = `${data.total} data`;
    
    if (!data.items || data.items.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color: var(--text-muted);">Tidak ada data sampah tak dikenali</td></tr>`;
        renderUnknownPagination(0, 1);
        return;
    }

    data.items.forEach((item, idx) => {
        const row = document.createElement('tr');
        const imgPath = item.image_url ? `${API_BASE_URL}${item.image_url}` : '';
        const imgTag = imgPath ? `<img src="${imgPath}" alt="Unknown" style="width:50px; height:50px; border-radius:4px; object-fit:cover; border:1px solid var(--border);" />` : `<span style="color:var(--text-muted); font-size:0.8em;">No Image</span>`;
        
        row.innerHTML = `
            <td>${((data.page - 1) * data.size) + idx + 1}</td>
            <td>${imgTag}</td>
            <td>${item.created_at || '-'}</td>
            <td><span class="badge" style="background:var(--bg-card); color:var(--text);">${item.bin_location}</span></td>
            <td>
                <div style="display:flex; gap:5px;">
                    <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.85em;" onclick="downloadUnknown(${item.id})">⬇️ Download</button>
                    <button class="btn btn-outline" style="padding: 4px 8px; font-size: 0.85em; color:var(--red); border-color:var(--red);" onclick="deleteUnknown(${item.id})">🗑️ Delete</button>
                </div>
            </td>
        `;
        tbody.appendChild(row);
    });
    
    renderUnknownPagination(data.total_pages, data.page);
}

function renderUnknownPagination(totalPages, currentPage) {
    const wrap = document.getElementById('unknown-pagination');
    wrap.innerHTML = '';
    
    if (totalPages <= 1) return;
    
    const prevBtn = document.createElement('button');
    prevBtn.className = 'btn btn-outline';
    prevBtn.style.padding = '4px 10px';
    prevBtn.textContent = 'Prev';
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => fetchUnknownTrash(currentPage - 1);
    wrap.appendChild(prevBtn);
    
    const info = document.createElement('span');
    info.style.padding = '4px 10px';
    info.style.color = 'var(--text-muted)';
    info.style.fontSize = '0.9em';
    info.textContent = `Page ${currentPage} of ${totalPages}`;
    wrap.appendChild(info);
    
    const nextBtn = document.createElement('button');
    nextBtn.className = 'btn btn-outline';
    nextBtn.style.padding = '4px 10px';
    nextBtn.textContent = 'Next';
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => fetchUnknownTrash(currentPage + 1);
    wrap.appendChild(nextBtn);
}

async function deleteUnknown(id) {
    if (!confirm('Hapus data ini permanen?')) return;
    try {
        const res = await fetch(`${API_BASE_URL}/admin/unknown-disposal/${id}`, { method: 'DELETE' });
        const result = await res.json();
        if (res.ok) {
            toast(result.message || 'Berhasil dihapus', 'success');
            fetchUnknownTrash(currentUnknownPage);
        } else {
            toast(result.message, 'error');
        }
    } catch (e) {
        toast('Koneksi terputus', 'error');
    }
}

function downloadUnknown(id) {
    // Membuka window/tab baru untuk download API
    const url = `${API_BASE_URL}/admin/unknown-disposal/download/${id}`;
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.download = '';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    // API akan menghapus data di belakang layar, kita refresh table
    setTimeout(() => fetchUnknownTrash(currentUnknownPage), 1500);
}

document.addEventListener('DOMContentLoaded', () => {
    // Event listeners
    document.getElementById('btn-delete-all')?.addEventListener('click', async () => {
        if (!confirm('Yakin ingin menghapus SEMUA data unknown trash permanen?')) return;
        try {
            const res = await fetch(`${API_BASE_URL}/admin/unknown-disposal/all`, { method: 'DELETE' });
            const result = await res.json();
            if (res.ok) {
                toast(result.message || 'Semua data dihapus', 'success');
                fetchUnknownTrash(1);
            } else {
                toast(result.message, 'error');
            }
        } catch (e) {
            toast('Koneksi terputus', 'error');
        }
    });
    
    document.getElementById('btn-download-all')?.addEventListener('click', () => {
        if (!confirm('Download semua gambar dalam ZIP dan hapus semua data?')) return;
        
        const url = `${API_BASE_URL}/admin/unknown-disposal/download-all`;
        const a = document.createElement('a');
        a.href = url;
        a.target = '_blank';
        a.download = 'unknown_disposals.zip';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        
        setTimeout(() => fetchUnknownTrash(1), 2000);
    });

    // Panggil fetch awal saat load
    fetchUnknownTrash(1);
});
