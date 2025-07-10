const backToTopButton = document.getElementById('backToTop');

function toggleButtonVisibility() {
  if (window.scrollY > 200) {
    backToTopButton.style.display = 'flex';
  } else {
    backToTopButton.style.display = 'none';
  }
}

window.addEventListener('scroll', toggleButtonVisibility);

document.getElementById("backToTop").onclick = function() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
};
