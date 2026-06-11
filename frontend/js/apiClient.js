const API_BASE_URL = "http://127.0.0.1:8000";

class ApiClient {
    constructor(baseUrl = API_BASE_URL) {
        this.baseUrl = baseUrl;
        this.token = sessionStorage.getItem("timeTrackingToken");
    }

    setToken(token) {
        this.token = token;
        sessionStorage.setItem("timeTrackingToken", token);
    }

    clearToken() {
        this.token = null;
        sessionStorage.removeItem("timeTrackingToken");
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

    clockOut() {
        return this.request("/clock-out", {
            method: "POST"
        });
    }

    dailyBreaks(year, month, day) {
        const params = new URLSearchParams({ year, month, day });
        return this.request(`/breaks/daily?${params.toString()}`);
    }

    monthlyReport(year, month, expectedMinutes) {
        const params = new URLSearchParams({
            year,
            month,
            expected_minutes: expectedMinutes
        });

        return this.request(`/report/monthly?${params.toString()}`);
    }

    getUsers() {
        return this.request("/users");
    }

    getUser(userId) {
        return this.request(`/users/${userId}`);
    }

    createUser(userData) {
        return this.request("/users", {
            method: "POST",
            body: JSON.stringify(userData)
        });
    }

    archiveUser(userId, adminPin) {
        return this.request(`/users/${userId}/archive`, {
            method: "POST",
            body: JSON.stringify({
                admin_pin: adminPin
            })
        });
    }

    updateUserStatus(userId, isActive) {
        return this.request(`/users/${userId}/status`, {
            method: "PATCH",
            body: JSON.stringify({
                is_active: isActive
            })
        });
    }

    updateUserProfile(userId, profileData) {
        return this.request(`/users/${userId}`, {
            method: "PATCH",
            body: JSON.stringify(profileData)
        });
    }

    resetUserPin(userId, newPin) {
        return this.request(`/users/${userId}/reset-pin`, {
            method: "POST",
            body: JSON.stringify({
                new_pin: newPin
            })
        });
    }

    auditLog() {
        return this.request("/audit-log");
    }
}

window.ApiClient = ApiClient;
