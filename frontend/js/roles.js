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

function canUseManagementMenu(user) {
    return user && ["admin", "executive"].includes(user.role);
}

window.ROLE_LABELS = ROLE_LABELS;
window.getRoleLabel = getRoleLabel;
window.canUseManagementMenu = canUseManagementMenu;
