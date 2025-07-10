function toggleMenu1() {
    const menu = document.getElementById("settingsMenu");
    const toggleBtn = document.getElementById("settingsToggleBtn");

    menu.classList.toggle("active");

    toggleBtn.classList.toggle("active");

    if (menu.classList.contains("active")) {
        toggleBtn.textContent = '✕';
    } else {
        toggleBtn.textContent = '☰';
    }
}

document.addEventListener('click', function (e) {
    const menu = document.getElementById('settingsMenu');
    const toggleBtn = document.getElementById('settingsToggleBtn');

    if (!menu.contains(e.target) && e.target !== toggleBtn) {
        menu.classList.remove('active');
        toggleBtn.classList.remove('active');
        toggleBtn.textContent = '☰';
    }
});



function toggleMenu2() {
    const mobileMenu = document.getElementById('mobileMenu');
    mobileMenu.classList.toggle('active');
}

document.addEventListener('click', function(event) {
    const mobileMenu = document.getElementById('mobileMenu');
    const menuButton = document.querySelector('.menu-icon2');

    if (!mobileMenu.contains(event.target) && !menuButton.contains(event.target)) {
        mobileMenu.classList.remove('active');
    }
});

