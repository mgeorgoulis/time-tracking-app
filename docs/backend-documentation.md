# Backend-Dokumentation: Time Tracking App

## 1. Ziel des Backends

Das Backend der Time Tracking App bildet die zentrale Geschäftslogik einer Arbeitszeiterfassungs-App ab.

Es ermöglicht:

- Login per PIN
- sichere Speicherung von PINs als Hash
- Benutzer- und Rollenverwaltung
- Ein- und Ausstempeln
- Pausenerfassung
- persistente Speicherung von Zeiteinträgen
- Wiederherstellung aktiver Zeiteinträge nach Neustart
- Monatsberichte
- digitale Quittierung von Stundenzetteln
- Audit-Logging
- Archivierung und Löschlogik
- API-Zugriff über FastAPI

Das Backend ist objektorientiert aufgebaut und trennt bewusst Modelle, Services, Persistenz und API.

---

## 2. Eingesetzte Technologien

| Bereich | Technologie |
|---|---|
| Programmiersprache | Python |
| API-Framework | FastAPI |
| Server | Uvicorn |
| Datenbank | SQLite |
| Tests | unittest |
| Versionsverwaltung | Git / GitHub |
| Authentifizierung | PIN + Session-Token |
| API-Dokumentation | Swagger UI über FastAPI |

---

## 3. Projektstruktur Backend

```text
backend/
├── api.py
├── app.py
├── cli.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── audit_log.py
│   ├── time_entry.py
│   ├── timesheet.py
│   └── user.py
├── services/
│   ├── __init__.py
│   ├── archive_service.py
│   ├── auth_service.py
│   ├── data_store.py
│   ├── permission_service.py
│   ├── report_service.py
│   ├── session_service.py
│   ├── sqlite_store.py
│   └── time_tracking_service.py
└── tests/
    ├── test_archive_service.py
    ├── test_audit_log.py
    ├── test_auth_service.py
    ├── test_data_store.py
    ├── test_permission_service.py
    ├── test_permissions.py
    ├── test_pin_hashing.py
    ├── test_report_service.py
    ├── test_session_service.py
    ├── test_sqlite_store.py
    ├── test_time_entry.py
    ├── test_time_tracking_persistence.py
    ├── test_time_tracking_service.py
    └── test_timesheet.py
