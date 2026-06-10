class ChangePinPage {
    constructor() {
        this.api = authApi;
        this.currentUser = null;

        this.currentPinInput = document.getElementById("current-pin-input");
        this.newPinInput = document.getElementById("new-pin-input");
        this.confirmPinInput = document.getElementById("confirm-pin-input");
        this.submitButton = document.getElementById("change-pin-submit-button");
        this.cancelButton = document.getElementById("change-pin-cancel-button");
        this.message = document.getElementById("change-pin-message");
        this.description = document.getElementById("change-pin-description");

        preparePinInput(this.currentPinInput, "Aktueller PIN");
        preparePinInput(this.newPinInput, "Neuer PIN");
        preparePinInput(this.confirmPinInput, "Neuen PIN bestätigen");

        this.bindEvents();
        this.initialize();
    }

bindEvents() {
    this.submitButton.addEventListener("click", () => this.handleChangePin());
    this.cancelButton.addEventListener("click", () => this.handleCancel());
}

handleCancel() {
    if (this.currentUser && this.currentUser.must_change_pin) {
        logoutAndRedirect();
        return;
    }

    navigateWithinApp("dashboard.html", true);
}

    async initialize() {
        const user = await getCurrentUserOrRedirect();


        if (!user) {
            return;
        }

        this.currentUser = user;

        if (user.must_change_pin) {
            this.description.textContent =
                "Aus Sicherheitsgründen müssen Sie Ihren Start-PIN ändern, bevor Sie die App nutzen können.";
            this.cancelButton.textContent = "Abmelden";
        } else {
            this.description.textContent = "Hier können Sie Ihren PIN ändern.";
            this.cancelButton.textContent = "Abbrechen";
        }

        revealProtectedPage();
    }

    async handleChangePin() {
        this.message.textContent = "";
        this.message.className = "message";

        const currentPin = this.currentPinInput.value;
        const newPin = this.newPinInput.value;
        const confirmPin = this.confirmPinInput.value;

        if (!/^\d{4}$/.test(currentPin)) {
            this.showError("Der aktuelle PIN muss genau 4 Ziffern enthalten.");
            return;
        }

        if (!/^\d{4}$/.test(newPin)) {
            this.showError("Der neue PIN muss genau 4 Ziffern enthalten.");
            return;
        }

        if (newPin !== confirmPin) {
            this.showError("Neuer PIN und Bestätigung stimmen nicht überein.");
            return;
        }

        try {
            await this.api.changePin(currentPin, newPin, confirmPin);

            this.message.textContent = "PIN erfolgreich geändert.";
            this.message.className = "message success";

            this.currentPinInput.value = "";
            this.newPinInput.value = "";
            this.confirmPinInput.value = "";

            window.setTimeout(() => {
                navigateWithinApp("dashboard.html", true);
            }, 800);
        } catch (error) {
            this.showError(error.message);
        }
    }

    showError(message) {
        this.message.textContent = message;
        this.message.className = "message error";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new ChangePinPage();
});
