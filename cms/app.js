/* ── APP INIT / ORCHESTRATOR ─────────────────────────── */

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

document.addEventListener('DOMContentLoaded', () => {
    initNav();

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

    // Render Awal saat Halaman Dimuat
    renderRewards();
    renderDevices();
});

