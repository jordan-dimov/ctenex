from fastapi import APIRouter

router = APIRouter(tags=["status"])


@router.get("/status")
async def read_system_status():
    # TODO: Check database connection
    return {"status": "OK"}
