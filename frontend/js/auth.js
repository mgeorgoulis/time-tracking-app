const authApi = new ApiClient();

async function getCurrentUserOrRedirect() {
    if (!authApi.token) {
        hideProtectedPage();
        window.location.replace("index.html");
        return null;
    }

    try {
        return await authApi.me();
    } catch (error) {
        authApi.clearToken();
        hideProtectedPage();
        window.location.replace("index.html");
        return null;
    }
}

async function requireManagementAccess() {
    const user = await getCurrentUserOrRedirect();

    if (!user) {
        return null;
    }

    if (!canUseManagementMenu(user)) {
        hideProtectedPage();
        window.location.replace("dashboard.html");
        return null;
    }

    return user;
}

async function logoutAndRedirect() {
    hideProtectedPage();

    try {
        await authApi.logout();
    } catch (error) {
        console.warn(error.message);
    }

    authApi.clearToken();
    sessionStorage.setItem("wasLoggedOut", "true");

    window.location.replace("index.html");
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

window.addEventListener("pageshow", async (event) => {
    const protectedPages = [
        "dashboard.html",
        "users.html",
        "create-user.html",
        "user-profile.html",
        "reports.html"
    ];

    const currentPage = window.location.pathname.split("/").pop();

    if (!protectedPages.includes(currentPage)) {
        return;
    }

    if (!authApi.token) {
        window.location.replace("index.html");
        return;
    }

    try {
        await authApi.me();
    } catch (error) {
        authApi.clearToken();
        window.location.replace("index.html");
    }
});

function hideProtectedPage() {
    document.body.classList.remove("auth-ready");
    document.body.classList.add("auth-locked");
}

function revealProtectedPage() {
    document.body.classList.remove("auth-locked");
    document.body.classList.add("auth-ready");
}

window.authApi = authApi;
window.getCurrentUserOrRedirect = getCurrentUserOrRedirect;
window.requireManagementAccess = requireManagementAccess;
window.logoutAndRedirect = logoutAndRedirect;
window.renderManagementNav = renderManagementNav;
window.hideProtectedPage = hideProtectedPage;
window.revealProtectedPage = revealProtectedPage;
window.addEventListener("pageshow", async () => {
    const protectedPages = [
        "dashboard.html",
        "users.html",
        "create-user.html",
        "user-profile.html",
        "reports.html"
    ];

    const currentPage = window.location.pathname.split("/").pop();

    if (!protectedPages.includes(currentPage)) {
        return;
    }

    hideProtectedPage();

    if (!authApi.token) {
        window.location.replace("index.html");
        return;
    }

    try {
        await authApi.me();
        revealProtectedPage();
    } catch (error) {
        authApi.clearToken();
        window.location.replace("index.html");
    }
});
