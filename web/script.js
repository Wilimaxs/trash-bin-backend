document.addEventListener("DOMContentLoaded", () => {
    // Membuat observer untuk memantau elemen yang masuk ke dalam layar
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            // Jika elemen sudah terlihat di area layar (viewport)
            if (entry.isIntersecting) {
                // Tambahkan class 'visible' untuk memicu animasi CSS di style.css
                entry.target.classList.add("visible");

                // Hentikan pemantauan pada elemen ini agar animasi tidak berulang-ulang
                // saat user scroll naik-turun
                observer.unobserve(entry.target);
            }
        });
    }, {
        // threshold 0.15 berarti animasi akan mulai jalan saat minimal 15%
        // bagian dari elemen tersebut sudah muncul dari bawah layar
        threshold: 0.15,
        rootMargin: "0px 0px -50px 0px" // Sedikit margin agar animasi terasa lebih natural
    });

    // Cari semua elemen HTML yang memiliki class 'fade-up'
    const hiddenElements = document.querySelectorAll(".fade-up");

    // Daftarkan setiap elemen yang ditemukan ke dalam observer
    hiddenElements.forEach((el) => observer.observe(el));
});