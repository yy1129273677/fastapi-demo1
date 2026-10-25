from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(prefix="/demo",tags=["测试"])
# 定义用户模型
class User(BaseModel):
    id: int
    name: str
    email: str
    password: str

@router.get("/health")
def read_health():
    """ 健康检查 """
    return {"message": "健康检查通过"}
    
