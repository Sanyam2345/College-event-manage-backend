from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, events

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="College Event Management System")

# CORS middleware to allow React frontend connection
# CORS middleware to allow connection from any frontend (Render)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(events.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to College Event Management System API"}
