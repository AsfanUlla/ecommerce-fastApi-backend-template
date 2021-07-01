from fastapi import FastAPI
from fastapi.responses import JSONResponse
from users.views import router as UserRouter
from content.views import router as ContentRouter

app = FastAPI()

app.include_router(UserRouter, tags=["Users"], prefix="/users")
app.include_router(ContentRouter, tags=["Content"], prefix="/content")


@app.get("/")
async def root():
    return JSONResponse(
        {'success': True},
        200
    )
