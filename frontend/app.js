const API_BASE_URL = "http://127.0.0.1:8000";

const ROLE_LABELS = {
    admin: "Administrator",
    executive: "Geschäftsführung",
    department_manager: "Abteilungsleiter",
    employee: "Mitarbeiter",
    apprentice: "Auszubildender"
};

function getRoleLabel(role) {
    return ROLE_LABELS[role] || role;
}

function formatUserId(userId) {
    return String(Number(userId)).padStart(4, "0");
}

function parseDisplayedUserId(value) {
    return Number(String(value).replace(/^0+/, "") || "0");
}

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

	getUsers() {
	     return this.request("/users");
	}

	createUser(userData) {
    	return this.request("/users", {
        	method: "POST",
        	body: JSON.stringify(userData)
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


    updateUserStatus(userId, isActive) {
        return this.request(`/users/${userId}/status`, {
            method: "PATCH",
            body: JSON.stringify({
                is_active: isActive
            })
        });
    }
}

class FrontendApp {
    constructor() {
        this.api = new ApiClient(API_BASE_URL);
        this.currentUser = null;
        this.forcePinChange = false;
        this.users = [];
	this.usersTableVisible = false;

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

	this.adminUsersSection = document.getElementById("admin-users-section");
	this.loadUsersButton = document.getElementById("load-users-button");
	this.usersTableWrapper = document.getElementById("users-table-wrapper");
	this.usersTableBody = document.getElementById("users-table-body");
	this.usersMessage = document.getElementById("users-message");

	this.newUserIdInput = document.getElementById("new-user-id-input");
	this.newUserFirstNameInput = document.getElementById("new-user-first-name-input");
	this.newUserLastNameInput = document.getElementById("new-user-last-name-input");
	this.newUserPinInput = document.getElementById("new-user-pin-input");
	this.newUserRoleSelect = document.getElementById("new-user-role-select");
	this.newUserDepartmentInput = document.getElementById("new-user-department-input");
	this.createUserButton = document.getElementById("create-user-button");
	this.createUserMessage = document.getElementById("create-user-message");

	this.managementMenu = document.getElementById("management-menu");
	this.mainDashboardPage = document.getElementById("main-dashboard-page");
	this.usersPage = document.getElementById("users-page");
	this.createUserPage = document.getElementById("create-user-page");
	this.reportsPage = document.getElementById("reports-page");

	this.showDashboardButton = document.getElementById("show-dashboard-button");
	this.showUsersButton = document.getElementById("show-users-button");
	this.showCreateUserButton = document.getElementById("show-create-user-button");
	this.showReportsButton = document.getElementById("show-reports-button");

	this.newUserFirstNameInput = document.getElementById("new-user-first-name-input");
	this.newUserLastNameInput = document.getElementById("new-user-last-name-input");
	this.newUserEmailInput = document.getElementById("new-user-email-input");
	this.newUserPhoneInput = document.getElementById("new-user-phone-input");
	this.newUserStreetInput = document.getElementById("new-user-street-input");
	this.newUserPostalCodeInput = document.getElementById("new-user-postal-code-input");
	this.newUserCityInput = document.getElementById("new-user-city-input");
	this.newUserCountryInput = document.getElementById("new-user-country-input");

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

	this.successModal = document.getElementById("success-modal");
	this.successModalMessage = document.getElementById("success-modal-message");
	this.successModalContinueButton = document.getElementById("success-modal-continue-button");

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

        this.loadUsersButton.addEventListener("click", () => this.handleLoadUsers());
        this.createUserButton.addEventListener("click", () => this.handleCreateUser());

	this.showDashboardButton.addEventListener("click", () => this.showAppPage("dashboard"));
	this.showUsersButton.addEventListener("click", () => this.showAppPage("users"));
	this.showCreateUserButton.addEventListener("click", () => this.showAppPage("create-user"));
	this.showReportsButton.addEventListener("click", () => this.showAppPage("reports"));

	this.successModalContinueButton.addEventListener("click", () => this.hideSuccessModal());

        this.pinInput.addEventListener("keydown", event => {
            if (event.key === "Enter") {
                this.handleLogin();
            }
        });
    }

async tryRestoreSession() {
    const wasLoggedOut = sessionStorage.getItem("wasLoggedOut");

    if (wasLoggedOut === "true") {
        sessionStorage.removeItem("wasLoggedOut");
        this.api.clearToken();
        this.showLogin();
        return;
    }

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
            window.location.replace("dashboard.html");
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
	    window.location.replace("dashboard.html");
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

async handleToggleUserStatus(button) {
    const userId = Number(button.dataset.userId);
    const isCurrentlyActive = button.dataset.isActive === "true";
    const newStatus = !isCurrentlyActive;

    const confirmationText = newStatus
        ? "Benutzer wirklich reaktivieren?"
        : "Benutzer wirklich deaktivieren?";

    if (!confirm(confirmationText)) {
        return;
    }

    try {
        const updatedUser = await this.api.updateUserStatus(userId, newStatus);

        this.usersMessage.textContent =
            `Status geändert: ${updatedUser.name} ist jetzt ${updatedUser.is_active ? "aktiv" : "inaktiv"}.`;
        this.usersMessage.className = "message success";

        await this.refreshUsers(this.usersTableVisible);
    } catch (error) {
        this.usersMessage.textContent = error.message;
        this.usersMessage.className = "message error";
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

async refreshUsers(showTable = false) {
    this.usersMessage.textContent = "";
    this.usersMessage.className = "message";

    try {
        const users = await this.api.getUsers();

        users.sort((a, b) => a.user_id - b.user_id);
        this.users = users;

        this.setNextAvailableUserId();
        this.updateUserIdAvailability();

        if (showTable) {
            this.renderUsersTable(users);
            this.usersTableWrapper.classList.remove("hidden");
        } else {
            this.usersTableWrapper.classList.add("hidden");
            this.usersTableBody.innerHTML = "";
        }
    } catch (error) {
        this.usersMessage.textContent = error.message;
        this.usersMessage.className = "message error";
    }
}

showAppPage(pageName) {
    this.mainDashboardPage.classList.add("hidden");
    this.usersPage.classList.add("hidden");
    this.createUserPage.classList.add("hidden");
    this.reportsPage.classList.add("hidden");

    if (pageName === "dashboard") {
        this.mainDashboardPage.classList.remove("hidden");
    }

    if (pageName === "users") {
        this.usersPage.classList.remove("hidden");
    }

    if (pageName === "create-user") {
        this.createUserPage.classList.remove("hidden");
        this.refreshUsers(false);
    }

    if (pageName === "reports") {
        this.reportsPage.classList.remove("hidden");
    }
}

renderUsersTable(users) {
    this.usersTableBody.innerHTML = "";

    if (users.length === 0) {
        this.usersMessage.textContent = "Keine Benutzer vorhanden.";
        return;
    }

    users.forEach(user => {
        const row = document.createElement("tr");
	const displayName = user.full_name || user.name;
        const department = user.department || "—";
        const mustChangePin = user.must_change_pin ? "Ja" : "Nein";
        const status = user.is_active ? "Aktiv" : "Inaktiv";
        const actionLabel = user.is_active ? "Deaktivieren" : "Reaktivieren";

        row.innerHTML = `
            <td>${formatUserId(user.user_id)}</td>
            <td>${user.name}</td>
	    <td>${displayName}</td>
	    <td>${user.email || "—"}</td>
            <td>${getRoleLabel(user.role)}</td>
            <td>${department}</td>
            <td>${mustChangePin}</td>
            <td>${status}</td>
            <td>
                <button
                    class="secondary-button user-status-button"
                    data-user-id="${user.user_id}"
                    data-is-active="${user.is_active}"
                >
                    ${actionLabel}
                </button>
            </td>
        `;

        this.usersTableBody.appendChild(row);
    });

    this.usersTableBody.querySelectorAll(".user-status-button").forEach(button => {
        button.addEventListener("click", () => this.handleToggleUserStatus(button));
    });
}

async handleLoadUsers() {
    this.usersTableVisible = true;
    await this.refreshUsers(true);
}


async handleCreateUser() {
    this.createUserMessage.textContent = "";
    this.createUserMessage.className = "message";

    await this.refreshUsers(this.usersTableVisible);

	const rawUserId = this.newUserIdInput.value.trim();
	const userId = parseDisplayedUserId(rawUserId);
	const firstName = this.newUserFirstNameInput.value.trim();
	const lastName = this.newUserLastNameInput.value.trim();
	const pinCode = this.newUserPinInput.value;
	const role = this.newUserRoleSelect.value;
	const department = this.newUserDepartmentInput.value.trim();

	const email = this.newUserEmailInput.value.trim();
	const phone = this.newUserPhoneInput.value.trim();
	const street = this.newUserStreetInput.value.trim();
	const postalCode = this.newUserPostalCodeInput.value.trim();
	const city = this.newUserCityInput.value.trim();
	const country = this.newUserCountryInput.value.trim();


    if (!Number.isInteger(userId) || userId <= 0) {
        this.createUserMessage.textContent = "Die Personal-ID muss größer als 0 sein.";
        this.createUserMessage.className = "message error";
        return;
    }

    if (this.isUserIdAlreadyAssigned(userId)) {
        this.createUserMessage.textContent = `Die Personal-ID ${formatUserId(userId)} ist bereits vergeben.`;
        this.createUserMessage.className = "message error";
        return;
    }

    if (!firstName) {
	    this.createUserMessage.textContent = "Bitte einen Vornamen eingeben.";
	    this.createUserMessage.className = "message error";
	    return;
     }

    if (!/^\d{4}$/.test(pinCode)) {
        this.createUserMessage.textContent = "Der Start-PIN muss genau 4 Ziffern enthalten.";
        this.createUserMessage.className = "message error";
        return;
    }

    if (["employee", "apprentice", "department_manager"].includes(role) && !department) {
        this.createUserMessage.textContent = "Für diese Rolle muss eine Abteilung angegeben werden.";
        this.createUserMessage.className = "message error";
        return;
    }

	const userData = {
	    user_id: userId,
	    first_name: firstName,
	    last_name: lastName,
	    pin_code: pinCode,
	    role,
	    department: department || null,
	    email: email || null,
	    phone: phone || null,
	    street: street || null,
	    postal_code: postalCode || null,
	    city: city || null,
	    country: country || null
	};

    try {
	const user = await this.api.createUser(userData);

	const fullName = user.full_name || user.name;
	const personnelId = formatUserId(user.user_id);

	this.clearCreateUserForm();
	await this.refreshUsers(this.usersTableVisible);

	this.showSuccessModal(
	    `${fullName} wurde erfolgreich mit der Personalnr. ${personnelId} im System hinterlegt.`
	);

    } catch (error) {
        this.createUserMessage.textContent = error.message;
        this.createUserMessage.className = "message error";
    }
}

clearCreateUserForm() {
	this.newUserFirstNameInput.value = "";
	this.newUserLastNameInput.value = "";
	this.newUserEmailInput.value = "";
	this.newUserPhoneInput.value = "";
	this.newUserStreetInput.value = "";
	this.newUserPostalCodeInput.value = "";
	this.newUserCityInput.value = "";
	this.newUserCountryInput.value = "Deutschland";

    if (this.currentUser.role === "department_manager") {
        this.newUserDepartmentInput.value = this.currentUser.department || "";
    } else {
        this.newUserDepartmentInput.value = "";
    }

    this.setNextAvailableUserId();
    this.updateUserIdAvailability();
}

isUserIdAlreadyAssigned(userId) {
    return this.users.some(user => Number(user.user_id) === Number(userId));
}

getNextAvailableUserId() {
    const usedIds = new Set(this.users.map(user => Number(user.user_id)));

    let nextId = 1;

    while (usedIds.has(nextId)) {
        nextId += 1;
    }

    return nextId;
}

setNextAvailableUserId() {
    const nextId = this.getNextAvailableUserId();
    this.newUserIdInput.value = nextId;
}

updateUserIdAvailability() {
    const userId = Number(this.newUserIdInput.value);

    if (!userId) {
        return;
    }

    if (this.isUserIdAlreadyAssigned(userId)) {
        this.createUserMessage.textContent = `Die Personal-ID ${userId} ist bereits vergeben.`;
        this.createUserButton.disabled = true;
    } else {
        this.createUserMessage.textContent = "";
        this.createUserButton.disabled = false;
    }
}

isUserIdAlreadyAssigned(userId) {
    return this.users.some(user => Number(user.user_id) === Number(userId));
}

getNextAvailableUserId() {
    const usedIds = new Set(
        this.users
            .map(user => Number(user.user_id))
            .filter(userId => userId > 0)
    );

    let nextId = 1;

    while (usedIds.has(nextId)) {
        nextId += 1;
    }

    return nextId;
}

setNextAvailableUserId() {
    const nextId = this.getNextAvailableUserId();
    this.newUserIdInput.value = formatUserId(nextId);
}

updateUserIdAvailability() {
    const userId = parseDisplayedUserId(this.newUserIdInput.value);

    if (!Number.isInteger(userId) || userId <= 0) {
        this.createUserMessage.textContent = "Die Personal-ID muss größer als 0 sein.";
        this.createUserMessage.className = "message error";
        this.createUserButton.disabled = true;
        return;
    }

    if (this.isUserIdAlreadyAssigned(userId)) {
        this.createUserMessage.textContent = `Die Personal-ID ${formatUserId(userId)} ist bereits vergeben.`;
        this.createUserMessage.className = "message error";
        this.createUserButton.disabled = true;
        return;
    }

    this.createUserButton.disabled = false;
}

clearCreateUserForm() {
    this.newUserFirstNameInput.value = "";
    this.newUserLastNameInput.value = "";
    this.newUserPinInput.value = "";
    this.newUserRoleSelect.value = "employee";

    this.newUserEmailInput.value = "";
    this.newUserPhoneInput.value = "";
    this.newUserStreetInput.value = "";
    this.newUserPostalCodeInput.value = "";
    this.newUserCityInput.value = "";
    this.newUserCountryInput.value = "Deutschland";

    if (this.currentUser.role === "department_manager") {
        this.newUserDepartmentInput.value = this.currentUser.department || "";
    } else {
        this.newUserDepartmentInput.value = "";
    }

    this.createUserMessage.textContent = "";
    this.createUserMessage.className = "message";

    this.setNextAvailableUserId();
    this.updateUserIdAvailability();
}

showSuccessModal(message) {
    this.successModalMessage.textContent = message;
    this.successModal.classList.remove("hidden");
}

hideSuccessModal() {
    this.successModal.classList.add("hidden");
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

updateRoleOptionsForCurrentUser() {
    const roleOptionsByUserRole = {
        admin: [
            ["employee", "Mitarbeiter"],
            ["apprentice", "Auszubildender"],
            ["department_manager", "Abteilungsleiter"],
            ["executive", "Geschäftsführung"],
            ["admin", "Administrator"]
        ],
        executive: [
            ["employee", "Mitarbeiter"],
            ["apprentice", "Auszubildender"],
            ["department_manager", "Abteilungsleiter"]
        ]
    };

    const options = roleOptionsByUserRole[this.currentUser.role] || [];

    this.newUserRoleSelect.innerHTML = "";

    options.forEach(([value, label]) => {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = label;
        this.newUserRoleSelect.appendChild(option);
    });
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
        this.userInfo.textContent = `${this.currentUser.name} · ${getRoleLabel(this.currentUser.role)} · ${department}`;

	if (["admin", "executive"].includes(this.currentUser.role)) {
	    this.managementMenu.classList.remove("hidden");
	    this.updateRoleOptionsForCurrentUser();
	    this.refreshUsers(false);
	} else {
	    this.managementMenu.classList.add("hidden");
	}

	this.showAppPage("dashboard");
	this.updateDailyBreaks();
	}
     }

document.addEventListener("DOMContentLoaded", () => {
    new FrontendApp();
});
