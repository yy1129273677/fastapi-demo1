import asyncio
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    model: str = "deepseek-chat"
    temperature: float = 0.7


class ChatResponse(BaseModel):
    answer: str
    model: str


async def call_llm(message: str, model: str, temperature: float) -> str:
    print("正在调用大模型...")
    print(f"模型：{model}")
    print(f"温度：{temperature}")
    print(f"用户问题：{message}")

    await asyncio.sleep(1)

    return f"AI 回答：你刚才问的是：{message}"


async def chat(request: ChatRequest) -> ChatResponse:
    answer = await call_llm(
        message=request.message, model=request.model, temperature=request.temperature
    )

    return ChatResponse(answer=answer, model=request.model)


async def main():
    request = ChatRequest(
        message="什么是 AI Agent？", model="deepseek-chat", temperature=0.7
    )

    response = await chat(request)

    print(response.model_dump())


asyncio.run(main())


async def stream_llm_answer(message: str):
    answer = f"这是针对「{message}」的模拟 AI 流式回答。"

    for char in answer:
        await asyncio.sleep(0.05)
        yield char


async def main():
    async for chunk in stream_llm_answer("什么是 RAG？"):
        print(chunk, end="", flush=True)

    print()


asyncio.run(main())
