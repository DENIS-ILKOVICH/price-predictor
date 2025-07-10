document.addEventListener('DOMContentLoaded', function () {
        const settingsBtn = document.getElementById('settings-btn');
        const gearImg = settingsBtn.querySelector('img');

        let currentRotation = 0;

        settingsBtn.addEventListener('click', () => {
            currentRotation += 180;
            gearImg.style.setProperty('--rotation', `${currentRotation}deg`);
        });

        gearImg.style.setProperty('--rotation', `0deg`);
    });