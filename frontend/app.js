const API_BASE_URL = "http://127.0.0.1:8000";

class ApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.token = localStorage.getItem("timeTrackingToken");
    }

    setToken(token) {
        this.token = token;
        localStorage.setItem("timeTrackingToken", token);
    }

    clearToken() {
        this.token = null;
        localStorage.removeItem("timeTrackingToken");
    }

    async request(path, options = {}) {
        const headers = {
            "Content-Type": "application/json",
            ...(options.headers || {})
        };

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

        const response = await fetch(`${this.baseUrl}${path}`, {
            ...options,
            headers
        });

        const contentType = response.headers.get("content-type");
        const hasJson = contentType && contentType.includes("application/json");
        const data = hasJson ? await response.json() : null;

        if (!response.ok) {
            const message = data && data.detail ? data.detail : "Unbekannter API-Fehler";
            throw new Error(message);
        }

        return data;
    }

    login(userId, pinCode) {
        return this.request("/login", {
            method: "POST",
            body: JSON.stringify({
                user_id: Number(userId),
                pin_code: pinCode
            })
        });
    }

    logout() {
        return this.request("/logout", {
            method: "POST"
        });
    }

    me() {
        return this.request("/me");
    }

    clockIn() {
        return this.request("/clock-in", {
            method: "POST"
        });
    }

    addBreak(minutes) {
        return this.request("/break", {
            method: "POST",
            body: JSON.stringify({ minutes })
        });
    }

    clockOut() {
        return this.request("/clock-out", {
            method: "POST"
        });
    }

    monthlyReport(year, month, expectedMinutes) {
        const params = new URLSearchParams({
            year,
            month,
            expected_minutes: expectedMinutes
        });

        return this.request(`/report/monthly?${params.toString()}`);
    }

    auditLog() {
        return this.request("/audit-log");
    }
}

class FrontendApp {
    constructor() {
        this.api = new ApiClient(API_BASE_URL);
        this.currentUser = null;

        this.loginView = document.getElementById("login-view");
        this.dashboardView = document.getElementById("dashboard-view");

        this.userIdInput = document.getElementById("user-id-input");
        this.pinInput = document.getElementById("pin-input");
        this.loginButton = document.getElementById("login-button");
        this.loginError = document.getElementById("login-error");

        this.userInfo = document.getElementById("user-info");
        this.logoutButton = document.getElementById("logout-button");

        this.statusText = document.getElementById("status-text");
        this.actionMessage = document.getElementById("action-message");

        this.clockInButton = document.getElementById("clock-in-button");
        this.breakButton = document.getElementById("break-button");
        this.clockOutButton = document.getElementById("clock-out-button");

        this.reportYearInput = document.getElementById("report-year-input");
        this.reportMonthInput = document.getElementById("report-month-input");
        this.expectedMinutesInput = document.getElementById("expected-minutes-input");
        this.loadReportButton = document.getElementById("load-report-button");
        this.reportOutput = document.getElementById("report-output");

        this.loadAuditLogButton = document.getElementById("load-audit-log-button");
        this.auditLogList = document.getElementById("audit-log-list");
        this.auditLogMessage = document.getElementById("audit-log-message");

        this.setupDefaultDate();
        this.bindEvents();
        this.tryRestoreSession();
    }

    setupDefaultDate() {
        const now = new Date();
        this.reportYearInput.value = now.getFullYear();
        this.reportMonthInput.value = now.getMonth() + 1;
    }

    bindEvents() {
        this.loginButton.addEventListener("click", () => this.handleLogin());
        this.logoutButton.addEventListener("click", () => this.handleLogout());

        this.clockInButton.addEventListener("click", () => this.handleClockIn());
        this.breakButton.addEventListener("click", () => this.handleBreak());
        this.clockOutButton.addEventListener("click", () => this.handleClockOut());

        this.loadReportButton.addEventListener("click", () => this.handleLoadReport());
        this.loadAuditLogButton.addEventListener("click", () => this.handleLoadAuditLog());

        this.pinInput.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                this.handleLogin();
            }
        });
    }

    async tryRestoreSession() {
        if (!this.api.token) {
            this.showLogin();
            return;
        }

        try {
            const user = await this.api.me();
            this.currentUser = user;
            this.showDashboard();
        } catch (error) {
            this.api.clearToken();
            this.showLogin();
        }
    }

    async handleLogin() {
        this.loginError.textContent = "";

        try {
            const response = await this.api.login(
                this.userIdInput.value,
                this.pinInput.value
            );

            this.api.setToken(response.token);
            this.currentUser = {
                user_id: response.user_id,
                name: response.name,
                role: response.role
            };

            const me = await this.api.me();
            this.currentUser = me;

            this.showDashboard();
        } catch (error) {
            this.loginError.textContent = error.message;
        }
    }

    async handleLogout() {
        try {
            await this.api.logout();
        } catch (error) {
            console.warn(error.message);
        }

        this.api.clearToken();
        this.currentUser = null;
        this.showLogin();
    }

    async handleClockIn() {
        try {
            const response = await this.api.clockIn();
            this.statusText.textContent = "Eingestempelt";
            this.actionMessage.textContent = `${response.message} Eintrag-ID: ${response.entry_id}`;
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleBreak() {
        try {
            const response = await this.api.addBreak(30);
            this.actionMessage.textContent = `${response.message} Pausenzeit: ${response.break_minutes} Minuten`;
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleClockOut() {
        try {
            const response = await this.api.clockOut();
            this.statusText.textContent = "Nicht eingestempelt";
            this.actionMessage.textContent = `${response.message} Gearbeitete Minuten: ${response.worked_minutes}`;
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleLoadReport() {
        try {
            const report = await this.api.monthlyReport(
                this.reportYearInput.value,
                this.reportMonthInput.value,
                this.expectedMinutesInput.value
            );

            this.reportOutput.textContent = JSON.stringify(report, null, 2);
        } catch (error) {
            this.reportOutput.textContent = error.message;
        }
    }

    async handleLoadAuditLog() {
        this.auditLogMessage.textContent = "";
        this.auditLogList.innerHTML = "";

        try {
            const entries = await this.api.auditLog();

            if (entries.length === 0) {
                this.auditLogMessage.textContent = "Keine Audit-Log-Einträge vorhanden.";
                return;
            }

            entries.forEach(entry => {
                const listItem = document.createElement("li");
                listItem.textContent = `${entry.created_at} · ${entry.action} · Benutzer ${entry.actor_id}`;
                this.auditLogList.appendChild(listItem);
            });
        } catch (error) {
            this.auditLogMessage.textContent = error.message;
        }
    }

    showLogin() {
        this.dashboardView.classList.add("hidden");
        this.loginView.classList.remove("hidden");
        this.pinInput.value = "";
    }

    showDashboard() {
        this.loginView.classList.add("hidden");
        this.dashboardView.classList.remove("hidden");

        const department = this.currentUser.department || "keine Abteilung";
        this.userInfo.textContent = `${this.currentUser.name} · ${this.currentUser.role} · ${department}`;
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new FrontendApp();
});
