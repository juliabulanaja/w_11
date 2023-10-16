from fastapi import FastAPI

# from src.database.auth import Hash
from src.routes import contacts
from src.routes import users

app = FastAPI()
# hash_handler = Hash()

app.include_router(users.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI!"}
