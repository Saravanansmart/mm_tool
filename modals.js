function openModal(id) {
    document.getElementById(id).classList.add('show');
    if (typeof gtag === 'function') gtag('event', 'open_modal', { event_category: 'Modal', event_label: id });
}
function closeModal(id) {
    document.getElementById(id).classList.remove('show');
}
document.querySelectorAll('.mm-modal').forEach(m => {
    m.addEventListener('click', e => { if (e.target === m) m.classList.remove('show'); });
});
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') document.querySelectorAll('.mm-modal.show').forEach(m => m.classList.remove('show'));
});
