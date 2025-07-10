document.addEventListener('DOMContentLoaded', function () {
    document.querySelector('#login-form').addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        const response = await fetch(this.action, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        if (result.success) {
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
                window.location.href = result.redirect;
            });
        } else {
            const flashContainer = document.querySelector('.flash-messages');
            flashContainer.innerHTML = `<div class="messagetxt ${result.category}">${result.message}</div>`;
        }
    });
});
