class UsersPage {
    constructor() {
        this.api = authApi;
        this.currentUser = null;

        this.userInfo = document.getElementById("user-info");
        this.refreshUsersButton = document.getElementById("refresh-users-button");
	this.activeUsersTableBody = document.getElementById("active-users-table-body");
	this.inactiveUsersTableBody = document.getElementById("inactive-users-table-body");
	this.inactiveUsersMessage = document.getElementById("inactive-users-message");
	this.usersMessage = document.getElementById("users-message");
	this.archiveUserModal = document.getElementById("archive-user-modal");
	this.archiveUserModalText = document.getElementById("archive-user-modal-text");
	this.archiveAdminPinInput = document.getElementById("archive-admin-pin-input");
	this.archiveUserConfirmButton = document.getElementById("archive-user-confirm-button");
	this.archiveUserCancelButton = document.getElementById("archive-user-cancel-button");
	this.archiveUserMessage = document.getElementById("archive-user-message");

	this.archiveTargetUser = null;

        this.bindEvents();
        this.initialize();
    }

	bindEvents() {
	    this.refreshUsersButton.addEventListener("click", () => this.loadUsers());

	    this.archiveUserCancelButton.addEventListener("click", () => this.closeArchiveUserModal());
	    this.archiveUserConfirmButton.addEventListener("click", () => this.confirmArchiveUser());

	    this.archiveAdminPinInput.addEventListener("input", () => {
	        this.archiveAdminPinInput.value = this.archiveAdminPinInput.value
	            .replace(/\D/g, "")
	            .slice(0, 4);
	    });
	}

    async initialize() {
        const user = await requireManagementAccess();

        if (!user) {
            return;
        }

        this.currentUser = user;
        this.renderHeader();
        renderManagementNav("users");

        await this.loadUsers();
        revealProtectedPage();
    }

    renderHeader() {
        const department = this.currentUser.department || "keine Abteilung";

        this.userInfo.textContent =
            `${this.currentUser.full_name || this.currentUser.name} · ${getRoleLabel(this.currentUser.role)} · ${department}`;
    }

	async loadUsers() {
	    this.usersMessage.textContent = "";
	    this.usersMessage.className = "message";
	    this.inactiveUsersMessage.textContent = "";
	    this.inactiveUsersMessage.className = "message";

	    this.activeUsersTableBody.innerHTML = "";
	    this.inactiveUsersTableBody.innerHTML = "";

	    try {
	        const users = await this.api.getUsers();

	        users.sort((a, b) => a.user_id - b.user_id);

	        const activeUsers = users.filter(user => user.is_active);
	        const inactiveUsers = users.filter(user => !user.is_active);

	        if (activeUsers.length === 0) {
	            this.usersMessage.textContent = "Keine aktiven Benutzer vorhanden.";
	        }

	        if (inactiveUsers.length === 0) {
	            this.inactiveUsersMessage.textContent = "Keine inaktiven Benutzer vorhanden.";
	        }

	        activeUsers.forEach(user => {
	            this.activeUsersTableBody.appendChild(this.createUserRow(user));
	        });

	        inactiveUsers.forEach(user => {
	            this.inactiveUsersTableBody.appendChild(this.createUserRow(user));
	        });
	    } catch (error) {
	        this.usersMessage.textContent = error.message;
	        this.usersMessage.className = "message error";
	    }
	}

	createUserRow(user) {
	    const row = document.createElement("tr");

	    if (!user.is_active) {
	        row.classList.add("inactive-user-row");
	    }

	    const displayName = user.full_name || user.name;
	    const department = user.department || "—";
	    const email = user.email || "—";
	    const status = user.is_active ? "Aktiv" : "Inaktiv";
	    const mustChangePin = user.must_change_pin ? "Ja" : "Nein";
	    const statusActionLabel = user.is_active ? "Deaktivieren" : "Reaktivieren";
		const archiveButtonHtml = user.is_active
		    ? ""
		    : `
		        <button
		            class="danger-button archive-user-button"
		            data-user-id="${user.user_id}"
		        >
		            Benutzer löschen
		        </button>
		    `;

	    row.innerHTML = `
	        <td>${formatUserId(user.user_id)}</td>
	        <td>${displayName}</td>
	        <td>${getRoleLabel(user.role)}</td>
	        <td>${department}</td>
	        <td>${email}</td>
	        <td>${status}</td>
	        <td>${mustChangePin}</td>
	        <td class="table-actions">
	            <button
	                class="secondary-button open-user-button"
	                data-user-id="${user.user_id}"
	            >
	                Öffnen
	            </button>

	            <button
	                class="secondary-button user-status-button"
	                data-user-id="${user.user_id}"
	                data-is-active="${user.is_active}"
	            >
	                ${statusActionLabel}
	            </button>

                   ${archiveButtonHtml}
	        </td>
	    `;

	    const openButton = row.querySelector(".open-user-button");
	    const statusButton = row.querySelector(".user-status-button");
            const archiveButton = row.querySelector(".archive-user-button");

	if (archiveButton) {
	    archiveButton.addEventListener("click", () => this.openArchiveUserModal(user));
	}

	    openButton.addEventListener("click", () => {
	        navigateWithinApp(`user-profile.html?id=${user.user_id}`);
	    });

	    statusButton.addEventListener("click", () => this.handleToggleUserStatus(statusButton));

	    return row;
	}

	openArchiveUserModal(user) {
	    this.archiveTargetUser = user;

	    const displayName = user.full_name || user.name;

	    this.archiveUserModalText.textContent =
	        `Soll der Benutzer "${displayName}" wirklich dauerhaft aus der Benutzerverwaltung entfernt werden? Die Daten werden im Backend archiviert.`;

	    this.archiveAdminPinInput.value = "";
	    this.archiveUserMessage.textContent = "";
	    this.archiveUserMessage.className = "message";

	    this.archiveUserModal.classList.remove("hidden");
	    this.archiveAdminPinInput.focus();
	}

	closeArchiveUserModal() {
	    this.archiveTargetUser = null;
	    this.archiveAdminPinInput.value = "";
	    this.archiveUserMessage.textContent = "";
	    this.archiveUserMessage.className = "message";
	    this.archiveUserModal.classList.add("hidden");
	}

	async confirmArchiveUser() {
	    if (!this.archiveTargetUser) {
	        return;
	    }

	    const adminPin = this.archiveAdminPinInput.value;
	    const displayName = this.archiveTargetUser.full_name || this.archiveTargetUser.name;

	    this.archiveUserMessage.textContent = "";
	    this.archiveUserMessage.className = "message";

	    if (!/^\d{4}$/.test(adminPin)) {
	        this.archiveUserMessage.textContent = "Bitte die 4-stellige Admin-PIN eingeben.";
	        this.archiveUserMessage.className = "message error";
	        return;
	    }

	    try {
	        await this.api.archiveUser(this.archiveTargetUser.user_id, adminPin);

	        this.closeArchiveUserModal();

	        this.usersMessage.textContent =
	            `${displayName} wurde archiviert und aus der Benutzerverwaltung entfernt.`;
	        this.usersMessage.className = "message success";

	        await this.loadUsers();
	    } catch (error) {
	        this.archiveAdminPinInput.value = "";

	        if (error.message.includes("Admin-PIN")) {
	            this.archiveUserMessage.textContent =
	                "Falsche Admin-PIN. Benutzer wurde nicht gelöscht.";
	        } else {
	            this.archiveUserMessage.textContent =
	                `${error.message} Benutzer wurde nicht gelöscht.`;
	        }

	        this.archiveUserMessage.className = "message error";
	        this.archiveAdminPinInput.focus();
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
                `Status geändert: ${updatedUser.full_name || updatedUser.name} ist jetzt ${updatedUser.is_active ? "aktiv" : "inaktiv"}.`;
            this.usersMessage.className = "message success";

            await this.loadUsers();
        } catch (error) {
            this.usersMessage.textContent = error.message;
            this.usersMessage.className = "message error";
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new UsersPage();
});
