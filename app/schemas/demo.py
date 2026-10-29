from pydantic import BaseModel, ValidationError


class UserA(BaseModel):
    name: str
    email: str | None


class UserB(BaseModel):
    name: str
    email: str | None = None


print(UserB(name="大伟"))

from typing import Any, Literal


ModelName = Literal["deepseek-chat", "qwen-plus", "gpt-4o-mini"]


def chat(message: str, model: ModelName) -> str:
    return f"使用 {model} 回答：{message}"


print(chat("什么是 AI Agent？", "deepseek-chat"))


from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


def create_message(role: MessageRole, content: str) -> dict[str, str]:
    return {
        "role": role.value,
        "content": content
    }


print(create_message(MessageRole.USER, "你好"))


from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    stream: bool = True


request = ChatRequest(
    message="什么是 AI Agent？"
)

print(request)
print(request.message)
print(request.model)
print(request.temperature)
print(request.stream)




class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    stream: bool = True


try:
    request = ChatRequest(
        message=123,
        temperature="abc"
    )
except ValidationError as e:
    # print(e)
    pass


    


class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-chat"
    temperature: float = 0.7
    stream: bool = True


request = ChatRequest(
    message="什么是 RAG？"
)

data = request.model_dump()

print(data)
print(type[str, Any](data))   