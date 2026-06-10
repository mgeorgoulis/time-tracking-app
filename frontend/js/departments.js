const DEPARTMENTS = [
    "Produktion",
    "Design",
    "Montage",
    "Office",
    "Geschäftsführung"
];

function populateDepartmentSelect(selectElement, placeholder = "Abteilung auswählen") {
    if (!selectElement) {
        return;
    }

    selectElement.innerHTML = "";

    const placeholderOption = document.createElement("option");
    placeholderOption.value = "";
    placeholderOption.textContent = placeholder;
    selectElement.appendChild(placeholderOption);

    DEPARTMENTS.forEach(department => {
        const option = document.createElement("option");
        option.value = department;
        option.textContent = department;
        selectElement.appendChild(option);
    });
}

window.DEPARTMENTS = DEPARTMENTS;
window.populateDepartmentSelect = populateDepartmentSelect;
