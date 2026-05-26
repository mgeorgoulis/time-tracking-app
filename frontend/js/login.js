class LoginPage {
    constructor() {
        this.api = new ApiClient();

        this.loginForm = document.getElementById("login-form");
        this.userIdInput = document.getElementById("user-id-input");
        this.pinInput = document.getElementById("pin-input");
        preparePinInput(this.pinInput);
        this.loginButton = document.getElementById("login-button");
        this.loginMessage = document.getElementById("login-message");

        this.bindEvents();
        this.initialize();
    }

    bindEvents() {
        this.loginButton.addEventListener("click", () => this.handleLogin());

        this.loginForm.addEventListener("submit", (event) => {
            event.preventDefault();
            this.handleLogin();
        });
    }

async initialize() {
    this.api.clearToken();

    sessionStorage.removeItem("wasLoggedOut");
    sessionStorage.removeItem("internalNavigation");

    this.userIdInput.value = "";
    this.pinInput.value = "";

    preparePinInput(this.pinInput, "4-stelliger PIN");
}

    async handleLogin() {
        this.loginMessage.textContent = "";
        this.loginMessage.className = "message";

        const userId = this.userIdInput.value;
        const pinCode = this.pinInput.value;

        if (!userId) {
            this.showError("Bitte eine Benutzer-ID eingeben.");
            return;
        }

        if (!pinCode) {
            this.showError("Bitte einen PIN eingeben.");
            return;
        }

        try {
            const loginResponse = await this.api.login(userId, pinCode);
            this.api.setToken(loginResponse.token);

            const currentUser = await this.api.me();

            if (loginResponse.must_change_pin || currentUser.must_change_pin) {
                window.location.replace("change-pin.html");
                return;
            }

            window.location.replace("dashboard.html");
        } catch (error) {
            this.showError(error.message);
        }
    }

    showError(message) {
        this.loginMessage.textContent = message;
        this.loginMessage.className = "message error";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new LoginPage();
});
