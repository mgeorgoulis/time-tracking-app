class UserProfilePage {
    constructor() {
        this.api = authApi;
        this.currentUser = null;
        this.profileUser = null;

        this.userInfo = document.getElementById("user-info");
        this.profileTitle = document.getElementById("profile-title");
        this.profileSubtitle = document.getElementById("profile-subtitle");
        this.profileFields = document.getElementById("profile-fields");
        this.profileMessage = document.getElementById("profile-message");

        this.resetPinInput = document.getElementById("reset-pin-input");
        preparePinInput(this.resetPinInput, "Neuer Start-PIN");
        this.resetPinButton = document.getElementById("reset-pin-button");
        this.resetPinMessage = document.getElementById("reset-pin-message");

        this.editableFields = [
            ["first_name", "Vorname"],
            ["last_name", "Nachname"],
            ["department", "Abteilung"],
            ["email", "E-Mail"],
            ["phone", "Telefonnummer"],
            ["street", "Straße und Hausnummer"],
            ["postal_code", "PLZ"],
            ["city", "Ort"],
            ["country", "Land"]
        ];

        this.bindEvents();
        this.initialize();
    }

    bindEvents() {
        this.resetPinButton.addEventListener("click", () => this.handleResetPin());
    }

    async initialize() {
        const user = await requireManagementAccess();

        if (!user) {
            return;
        }

        this.currentUser = user;
        this.renderHeader();
        renderManagementNav("users");

        const userId = this.getUserIdFromUrl();

        if (!userId) {
            this.profileMessage.textContent = "Keine Benutzer-ID angegeben.";
            this.profileMessage.className = "message error";
            revealProtectedPage();
            return;
        }

        await this.loadProfile(userId);
        revealProtectedPage();
    }

    getUserIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return Number(params.get("id"));
    }

    renderHeader() {
        const department = this.currentUser.department || "keine Abteilung";

        this.userInfo.textContent =
            `${this.currentUser.full_name || this.currentUser.name} · ${getRoleLabel(this.currentUser.role)} · ${department}`;
    }

    async loadProfile(userId) {
        this.profileMessage.textContent = "";
        this.profileMessage.className = "message";

        try {
            this.profileUser = await this.api.getUser(userId);
            this.renderProfile();
        } catch (error) {
            this.profileMessage.textContent = error.message;
            this.profileMessage.className = "message error";
        }
    }

    renderProfile() {
        const displayName = this.profileUser.full_name || this.profileUser.name;

        this.profileTitle.textContent = displayName;
        this.profileSubtitle.textContent =
            `Personalnr. ${formatUserId(this.profileUser.user_id)} · ${getRoleLabel(this.profileUser.role)} · ${this.profileUser.is_active ? "Aktiv" : "Inaktiv"}`;

        this.profileFields.innerHTML = "";

        this.editableFields.forEach(([fieldName, label]) => {
            this.profileFields.appendChild(this.createEditableRow(fieldName, label));
        });
    }

    createEditableRow(fieldName, label) {
        const row = document.createElement("div");
        row.className = "profile-row";

        const value = this.profileUser[fieldName] || "";
        const displayValue = value || "—";

        row.innerHTML = `
            <div class="profile-label">${label}</div>
            <div class="profile-value">${displayValue}</div>
            <input class="profile-input hidden" type="text" value="${this.escapeHtml(value)}" />
            <button class="secondary-button edit-button">Bearbeiten</button>
            <button class="secondary-button save-button hidden">Speichern</button>
            <button class="secondary-button cancel-button hidden">Abbrechen</button>
        `;

        const valueElement = row.querySelector(".profile-value");
        const inputElement = row.querySelector(".profile-input");
        const editButton = row.querySelector(".edit-button");
        const saveButton = row.querySelector(".save-button");
        const cancelButton = row.querySelector(".cancel-button");

        editButton.addEventListener("click", () => {
            valueElement.classList.add("hidden");
            inputElement.classList.remove("hidden");
            editButton.classList.add("hidden");
            saveButton.classList.remove("hidden");
            cancelButton.classList.remove("hidden");
            inputElement.focus();
        });

        cancelButton.addEventListener("click", () => {
            inputElement.value = this.profileUser[fieldName] || "";
            valueElement.classList.remove("hidden");
            inputElement.classList.add("hidden");
            editButton.classList.remove("hidden");
            saveButton.classList.add("hidden");
            cancelButton.classList.add("hidden");
        });

        saveButton.addEventListener("click", async () => {
            await this.saveField(fieldName, inputElement.value.trim());
        });

        return row;
    }

    async saveField(fieldName, value) {
        this.profileMessage.textContent = "";
        this.profileMessage.className = "message";

        try {
            const updatedUser = await this.api.updateUserProfile(
                this.profileUser.user_id,
                {
                    [fieldName]: value || null
                }
            );

            this.profileUser = updatedUser;
            this.renderProfile();

            this.profileMessage.textContent = "Änderung wurde gespeichert.";
            this.profileMessage.className = "message success";
        } catch (error) {
            this.profileMessage.textContent = error.message;
            this.profileMessage.className = "message error";
        }
    }

    async handleResetPin() {
        this.resetPinMessage.textContent = "";
        this.resetPinMessage.className = "message";

        const newPin = this.resetPinInput.value;

        if (!/^\d{4}$/.test(newPin)) {
            this.resetPinMessage.textContent = "Der neue Start-PIN muss genau 4 Ziffern enthalten.";
            this.resetPinMessage.className = "message error";
            return;
        }

        if (!confirm("PIN für diesen Benutzer wirklich zurücksetzen?")) {
            return;
        }

        try {
            const updatedUser = await this.api.resetUserPin(this.profileUser.user_id, newPin);

            this.profileUser = updatedUser;
            this.resetPinInput.value = "";
	    this.resetPinInput.dataset.userEdited = "";
	    this.resetPinInput.placeholder = "Neuer Start-PIN";

            this.resetPinMessage.textContent =
                "PIN wurde zurückgesetzt. Der Benutzer muss beim nächsten Login einen neuen PIN wählen.";
            this.resetPinMessage.className = "message success";

            this.renderProfile();
        } catch (error) {
            this.resetPinMessage.textContent = error.message;
            this.resetPinMessage.className = "message error";
        }
    }

    escapeHtml(value) {
        return String(value)
            .replaceAll("&", "&amp;")
            .replaceAll('"', "&quot;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new UserProfilePage();
});
