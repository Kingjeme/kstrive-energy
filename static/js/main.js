function changeCartQuantity(inputId, amount) {
    const input = document.getElementById(inputId);

    if (!input) {
        return;
    }

    let quantity = parseInt(input.value, 10) || 1;

    const minimum = parseInt(input.min, 10) || 1;
    const maximum = parseInt(input.max, 10) || 999999;

    quantity += amount;

    if (quantity < minimum) {
        quantity = minimum;
    }

    if (quantity > maximum) {
        quantity = maximum;
    }

    input.value = quantity;
}