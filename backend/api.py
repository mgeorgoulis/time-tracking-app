import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from backend.models.audit_log import AuditLog
from backend.models.user import Admin
from backend.models.timesheet import Timesheet
from backend.services.auth_service import AuthService
from backend.services.report_service import ReportService
from backend.services.session_service import SessionService
from backend.services.sqlite_store import SQLiteStore
from backend.services.time_tracking_service import TimeTrackingService


DATABASE_PATH = "data/time_tracking.db"

os.makedirs("data", exist_ok=True)

app = FastAPI(title="Time Tracking App API")

security = HTTPBearer()

store = SQLiteStore(DATABASE_PATH)
audit_log = AuditLog()
session_service = SessionService(audit_log)
time_tracking_service = TimeTrackingService(audit_log, store)
report_service = ReportService()


class LoginRequest(BaseModel):
    user_id: int
    pin_code: str


class LoginResponse(BaseModel):
    token: str
    user_id: int
    name: str
    role: str


class BreakRequest(BaseModel):
    minutes: int


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
            role=user.role
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
        "department": getattr(current_user, "department", None)
    }


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
