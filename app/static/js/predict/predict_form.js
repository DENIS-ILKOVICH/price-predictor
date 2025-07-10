function incrementValue(id, step) {
    const input = document.getElementById(id);
    let currentValue = parseInt(input.value, 10);
    if (isNaN(currentValue)) currentValue = 0;
    currentValue += step;
    input.value = currentValue;
}

function decrementValue(id, step) {
    const input = document.getElementById(id);
    let currentValue = parseInt(input.value, 10);
    if (isNaN(currentValue)) currentValue = 0;
    currentValue -= step;
    if (currentValue < 0) currentValue = 0;
    input.value = currentValue;
}

document.querySelectorAll('.input-button').forEach(button => {
    button.addEventListener('click', event => event.preventDefault());
});

function toggleDropdown(select) {
    const dropdown = select.querySelector('.custom-select__dropdown');
    dropdown.classList.toggle('show');
    const arrow = select.querySelector('.arrow');
    arrow.style.transform = dropdown.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
}

function selectOption(option, inputId, selectId) {
    const selectContainer = option.closest('.custom-select');
    const selectedText = selectContainer.querySelector('.selected-option');
    const value = option.textContent;
    const valueAttribute = option.getAttribute('data-value');
    selectedText.textContent = value;
    document.getElementById(inputId).value = valueAttribute;
    const select = document.getElementById(selectId);
    select.click();
}

document.addEventListener('click', function(event) {
    const select = event.target.closest('.custom-select');
    if (!select) {
        document.querySelectorAll('.custom-select__dropdown').forEach(dropdown => dropdown.classList.remove('show'));
        document.querySelectorAll('.arrow').forEach(arrow => arrow.style.transform = 'rotate(0deg)');
    }
});

function validateField(event, min, max, fieldId) {
    const field = document.getElementById(fieldId);
    const value = field.value;
    if (value === '') return;

    if (!/^\d+$/.test(value) || value < min || value > max) {
        setTimeout(() => animateDeletion(field), 1000);
    }
}

function animateDeletion(field) {
    let value = field.value;
    let index = value.length;
    const interval = setInterval(() => {
        field.value = value.substring(0, index - 1);
        index -= 1;
        if (index <= 0) {
            clearInterval(interval);
            field.value = '1';
        }
    }, 111);
}

function resetForm() {
    document.querySelectorAll('.custom-select').forEach(select => {
        const currentDisplay = select.querySelector('.selected-option');
        if (currentDisplay) currentDisplay.textContent = 'Select a value';
        const hiddenInput = select.querySelector('input[type="hidden"]');
        if (hiddenInput) hiddenInput.value = '';
    });

    document.querySelectorAll('input[type="hidden"]').forEach(input => input.value = '');
    $('#rooms').val('1');
    $('#floor').val('1');
    $('#floors').val('1');
    $('#area').val('1');

    document.querySelectorAll('textarea').forEach(textarea => textarea.value = '');
}

document.getElementById("rooms").addEventListener("input", event => validateField(event, 1, 10, "rooms"));
document.getElementById("floor").addEventListener("input", event => validateField(event, 1, 50, "floor"));
document.getElementById("floors").addEventListener("input", event => validateField(event, 1, 50, "floors"));
document.getElementById("area").addEventListener("input", event => validateField(event, 1, 400, "area"));

let logoAnimationIntervalId = null;

function showLogoAnimation() {
    const overlay = document.getElementById('logoanimationOverlay');
    overlay.classList.remove('hidden');
    document.body.classList.add('animation-active');

    const logoContainer = overlay.querySelector('.logo-container-animation');
    if (!logoContainer || logoAnimationIntervalId !== null) return;

    function restartAnimation() {
        logoContainer.remove();
        setTimeout(() => overlay.querySelector('.animation-box').appendChild(logoContainer), 20);
    }

    setTimeout(() => {
        restartAnimation();
        logoAnimationIntervalId = setInterval(restartAnimation, 2200);
    }, 2200);
}

function hideLogoAnimation() {
    const overlay = document.getElementById('logoanimationOverlay');
    overlay.classList.add('hidden');
    document.body.classList.remove('animation-active');
    if (logoAnimationIntervalId !== null) {
        clearInterval(logoAnimationIntervalId);
        logoAnimationIntervalId = null;
    }
}

const districtPrices = {
    "Kievsky": 51698.52,
    "Malinovsky": 43397.88,
    "Primorsky": 81798.01,
    "Suvorovsky": 39477.39
};

function submitFormAndClearFields(event) {
    event.preventDefault();
    validateField(event, 1, 10, "rooms");
    validateField(event, 1, 50, "floor");
    validateField(event, 1, 50, "floors");
    validateField(event, 1, 400, "area");

    showLogoAnimation();

    $.ajax({
        url: "/get_predict",
        method: 'POST',
        data: $(event.target).serialize(),
        success: function (data) {
            const predictedPrice = data.predicted_price;
            const selectedDistrict = document.getElementById("district").value;
            const area = parseFloat(document.getElementById("area").value);

            document.getElementById('predicted-price').textContent = predictedPrice.toFixed(1) + '$';

            const districtAvgPrice = districtPrices[selectedDistrict];
            document.getElementById('avg-district-price').textContent = districtAvgPrice
                ? districtAvgPrice.toFixed(1) + '$'
                : '—';

            if (!isNaN(area) && area > 0) {
                const pricePerM2 = predictedPrice / area;
                document.getElementById('area-price').textContent = pricePerM2.toFixed(1) + '$/m²';
            } else {
                document.getElementById('area-price').textContent = '—';
            }

            resetForm();
            hideLogoAnimation();
            openButton.style.display = 'block';
        },
        error: function (xhr, status, error) {
            toastr.options = {
                "closeButton": true,
                "preventDuplicates": true,
                "hideEasing": "linear",
                "escapeHtml": false
            };
            hideLogoAnimation();

            if (xhr.status === 422) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.error_list && Array.isArray(response.error_list)) {
                        const fieldMap = {
                            'district': 'District',
                            'type': 'Property Type',
                            'cond': 'Condition',
                            'walls': 'Wall Material',
                            'rooms': 'Rooms',
                            'floor': 'Floor',
                            'floors': 'Total Floors',
                            'area': 'Area'
                        };

                        let fieldErrors = [];
                        let customMessages = [];

                        response.error_list.forEach(err => {
                            const errorText = err.error;

                            if (errorText.includes('total floors cannot be less than current floor')) {
                                customMessages.push('• Total number of floors cannot be less than the floor number!');
                            } else if (errorText.includes('Illegal characters or suspicious code detected')) {
                                customMessages.push('• Suspicious characters or code detected in the description field!');
                            } else if (errorText.includes('Description must contain only English (Latin) letters and allowed symbols')) {
                                customMessages.push('• The "Description" field must contain only Latin characters and allowed symbols!');
                            } else {
                                const match = errorText.match(/field: (\w+)/i);
                                const field = match ? match[1] : null;
                                if (field) {
                                    fieldErrors.push(fieldMap[field] || field);
                                } else {
                                    customMessages.push(errorText);
                                }
                            }
                        });

                        const uniqueFields = [...new Set(fieldErrors)];
                        const fieldMessage = uniqueFields.length
                            ? 'Invalid values in fields:<br>– ' + uniqueFields.join('<br>– ')
                            : '';

                        const customMessage = customMessages.length
                            ? customMessages.join('<br>')
                            : '';

                        const fullMessage = [fieldMessage, customMessage].filter(Boolean).join('<br><br>') +
                            '<br><br><strong>Please enter valid values.</strong>';

                        toastr.error(fullMessage, 'Validation Error!');
                    } else {
                        toastr.error('Please check the entered values and try again.', 'Error!');
                    }
                } catch (e) {
                    console.error('Failed to parse error response', e);
                    toastr.error('An error occurred while processing the server response.', 'Error!');
                }
            } else {
                console.error(error);
                toastr.error('An unexpected error occurred. Please try again later.', 'Error!');
            }
        }
    });
}

$('#predict-form').on('submit', submitFormAndClearFields);

document.addEventListener('keydown', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        const form = document.getElementById('predict-form');
        if (form) {
            form.requestSubmit();
        }
    }
});
