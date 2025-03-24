function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

document.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    const openBtn = document.querySelector('.open-btn');
    
    if (!sidebar.contains(event.target) && 
        !openBtn.contains(event.target) && 
        sidebar.classList.contains('open')) {
        toggleSidebar();
    }
});

document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const sidebar = document.getElementById('sidebar');
        if (sidebar.classList.contains('open')) {
            toggleSidebar();
        }
    }
});