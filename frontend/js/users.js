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

        this.bindEvents();
        this.initialize();
    }

    bindEvents() {
        this.refreshUsersButton.addEventListener("click", () => this.loadUsers());
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
	        </td>
	    `;

	    const openButton = row.querySelector(".open-user-button");
	    const statusButton = row.querySelector(".user-status-button");

	    openButton.addEventListener("click", () => {
	        navigateWithinApp(`user-profile.html?id=${user.user_id}`);
	    });

	    statusButton.addEventListener("click", () => this.handleToggleUserStatus(statusButton));

	    return row;
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
