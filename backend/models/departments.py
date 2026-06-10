ALLOWED_DEPARTMENTS = [
    "Produktion",
    "Design",
    "Montage",
    "Office",
    "Geschäftsführung"
]


def is_allowed_department(department):
    return department in ALLOWED_DEPARTMENTS
