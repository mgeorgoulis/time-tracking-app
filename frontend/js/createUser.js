class CreateUserPage {
    constructor() {
        this.api = authApi;
        this.currentUser = null;
        this.users = [];

        this.userInfo = document.getElementById("user-info");

        this.newUserIdInput = document.getElementById("new-user-id-input");
        this.newUserFirstNameInput = document.getElementById("new-user-first-name-input");
        this.newUserLastNameInput = document.getElementById("new-user-last-name-input");
        this.newUserPinInput = document.getElementById("new-user-pin-input");
	preparePinInput(this.newUserPinInput, "Start-PIN");
        this.newUserRoleSelect = document.getElementById("new-user-role-select");
        this.newUserDepartmentInput = document.getElementById("new-user-department-input");
        this.newUserEmailInput = document.getElementById("new-user-email-input");
        this.newUserPhoneInput = document.getElementById("new-user-phone-input");
        this.newUserStreetInput = document.getElementById("new-user-street-input");
        this.newUserPostalCodeInput = document.getElementById("new-user-postal-code-input");
        this.newUserCityInput = document.getElementById("new-user-city-input");
        this.newUserCountryInput = document.getElementById("new-user-country-input");

        this.createUserButton = document.getElementById("create-user-button");
        this.createUserMessage = document.getElementById("create-user-message");

        this.successModal = document.getElementById("success-modal");
        this.successModalMessage = document.getElementById("success-modal-message");
        this.successModalContinueButton = document.getElementById("success-modal-continue-button");

        this.bindEvents();
        this.initialize();
    }

    bindEvents() {
        this.createUserButton.addEventListener("click", () => this.handleCreateUser());
        this.successModalContinueButton.addEventListener("click", () => this.hideSuccessModal());
    }

    async initialize() {
        const user = await requireManagementAccess();

        if (!user) {
            return;
        }
	
	this.currentUser = user;
	this.renderHeader();
	renderManagementNav("create-user");
	this.updateRoleOptionsForCurrentUser();
	this.populateDepartmentOptions();

	await this.refreshUsers();

        revealProtectedPage();
    }

    renderHeader() {
        const department = this.currentUser.department || "keine Abteilung";

        this.userInfo.textContent =
            `${this.currentUser.full_name || this.currentUser.name} · ${getRoleLabel(this.currentUser.role)} · ${department}`;
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

populateDepartmentOptions() {
    const departments = [
        "Produktion",
        "Design",
        "Montage",
        "Office",
        "Geschäftsführung"
    ];

    this.newUserDepartmentInput.innerHTML = "";

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = "Abteilung auswählen";
    this.newUserDepartmentInput.appendChild(placeholderOption);

    departments.forEach(department => {
        const option = document.createElement("option");
        option.value = department;
        option.textContent = department;
        this.newUserDepartmentInput.appendChild(option);
    });
}

    async refreshUsers() {
        this.createUserMessage.textContent = "";
        this.createUserMessage.className = "message";

        try {
            const users = await this.api.getUsers();
            users.sort((a, b) => a.user_id - b.user_id);
            this.users = users;

            this.setNextAvailableUserId();
            this.updateUserIdAvailability();
        } catch (error) {
            this.createUserMessage.textContent = error.message;
            this.createUserMessage.className = "message error";
        }
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

    isUserIdAlreadyAssigned(userId) {
        return this.users.some(user => Number(user.user_id) === Number(userId));
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

    async handleCreateUser() {
        this.createUserMessage.textContent = "";
        this.createUserMessage.className = "message";

        await this.refreshUsers();

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
            this.createUserMessage.textContent =
                `Die Personal-ID ${formatUserId(userId)} ist bereits vergeben.`;
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
            await this.refreshUsers();

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
        this.newUserPinInput.value = "";
        this.newUserRoleSelect.value = "employee";

        this.newUserEmailInput.value = "";
        this.newUserPhoneInput.value = "";
        this.newUserStreetInput.value = "";
        this.newUserPostalCodeInput.value = "";
        this.newUserCityInput.value = "";
        this.newUserCountryInput.value = "Deutschland";
        this.newUserDepartmentInput.value = "";

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
}

document.addEventListener("DOMContentLoaded", () => {
    new CreateUserPage();
});
