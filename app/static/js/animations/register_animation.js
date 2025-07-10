document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#register-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(this);

        try {
            const response = await fetch(this.action, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            const flashContainer = document.querySelector('.flash-messages');
            flashContainer.innerHTML = '';

            if (response.ok && result.success) {
                document.getElementById('overlay').style.display = 'block';
                const container = document.getElementById('animation-container');
                container.style.display = 'block';

                const animation = lottie.loadAnimation({
                    container: container,
                    path: '/static/json_animations/login_success.json',
                    renderer: 'svg',
                    loop: false,
                    autoplay: true
                });

                animation.addEventListener('complete', () => {
                    window.location.href = result.redirect || '/dashboard';
                });
            } else {
                const errors = result.error || result.errors || [];
                if (Array.isArray(errors)) {
                    errors.forEach(err => {
                        const msg = document.createElement('div');
                        msg.className = `messagetxt ${err.category || 'warning'}`;
                        msg.textContent = err.message || 'Невідома помилка';
                        flashContainer.appendChild(msg);
                    });
                } else {
                    const msg = document.createElement('div');
                    msg.className = 'messagetxt warning';
                    msg.textContent = result.message || 'Невідома помилка';
                    flashContainer.appendChild(msg);
                }
            }
        } catch (error) {
            const flashContainer = document.querySelector('.flash-messages');
            flashContainer.innerHTML = `<div class="messagetxt danger">Помилка з'єднання з сервером. Спробуйте пізніше.</div>`;
            console.error('Registration error:', error);
        }
    });
});
