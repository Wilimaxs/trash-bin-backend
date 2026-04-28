/* ── UPLOAD LOGIC ──────────────────────── */

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

document.addEventListener('DOMContentLoaded', () => {
    // Upload Input Logic
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

    // Dropzone Logic
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
});
