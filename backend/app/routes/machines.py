from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Machines"])


@router.get("/machines")
def get_machines():
    """Emergency demo configuration: one live machine + one fault simulation."""
    return {
        "machines": ["MACHINE-001", "MACHINE-002"],
        "count": 2,
    }
