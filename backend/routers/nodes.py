from fastapi import APIRouter
from services import influx

router = APIRouter()


@router.get("")
def nodes():
    return influx.get_nodes()
