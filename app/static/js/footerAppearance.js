window.addEventListener('scroll', () => {
  const scrollPosition = window.scrollY + window.innerHeight;
  const triggerPoint = document.body.offsetHeight * 0.7;

  const footer = document.querySelector('.footer-container');
  if (scrollPosition >= triggerPoint) {
    footer?.classList.add('show');
  } else {
    footer?.classList.remove('show');
  }
});