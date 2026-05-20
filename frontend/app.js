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

    changePin(currentPin, newPin, confirmPin) {
        return this.request("/change-pin", {
            method: "POST",
            body: JSON.stringify({
                current_pin: currentPin,
                new_pin: newPin,
                confirm_pin: confirmPin
            })
        });
    }

    clockIn() {
        return this.request("/clock-in", {
            method: "POST"
        });
    }

    startBreak() {
        return this.request("/break/start", {
            method: "POST"
        });
    }

    endBreak() {
        return this.request("/break/end", {
            method: "POST"
        });
    }

    dailyBreaks(year, month, day) {
        const params = new URLSearchParams({
            year,
            month,
            day
        });

        return this.request(`/breaks/daily?${params.toString()}`);
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
        this.forcePinChange = false;

        this.loginView = document.getElementById("login-view");
        this.changePinView = document.getElementById("change-pin-view");
        this.dashboardView = document.getElementById("dashboard-view");

        this.userIdInput = document.getElementById("user-id-input");
        this.pinInput = document.getElementById("pin-input");
        this.loginButton = document.getElementById("login-button");
        this.loginError = document.getElementById("login-error");

        this.changePinTitle = document.getElementById("change-pin-title");
        this.changePinDescription = document.getElementById("change-pin-description");
        this.currentPinInput = document.getElementById("current-pin-input");
        this.newPinInput = document.getElementById("new-pin-input");
        this.confirmPinInput = document.getElementById("confirm-pin-input");
        this.changePinButton = document.getElementById("change-pin-button");
        this.cancelChangePinButton = document.getElementById("cancel-change-pin-button");
        this.changePinError = document.getElementById("change-pin-error");

        this.userInfo = document.getElementById("user-info");
        this.logoutButton = document.getElementById("logout-button");
        this.openChangePinButton = document.getElementById("open-change-pin-button");

        this.statusText = document.getElementById("status-text");
        this.actionMessage = document.getElementById("action-message");

        this.clockInButton = document.getElementById("clock-in-button");
        this.breakStartButton = document.getElementById("break-start-button");
        this.breakEndButton = document.getElementById("break-end-button");
        this.clockOutButton = document.getElementById("clock-out-button");
        this.dailyBreakMinutes = document.getElementById("daily-break-minutes");

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
        this.openChangePinButton.addEventListener("click", () => this.showChangePin(false));
        this.changePinButton.addEventListener("click", () => this.handleChangePin());
        this.cancelChangePinButton.addEventListener("click", () => this.showDashboard());

        this.clockInButton.addEventListener("click", () => this.handleClockIn());
        this.breakStartButton.addEventListener("click", () => this.handleBreakStart());
        this.breakEndButton.addEventListener("click", () => this.handleBreakEnd());
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

            if (user.must_change_pin) {
                this.showChangePin(true);
            } else {
                this.showDashboard();
            }
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

            const me = await this.api.me();
            this.currentUser = me;

            if (response.must_change_pin || me.must_change_pin) {
                this.showChangePin(true);
            } else {
                this.showDashboard();
            }
        } catch (error) {
            this.loginError.textContent = error.message;
        }
    }

    async handleChangePin() {
        this.changePinError.textContent = "";

        try {
            const response = await this.api.changePin(
                this.currentPinInput.value,
                this.newPinInput.value,
                this.confirmPinInput.value
            );

            this.clearPinChangeFields();

            const me = await this.api.me();
            this.currentUser = me;
            this.currentUser.must_change_pin = response.must_change_pin;

            this.actionMessage.textContent = response.message;
            this.showDashboard();
        } catch (error) {
            this.changePinError.textContent = error.message;
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

    async handleBreakStart() {
        try {
            const response = await this.api.startBreak();
            this.statusText.textContent = "In Pause";
            this.actionMessage.textContent = `${response.message} Eintrag-ID: ${response.entry_id}`;
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleBreakEnd() {
        try {
            const response = await this.api.endBreak();
            this.statusText.textContent = "Eingestempelt";
            this.actionMessage.textContent = `${response.message} Gesamtpause: ${response.total_break_minutes} Minuten`;
            await this.updateDailyBreaks();
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleClockOut() {
        try {
            const response = await this.api.clockOut();
            this.statusText.textContent = "Nicht eingestempelt";
            this.actionMessage.textContent = `${response.message} Gearbeitete Minuten: ${response.worked_minutes}`;
            await this.updateDailyBreaks();
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

            this.reportOutput.textContent = this.formatMonthlyReport(report);
        } catch (error) {
            this.reportOutput.textContent = error.message;
        }
    }

    formatMonthlyReport(report) {
        const department = report.department || "keine Abteilung";
        const confirmedText = report.confirmed ? "Ja" : "Nein";
        const confirmedAt = report.confirmed_at || "Noch nicht quittiert";
        const confirmationMethod = report.confirmation_method || "Keine";

        return [
            "Monatsbericht Arbeitszeit",
            "=========================",
            "",
            `Mitarbeiter: ${report.employee_name}`,
            `Mitarbeiter-ID: ${report.employee_id}`,
            `Abteilung: ${department}`,
            `Zeitraum: ${String(report.month).padStart(2, "0")}/${report.year}`,
            "",
            `Soll-Zeit: ${report.expected_time} Stunden`,
            `Ist-Zeit: ${report.worked_time} Stunden`,
            `Pausenzeit: ${report.break_time || "00:00"} Stunden`,
            `Saldo: ${report.overtime_time} Stunden`,
            "",
            `Quittiert: ${confirmedText}`,
            `Quittiert am: ${confirmedAt}`,
            `Quittierungsmethode: ${confirmationMethod}`,
            "",
            "Unterschrift Mitarbeiter:",
            "",
            "____________________________"
        ].join("\n");
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

    async updateDailyBreaks() {
        if (!this.currentUser) {
            return;
        }

        const now = new Date();

        try {
            const response = await this.api.dailyBreaks(
                now.getFullYear(),
                now.getMonth() + 1,
                now.getDate()
            );

            this.dailyBreakMinutes.textContent = response.break_minutes;
        } catch (error) {
            console.warn(error.message);
        }
    }

    clearPinChangeFields() {
        this.currentPinInput.value = "";
        this.newPinInput.value = "";
        this.confirmPinInput.value = "";
    }

    showLogin() {
        this.dashboardView.classList.add("hidden");
        this.changePinView.classList.add("hidden");
        this.loginView.classList.remove("hidden");
        this.pinInput.value = "";
    }

    showChangePin(forceChange) {
        this.forcePinChange = forceChange;

        this.loginView.classList.add("hidden");
        this.dashboardView.classList.add("hidden");
        this.changePinView.classList.remove("hidden");

        this.clearPinChangeFields();
        this.changePinError.textContent = "";

        if (forceChange) {
            this.changePinTitle.textContent = "PIN-Wechsel erforderlich";
            this.changePinDescription.textContent = "Du musst deinen Start-PIN ändern, bevor du die App nutzen kannst.";
            this.cancelChangePinButton.classList.add("hidden");
        } else {
            this.changePinTitle.textContent = "PIN ändern";
            this.changePinDescription.textContent = "Du kannst deinen PIN jederzeit ändern.";
            this.cancelChangePinButton.classList.remove("hidden");
        }
    }

    showDashboard() {
        if (this.currentUser && this.currentUser.must_change_pin) {
            this.showChangePin(true);
            return;
        }

        this.loginView.classList.add("hidden");
        this.changePinView.classList.add("hidden");
        this.dashboardView.classList.remove("hidden");

        const department = this.currentUser.department || "keine Abteilung";
        this.userInfo.textContent = `${this.currentUser.name} · ${this.currentUser.role} · ${department}`;

        this.updateDailyBreaks();
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new FrontendApp();
});
