from fastapi import FastAPI
from auth.router import router as auth_router

import importlib

app = FastAPI(title="SOS API — Sistem de Management Universitar", version="1.0.0")


app.include_router(auth_router, prefix="/auth", tags=["auth"])

MODULES = [
    "students",
    "professors",
    "enrollments",
    "schedule",
    "grades",
    "materials",
    "announcements",
    "library",
    "reports",
]

active_modules = []
missing_modules = []

for module in MODULES:
    try:
        mod = importlib.import_module(f"{module}.router")
        app.include_router(mod.router, prefix=f"/{module}", tags=[module])
        active_modules.append(module)
    except ImportError:
        missing_modules.append(module)


@app.get("/status")
def get_status():
    return {
        "active_modules": active_modules,
        "missing_modules": missing_modules,
        "total": len(active_modules),
        "expected": len(MODULES) + 1,
    }
