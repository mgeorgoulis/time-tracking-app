import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.models.audit_log import AuditLog
from backend.models.user import Admin, Apprentice, DepartmentManager, Employee, Executive
from backend.models.timesheet import Timesheet
from backend.services.auth_service import AuthService
from backend.services.report_service import ReportService
from backend.services.session_service import SessionService
from backend.services.sqlite_store import SQLiteStore
from backend.services.time_tracking_service import TimeTrackingService


DATABASE_PATH = "data/time_tracking.db"

os.makedirs("data", exist_ok=True)

app = FastAPI(title="Time Tracking App API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

store = SQLiteStore(DATABASE_PATH)
audit_log = AuditLog()
session_service = SessionService(audit_log)
time_tracking_service = TimeTrackingService(audit_log, store)
report_service = ReportService()


class LoginRequest(BaseModel):
    user_id: int
    pin_code: str


class CreateUserRequest(BaseModel):
    user_id: int | None = None
    name: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    pin_code: str
    role: str
    department: str | None = None
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country: str | None = None

class UserResponse(BaseModel):
    user_id: int
    personnel_id: str
    name: str
    first_name: str
    last_name: str
    full_name: str
    role: str
    department: str | None = None
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country: str | None = None
    must_change_pin: bool
    is_active: bool

class LoginResponse(BaseModel):
    token: str
    user_id: int
    name: str
    role: str
    must_change_pin: bool

class UpdateUserStatusRequest(BaseModel):
    is_active: bool

class BreakRequest(BaseModel):
    minutes: int

class ChangePinRequest(BaseModel):
    current_pin: str
    new_pin: str
    confirm_pin: str

class UpdateUserProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    department: str | None = None
    email: str | None = None
    phone: str | None = None
    street: str | None = None
    postal_code: str | None = None
    city: str | None = None
    country: str | None = None


class ResetUserPinRequest(BaseModel):
    new_pin: str

def seed_default_admin():
    if len(store.get_all_users()) > 0:
        return

    admin = Admin(
        user_id=1,
        name="Default Admin",
        pin_code="9999"
    )

    store.add_user(admin)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    user = session_service.get_user_by_token(token)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Ungültige oder abgelaufene Session."
        )

    return user

def ensure_pin_is_changed(user):
    if user.must_change_pin:
        raise HTTPException(
            status_code=403,
            detail="PIN-Wechsel erforderlich."
        )

def ensure_can_manage_users(user):
    if user.role not in ["admin", "executive", "department_manager"]:
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung: Benutzerverwaltung nicht erlaubt."
        )


def can_update_user_profile(actor, target_user):
    if actor.role == "admin":
        return True

    if actor.role == "executive":
        return target_user.role != "admin"

    return False


def can_reset_user_pin(actor, target_user):
    if actor.role == "admin":
        return True

    if actor.role == "executive":
        return target_user.role != "admin"

    return False

def can_create_role(creator, target_role):
    if creator.role == "admin":
        return target_role in [
            "admin",
            "executive",
            "department_manager",
            "employee",
            "apprentice"
        ]

    if creator.role == "executive":
        return target_role in [
            "department_manager",
            "employee",
            "apprentice"
        ]

    if creator.role == "department_manager":
        return target_role in [
            "employee",
            "apprentice"
        ]

    return False


def can_view_user(viewer, target_user):
    if viewer.role in ["admin", "executive"]:
        return True

    if viewer.role == "department_manager":
        return getattr(viewer, "department", None) == getattr(target_user, "department", None)

    return viewer.user_id == target_user.user_id


def user_to_response(user):
    return UserResponse(
        user_id=user.user_id,
        personnel_id=f"{user.user_id:04d}",
        name=user.name,
        first_name=user.first_name,
        last_name=user.last_name,
        full_name=user.full_name,
        role=user.role,
        department=getattr(user, "department", None),
        email=user.email,
        phone=user.phone,
        street=user.street,
        postal_code=user.postal_code,
        city=user.city,
        country=user.country,
        must_change_pin=user.must_change_pin,
        is_active=user.is_active
    )

def can_update_user_status(actor, target_user):
    if actor.user_id == target_user.user_id:
        return False

    if actor.role == "admin":
        return True

    if actor.role == "executive":
        return target_user.role in [
            "department_manager",
            "employee",
            "apprentice"
        ]

    if actor.role == "department_manager":
        return (
            target_user.role in ["employee", "apprentice"]
            and getattr(actor, "department", None) == getattr(target_user, "department", None)
        )

    return False

@app.on_event("startup")
def startup():
    seed_default_admin()


@app.get("/")
def root():
    return {
        "message": "Time Tracking App API läuft",
        "docs": "/docs"
    }


@app.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    auth_service = AuthService(store.get_all_users(), audit_log)

    try:
        user = auth_service.login_with_pin(request.user_id, request.pin_code)
        session = session_service.create_session(user)

        return LoginResponse(
            token=session.token,
            user_id=user.user_id,
            name=user.name,
            role=user.role,
            must_change_pin=user.must_change_pin
        )

    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))


@app.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        session_service.logout(token)
        return {"message": "Logout erfolgreich."}

    except ValueError as error:
        raise HTTPException(status_code=401, detail=str(error))


@app.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "name": current_user.name,
        "role": current_user.role,
        "department": getattr(current_user, "department", None),
        "must_change_pin": current_user.must_change_pin
    }

@app.post("/change-pin")
def change_pin(
    request: ChangePinRequest,
    current_user=Depends(get_current_user)
):
    if request.new_pin != request.confirm_pin:
        raise HTTPException(
            status_code=400,
            detail="Neuer PIN und Bestätigung stimmen nicht überein."
        )

    try:
        current_user.change_pin(
            current_pin=request.current_pin,
            new_pin=request.new_pin
        )

        store.update_user_pin(current_user)

        audit_log.record(
            actor_id=current_user.user_id,
            action="pin_changed",
            target_type="User",
            target_id=current_user.user_id,
            details={"employee_name": current_user.name}
        )

        return {
            "message": "PIN erfolgreich geändert.",
            "must_change_pin": current_user.must_change_pin
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.get("/users", response_model=list[UserResponse])
def get_users(current_user=Depends(get_current_user)):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    users = store.get_all_users()

    visible_users = [
        user for user in users
        if can_view_user(current_user, user)
    ]

    return [
        user_to_response(user)
        for user in visible_users
    ]


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, current_user=Depends(get_current_user)):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    user = store.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Benutzer wurde nicht gefunden."
        )

    if not can_view_user(current_user, user):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung für diesen Benutzer."
        )

    return user_to_response(user)


@app.post("/users", response_model=UserResponse)
def create_user(
    request: CreateUserRequest,
    current_user=Depends(get_current_user)
):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    if request.user_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Die Personal-ID muss größer als 0 sein."
        )

    if store.get_user_by_id(request.user_id) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Die Personal-ID {request.user_id:04d} ist bereits vergeben."
        )

    if not can_create_role(current_user, request.role):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung, diese Rolle anzulegen."
        )

    if current_user.role == "department_manager":
        if request.department != getattr(current_user, "department", None):
            raise HTTPException(
                status_code=403,
                detail="Abteilungsleiter dürfen nur Benutzer der eigenen Abteilung anlegen."
            )
    first_name = request.first_name or ""
    last_name = request.last_name or ""

    if not first_name and request.name:
        name_parts = request.name.split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

    if not first_name:
        raise HTTPException(
            status_code=400,
            detail="Vorname ist erforderlich."
        )

    display_name = f"{first_name} {last_name}".strip()

    try:
        if request.role == "employee":
            if not request.department:
                raise ValueError("Für Mitarbeiter muss eine Abteilung angegeben werden.")

            user = Employee(
                user_id=request.user_id,
                name=request.name,
                pin_code=request.pin_code,
                department=request.department,
                must_change_pin=True,
                first_name=first_name,
                last_name=last_name,
                email=request.email,
                phone=request.phone,
                street=request.street,
                postal_code=request.postal_code,
                city=request.city,
                country=request.country
            )

        elif request.role == "apprentice":
            if not request.department:
                raise ValueError("Für Auszubildende muss eine Abteilung angegeben werden.")

            user = Apprentice(
                user_id=request.user_id,
                name=request.name,
                pin_code=request.pin_code,
                department=request.department,
                must_change_pin=True,
                first_name=first_name,
                last_name=last_name,
                email=request.email,
                phone=request.phone,
                street=request.street,
                postal_code=request.postal_code,
                city=request.city,
                country=request.country
            )

        elif request.role == "department_manager":
            if not request.department:
                raise ValueError("Für Abteilungsleiter muss eine Abteilung angegeben werden.")

            user = DepartmentManager(
                user_id=request.user_id,
                name=request.name,
                pin_code=request.pin_code,
                department=request.department,
                must_change_pin=True,
                first_name=first_name,
                last_name=last_name,
                email=request.email,
                phone=request.phone,
                street=request.street,
                postal_code=request.postal_code,
                city=request.city,
                country=request.country
            )

        elif request.role == "executive":
            user = Executive(
                user_id=request.user_id,
                name=request.name,
                pin_code=request.pin_code,
                must_change_pin=True,
                first_name=first_name,
                last_name=last_name,
                email=request.email,
                phone=request.phone,
                street=request.street,
                postal_code=request.postal_code,
                city=request.city,
                country=request.country
            )

        elif request.role == "admin":
            user = Admin(
                user_id=request.user_id,
                name=request.name,
                pin_code=request.pin_code,
                must_change_pin=True,
                first_name=first_name,
                last_name=last_name,
                email=request.email,
                phone=request.phone,
                street=request.street,
                postal_code=request.postal_code,
                city=request.city,
                country=request.country
            )

        else:
            raise ValueError("Ungültige Rolle.")

        store.add_user(user)

        audit_log.record(
            actor_id=current_user.user_id,
            action="user_created",
            target_type="User",
            target_id=user.user_id,
            details={
                "created_user_name": user.name,
                "created_user_role": user.role,
                "must_change_pin": user.must_change_pin
            }
        )

        return user_to_response(user)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

@app.patch("/users/{user_id}/status", response_model=UserResponse)
def update_user_status(
    user_id: int,
    request: UpdateUserStatusRequest,
    current_user=Depends(get_current_user)
):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    target_user = store.get_user_by_id(user_id)

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="Benutzer wurde nicht gefunden."
        )

    if not can_update_user_status(current_user, target_user):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung, diesen Benutzerstatus zu ändern."
        )

    target_user.is_active = request.is_active
    store.update_user_status(target_user)

    audit_log.record(
        actor_id=current_user.user_id,
        action="user_status_changed",
        target_type="User",
        target_id=target_user.user_id,
        details={
            "target_user_name": target_user.name,
            "is_active": target_user.is_active
        }
    )

    return user_to_response(target_user)

@app.post("/clock-in")
def clock_in(current_user=Depends(get_current_user)):
    try:
        entry = time_tracking_service.clock_in(current_user)

        return {
            "message": "Einstempeln erfolgreich.",
            "entry_id": entry.entry_id,
            "clock_in_time": entry.clock_in_time.isoformat()
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/break")
def add_break(
    request: BreakRequest,
    current_user=Depends(get_current_user)
):
    try:
        entry = time_tracking_service.add_break(current_user, request.minutes)

        return {
            "message": "Pause hinzugefügt.",
            "entry_id": entry.entry_id,
            "break_minutes": entry.break_minutes
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/break/start")
def start_break(current_user=Depends(get_current_user)):
    try:
        entry = time_tracking_service.start_break(current_user)

        return {
            "message": "Pause begonnen.",
            "entry_id": entry.entry_id,
            "break_started_at": entry.break_started_at.isoformat()
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.post("/break/end")
def end_break(current_user=Depends(get_current_user)):
    try:
        entry = time_tracking_service.end_break(current_user)

        return {
            "message": "Pause beendet.",
            "entry_id": entry.entry_id,
            "total_break_minutes": entry.break_minutes
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/breaks/daily")
def daily_breaks(
    year: int,
    month: int,
    day: int,
    current_user=Depends(get_current_user)
):
    break_minutes = store.get_daily_break_minutes(
        employee_id=current_user.user_id,
        year=year,
        month=month,
        day=day
    )

    return {
        "employee_id": current_user.user_id,
        "year": year,
        "month": month,
        "day": day,
        "break_minutes": break_minutes
    }

@app.post("/clock-out")
def clock_out(current_user=Depends(get_current_user)):
    try:
        entry = time_tracking_service.clock_out(current_user)

        return {
            "message": "Ausstempeln erfolgreich.",
            "entry_id": entry.entry_id,
            "clock_out_time": entry.clock_out_time.isoformat(),
            "worked_minutes": entry.worked_minutes()
        }

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@app.get("/report/monthly")
def monthly_report(
    year: int,
    month: int,
    expected_minutes: int,
    current_user=Depends(get_current_user)
):
    entries = store.get_time_entries_by_employee(current_user.user_id)

    timesheet = Timesheet(
        employee=current_user,
        month=month,
        year=year,
        expected_minutes=expected_minutes
    )

    for entry in entries:
        if (
            entry.clock_in_time
            and entry.clock_in_time.year == year
            and entry.clock_in_time.month == month
        ):
            timesheet.add_entry(entry)

    return report_service.generate_monthly_report(timesheet)


@app.get("/audit-log")
def get_audit_log(current_user=Depends(get_current_user)):
    if current_user.role not in ["admin", "executive"]:
        raise HTTPException(status_code=403, detail="Keine Berechtigung.")

    return [entry.to_dict() for entry in store.get_audit_log_entries()]

@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user_profile(
    user_id: int,
    request: UpdateUserProfileRequest,
    current_user=Depends(get_current_user)
):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    target_user = store.get_user_by_id(user_id)

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="Benutzer wurde nicht gefunden."
        )

    if not can_update_user_profile(current_user, target_user):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung, dieses Benutzerprofil zu bearbeiten."
        )

    update_data = request.model_dump(exclude_unset=True)

    for field_name, value in update_data.items():
        setattr(target_user, field_name, value)

    target_user.name = target_user.full_name

    store.update_user_profile(target_user)

    audit_log.record(
        actor_id=current_user.user_id,
        action="user_profile_updated",
        target_type="User",
        target_id=target_user.user_id,
        details={
            "target_user_name": target_user.name,
            "updated_fields": list(update_data.keys())
        }
    )

    return user_to_response(target_user)


@app.post("/users/{user_id}/reset-pin", response_model=UserResponse)
def reset_user_pin(
    user_id: int,
    request: ResetUserPinRequest,
    current_user=Depends(get_current_user)
):
    ensure_pin_is_changed(current_user)
    ensure_can_manage_users(current_user)

    target_user = store.get_user_by_id(user_id)

    if target_user is None:
        raise HTTPException(
            status_code=404,
            detail="Benutzer wurde nicht gefunden."
        )

    if not can_reset_user_pin(current_user, target_user):
        raise HTTPException(
            status_code=403,
            detail="Keine Berechtigung, den PIN dieses Benutzers zurückzusetzen."
        )

    try:
        target_user.set_pin(request.new_pin)
        target_user.must_change_pin = True

        store.update_user_pin(target_user)

        audit_log.record(
            actor_id=current_user.user_id,
            action="user_pin_reset",
            target_type="User",
            target_id=target_user.user_id,
            details={
                "target_user_name": target_user.name,
                "must_change_pin": True
            }
        )

        return user_to_response(target_user)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
