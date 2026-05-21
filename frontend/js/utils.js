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
