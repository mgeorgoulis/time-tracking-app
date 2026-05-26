const authApi = new ApiClient();

const PROTECTED_PAGES = [
    "dashboard.html",
    "users.html",
    "create-user.html",
    "user-profile.html",
    "reports.html",
    "change-pin.html"
];

function getCurrentPageName() {
    return window.location.pathname.split("/").pop() || "index.html";
}

function isProtectedPage() {
    return PROTECTED_PAGES.includes(getCurrentPageName());
}

function hideProtectedPage() {
    document.body.classList.remove("auth-ready");
    document.body.classList.add("auth-locked");
}

function revealProtectedPage() {
    document.body.classList.remove("auth-locked");
    document.body.classList.add("auth-ready");
}

function navigateWithinApp(url, replace = false) {
    sessionStorage.setItem("internalNavigation", "true");

    if (replace) {
        window.location.replace(url);
        return;
    }

    window.location.href = url;
}

function clearSessionLocally() {
    authApi.clearToken();
    sessionStorage.setItem("wasLoggedOut", "true");
}

function logoutBestEffort() {
    if (!authApi.token) {
        return;
    }

    try {
        fetch(`${authApi.baseUrl}/logout`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authApi.token}`
            },
            body: "{}",
            keepalive: true
        });
    } catch (error) {
        console.warn(error.message);
    }
}

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
        navigateWithinApp("dashboard.html", true);
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

    clearSessionLocally();
    window.location.replace("index.html");
}

function renderManagementNav(activePage) {
    const nav = document.getElementById("management-nav");

    if (!nav) {
        return;
    }

    nav.innerHTML = `
        <a class="${activePage === "dashboard" ? "active" : ""}" href="dashboard.html" data-nav-url="dashboard.html">Dashboard</a>
        <a class="${activePage === "users" ? "active" : ""}" href="users.html" data-nav-url="users.html">Benutzerverwaltung</a>
        <a class="${activePage === "create-user" ? "active" : ""}" href="create-user.html" data-nav-url="create-user.html">Mitarbeiter anlegen</a>
        <a class="${activePage === "reports" ? "active" : ""}" href="reports.html" data-nav-url="reports.html">Berichte</a>
        <button id="nav-logout-button" class="secondary-button">Logout</button>
    `;

    nav.querySelectorAll("a[data-nav-url]").forEach(link => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            navigateWithinApp(link.dataset.navUrl);
        });
    });

    const logoutButton = document.getElementById("nav-logout-button");

    if (logoutButton) {
        logoutButton.addEventListener("click", () => logoutAndRedirect());
    }
}


window.addEventListener("pageshow", async () => {
    if (!isProtectedPage()) {
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

function hideProtectedPage() {
    document.body.classList.remove("auth-ready");
    document.body.classList.add("auth-locked");
}

function revealProtectedPage() {
    document.body.classList.remove("auth-locked");
    document.body.classList.add("auth-ready");
}

window.addEventListener("beforeunload", () => {
    if (!isProtectedPage()) {
        return;
    }

    const isInternalNavigation = sessionStorage.getItem("internalNavigation") === "true";

    if (isInternalNavigation) {
        sessionStorage.removeItem("internalNavigation");
        return;
    }

    logoutBestEffort();
    clearSessionLocally();
});

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
