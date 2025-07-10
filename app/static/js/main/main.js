document.addEventListener("DOMContentLoaded", function () {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add("show");

        if (entry.target.classList.contains('benefit-item')) {
          anime({
            targets: '.benefit-item',
            opacity: [0, 1],
            translateY: [-50, 0],
            easing: 'easeOutQuad',
            duration: 1000,
            delay: anime.stagger(500, { start: 100 })
          });
          observer.unobserve(entry.target);
        }
      }
    });
  }, { threshold: 0.3 });

  document.querySelectorAll(".main-container, .text-content, .text-content-two, .image-container,.image-container-two, .benefit-item").forEach(el => {
    observer.observe(el);
  });
});

