const faqItems = document.querySelectorAll('.faq-modern-item');

faqItems.forEach(item => {
  const btn = item.querySelector('.faq-modern-question');
  const icon = item.querySelector('.faq-icon');
  const answer = item.querySelector('.faq-modern-answer');

  btn.addEventListener('click', () => {
    const isActive = item.classList.contains('active');

    faqItems.forEach(i => {
      i.classList.remove('active');
      i.querySelector('.faq-icon').style.transform = 'rotate(0deg)';
      const ans = i.querySelector('.faq-modern-answer');
      ans.style.height = ans.scrollHeight + 'px';
      requestAnimationFrame(() => {
        ans.style.height = '0px';
        ans.style.paddingTop = '0';
      });
    });

    if (!isActive) {
      item.classList.add('active');
      icon.style.transform = 'rotate(45deg)';
      answer.style.height = 'auto';
      const fullHeight = answer.scrollHeight + 'px';
      answer.style.height = '0px';
      answer.style.paddingTop = '0';

      requestAnimationFrame(() => {
        answer.style.height = fullHeight;
        answer.style.paddingTop = '1px';
      });
    }
  });
});