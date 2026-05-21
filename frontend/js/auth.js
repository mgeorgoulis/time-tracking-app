const authApi = new ApiClient();

async function getCurrentUserOrRedirect() {
    try {
        return await authApi.me();
    } catch (error) {
        authApi.clearToken();
        window.location.href = "index.html";
        return null;
    }
}

async function requireManagementAccess() {
    const user = await getCurrentUserOrRedirect();

    if (!user) {
        return null;
    }

    if (!canUseManagementMenu(user)) {
        window.location.href = "dashboard.html";
        return null;
    }

    return user;
}

async function logoutAndRedirect() {
    try {
        await authApi.logout();
    } catch (error) {
        console.warn(error.message);
    }

    authApi.clearToken();
    window.location.href = "index.html";
}

function renderManagementNav(activePage) {
    const nav = document.getElementById("management-nav");

    if (!nav) {
        return;
    }

    nav.innerHTML = `
        <a class="${activePage === "dashboard" ? "active" : ""}" href="dashboard.html">Dashboard</a>
        <a class="${activePage === "users" ? "active" : ""}" href="users.html">Benutzerverwaltung</a>
        <a class="${activePage === "create-user" ? "active" : ""}" href="create-user.html">Mitarbeiter anlegen</a>
        <a class="${activePage === "reports" ? "active" : ""}" href="reports.html">Berichte</a>
        <button id="nav-logout-button" class="secondary-button">Logout</button>
    `;

    const logoutButton = document.getElementById("nav-logout-button");

    if (logoutButton) {
        logoutButton.addEventListener("click", () => logoutAndRedirect());
    }
}

window.authApi = authApi;
window.getCurrentUserOrRedirect = getCurrentUserOrRedirect;
window.requireManagementAccess = requireManagementAccess;
window.logoutAndRedirect = logoutAndRedirect;
window.renderManagementNav = renderManagementNav;
