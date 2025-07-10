if (!sessionStorage.getItem('authChecked')) {
  fetch('/check_auth')
    .then(response => response.json())
    .then(data => {
      if (data.status === 'authorized') {
        showUserInfo(data.user);
      }
      sessionStorage.setItem('authChecked', 'true');
    })
    .catch(err => {
      console.error('Ошибка авторизации:', err);
      sessionStorage.setItem('authChecked', 'true');
    });
}

function showUserInfo(user) {
  const userInfo = document.getElementById('user-info');
  const avatar = document.getElementById('avatar');
  const username = document.getElementById('username');

  avatar.style.backgroundImage = `url('${user.avatar}')`;
  username.textContent = user.name;

  userInfo.classList.add('show');
  avatar.classList.add('slide-left');

  setTimeout(() => {
    const blockWidth = userInfo.offsetWidth;
    const avatarWidth = avatar.offsetWidth;
    const padding = 10;

    const shift = blockWidth - avatarWidth - padding;

    avatar.style.setProperty('--avatar-shift', `${shift}px`);

    avatar.classList.remove('slide-left');
    avatar.classList.add('slide-right');
  }, 300);

  setTimeout(() => {
    username.classList.add('visible');
    const spinner = document.createElement('div');
    spinner.className = 'auto-login-spinner';
    avatar.appendChild(spinner);
  }, 800);

  setTimeout(() => {
    username.classList.remove('visible');
    const spinner = avatar.querySelector('.auto-login-spinner');
    if (spinner) avatar.removeChild(spinner);
    avatar.classList.remove('slide-right');
    avatar.classList.add('slide-left');
  }, 2800);

  setTimeout(() => {
    userInfo.classList.add('hide');
  }, 3600);

  setTimeout(() => {
    userInfo.classList.remove('show', 'hide');
    avatar.classList.remove('slide-left', 'slide-right');
  }, 4200);
}

