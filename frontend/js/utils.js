function formatUserId(userId) {
    return String(Number(userId)).padStart(4, "0");
}

function parseDisplayedUserId(value) {
    return Number(String(value).replace(/^0+/, "") || "0");
}

function formatNullable(value, fallback = "—") {
    return value || fallback;
}

window.formatUserId = formatUserId;
window.parseDisplayedUserId = parseDisplayedUserId;
window.formatNullable = formatNullable;

function preparePinInput(input, placeholder = "4-stelliger PIN") {
    if (!input) {
        return;
    }

    const randomName = `pin_${Math.random().toString(36).slice(2)}`;

    input.type = "password";
    input.value = "";
    input.defaultValue = "";
    input.name = randomName;
    input.placeholder = placeholder;

    input.setAttribute("autocomplete", "new-password");
    input.setAttribute("autocorrect", "off");
    input.setAttribute("autocapitalize", "off");
    input.setAttribute("spellcheck", "false");
    input.setAttribute("inputmode", "numeric");
    input.setAttribute("maxlength", "4");
    input.setAttribute("pattern", "\\d{4}");
    input.setAttribute("data-lpignore", "true");
    input.setAttribute("data-1p-ignore", "true");

    input.removeAttribute("readonly");
    input.removeAttribute("disabled");

    const clearIfNotEdited = () => {
        if (!input.dataset.userEdited) {
            input.value = "";
            input.defaultValue = "";
        }
    };

    input.addEventListener("focus", () => {
        clearIfNotEdited();
    });

    input.addEventListener("click", () => {
        clearIfNotEdited();
    });

    input.addEventListener("input", () => {
        input.dataset.userEdited = "true";
        input.value = input.value.replace(/\D/g, "").slice(0, 4);
    });

    input.addEventListener("blur", () => {
        if (!input.value) {
            delete input.dataset.userEdited;
            input.placeholder = placeholder;
        }
    });

    window.setTimeout(clearIfNotEdited, 0);
    window.setTimeout(clearIfNotEdited, 150);
    window.setTimeout(clearIfNotEdited, 500);
    window.setTimeout(clearIfNotEdited, 1000);
}

window.preparePinInput = preparePinInput;
