class DashboardPage {
    constructor() {
        this.api = authApi;
        this.currentUser = null;

        this.userInfo = document.getElementById("user-info");
        this.logoutButton = document.getElementById("logout-button");
        this.changePinButton = document.getElementById("change-pin-button");

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

        this.auditLogSection = document.getElementById("audit-log-section");
        this.loadAuditLogButton = document.getElementById("load-audit-log-button");
        this.auditLogList = document.getElementById("audit-log-list");
        this.auditLogMessage = document.getElementById("audit-log-message");

        this.setupDefaultDate();
        this.bindEvents();
        this.initialize();
    }

    setupDefaultDate() {
        const now = new Date();
        this.reportYearInput.value = now.getFullYear();
        this.reportMonthInput.value = now.getMonth() + 1;
    }

    bindEvents() {
        this.logoutButton.addEventListener("click", () => logoutAndRedirect());

        this.changePinButton.addEventListener("click", () => {
             navigateWithinApp("change-pin.html");
        });

        this.clockInButton.addEventListener("click", () => this.handleClockIn());
        this.breakStartButton.addEventListener("click", () => this.handleBreakStart());
        this.breakEndButton.addEventListener("click", () => this.handleBreakEnd());
        this.clockOutButton.addEventListener("click", () => this.handleClockOut());

        this.loadReportButton.addEventListener("click", () => this.handleLoadReport());
        this.loadAuditLogButton.addEventListener("click", () => this.handleLoadAuditLog());
    }

    async initialize() {
        const user = await getCurrentUserOrRedirect();

        if (!user) {
            return;
        }

        this.currentUser = user;

        if (user.must_change_pin) {
           navigateWithinApp("change-pin.html");
            return;
        }

        this.renderUserInfo();
        this.renderManagementNavigation();
        await this.updateDailyBreaks();

        this.statusText.textContent = "Bereit";
        revealProtectedPage();
    }

    renderUserInfo() {
        const department = this.currentUser.department || "keine Abteilung";

        this.userInfo.textContent =
            `${this.currentUser.full_name || this.currentUser.name} · ${getRoleLabel(this.currentUser.role)} · ${department}`;
    }

    renderManagementNavigation() {
        if (canUseManagementMenu(this.currentUser)) {
            renderManagementNav("dashboard");

            const nav = document.getElementById("management-nav");

            if (nav) {
                nav.classList.remove("hidden");
            }

            this.auditLogSection.classList.remove("hidden");
        }
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
            this.actionMessage.textContent =
                `${response.message} Gesamtpause: ${response.total_break_minutes} Minuten`;

            await this.updateDailyBreaks();
        } catch (error) {
            this.actionMessage.textContent = error.message;
        }
    }

    async handleClockOut() {
        try {
            const response = await this.api.clockOut();
            this.statusText.textContent = "Nicht eingestempelt";
            this.actionMessage.textContent =
                `${response.message} Gearbeitete Minuten: ${response.worked_minutes}`;

            await this.updateDailyBreaks();
        } catch (error) {
            this.actionMessage.textContent = error.message;
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
            `Mitarbeiter-ID: ${formatUserId(report.employee_id)}`,
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
                listItem.textContent =
                    `${entry.created_at} · ${entry.action} · Benutzer ${formatUserId(entry.actor_id)}`;

                this.auditLogList.appendChild(listItem);
            });
        } catch (error) {
            this.auditLogMessage.textContent = error.message;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new DashboardPage();
});
