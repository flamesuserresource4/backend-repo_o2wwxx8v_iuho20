import os
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document, get_documents, db
from schemas import Event, Booking, TrainingApplication, ContactMessage, Story, Partner, Resource, SiteStat

app = FastAPI(title="Ekhaya Legae API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Ekhaya Legae API running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Set"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


@app.get("/api/schema")
def get_schema():
    def model_schema(model: Any) -> Dict[str, Any]:
        fields = {}
        for name, field in model.model_fields.items():  # pydantic v2
            fields[name] = {
                "annotation": str(field.annotation),
                "required": field.is_required(),
                "default": None if field.is_required() else getattr(field, 'default', None),
                "description": getattr(field, 'description', None)
            }
        return {
            "collection": model.__name__.lower(),
            "fields": fields
        }

    return {
        "event": model_schema(Event),
        "booking": model_schema(Booking),
        "trainingapplication": model_schema(TrainingApplication),
        "contactmessage": model_schema(ContactMessage),
        "story": model_schema(Story),
        "partner": model_schema(Partner),
        "resource": model_schema(Resource),
        "sitestat": model_schema(SiteStat),
    }


# ------------------------------
# Public Content Endpoints
# ------------------------------

@app.get("/api/events")
def list_events(limit: int = 10):
    try:
        items = get_documents("event", {}, limit)
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}


@app.post("/api/bookings")
def create_booking(booking: Booking):
    try:
        inserted_id = create_document("booking", booking)
        return {"id": inserted_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/api/resources")
def list_resources(limit: int = 20, type: Optional[str] = None, language: Optional[str] = None):
    try:
        query: Dict[str, Any] = {}
        if type:
            query["type"] = type
        if language:
            query["language"] = language
        items = get_documents("resource", query, limit)
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}


@app.get("/api/partners")
def list_partners(limit: int = 20):
    try:
        items = get_documents("partner", {}, limit)
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}


@app.get("/api/stories")
def list_stories(limit: int = 10):
    try:
        items = get_documents("story", {"featured": True}, limit)
        return {"items": items}
    except Exception as e:
        return {"items": [], "error": str(e)}


@app.get("/api/stats")
def list_stats():
    try:
        items = get_documents("sitestat", {}, None)
        # Provide reasonable defaults if none exist yet
        if not items:
            items = [
                {"label": "Tests Conducted", "value": 0},
                {"label": "Youth Trained", "value": 0},
                {"label": "Communities Served", "value": 0},
                {"label": "Lives Impacted", "value": 0},
            ]
        return {"items": items}
    except Exception:
        # On DB error, still return defaults
        return {
            "items": [
                {"label": "Tests Conducted", "value": 0},
                {"label": "Youth Trained", "value": 0},
                {"label": "Communities Served", "value": 0},
                {"label": "Lives Impacted", "value": 0},
            ]
        }


# ------------------------------
# Forms / Submissions
# ------------------------------

@app.post("/api/applications")
def submit_training_application(app_data: TrainingApplication):
    try:
        inserted_id = create_document("trainingapplication", app_data)
        return {"id": inserted_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/api/contact")
def submit_contact_message(msg: ContactMessage):
    try:
        inserted_id = create_document("contactmessage", msg)
        return {"id": inserted_id, "status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
