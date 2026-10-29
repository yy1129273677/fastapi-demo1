# Python 没有 var / let / const
# 直接赋值就可以

name = "大伟"
age = 30
score = 99.5
is_teacher = True
nothing = None

# Python 推荐使用 snake_case 下划线命名

user_name = "张三"
max_retry_count = 3
is_login = False

print(user_name)
print(max_retry_count)
print(is_login)

print(name)
print(age)
print(score)
print(is_teacher)
print(nothing)

name = "大伟"
age = 30

# 不推荐这种拼接方式
msg1 = "你好，我是" + name

# 推荐 f-string
msg2 = f"你好，我是{name}，今年{age}岁"

# 推荐多行字符串
msg3 = f""" 
你好，我是{name}，今年{age}岁。 
"""

print(msg1)
print(msg2)
print(msg3)


fruits = ["苹果", "香蕉", "橙子"]

for fruit in fruits:
    print(fruit)

    numbers = [1, 2, 3, 4, 5]

# 普通写法
result = []

for num in numbers:
    result.append(num * 2)

print(result)

# 列表推导式
doubled = [num * 2 for num in numbers]

print(doubled)

numbers = [1, 2, 3, 4, 5]

big_numbers = [num for num in numbers if num > 2]

print(big_numbers)

user = {"name": "大伟", "age": 30, "city": "北京"}

for key, value in user.items():
    print(f"{key}: {value}")

user = {"name": "大伟", "age": 30}

print(user.get("name"))
print(user.get("email"))
print(user.get("email", "未填写"))

score = 85

if score >= 90:
    print("优秀")
elif score >= 60:
    print("及格")
else:
    print("不及格")


age = 25
is_vip = True

if age >= 18 and is_vip:
    print("成年 VIP 用户")

if age < 18 or is_vip:
    print("满足其中一个条件")

if not is_vip:
    print("不是 VIP")
else:
    print("是 VIP")


for i in range(1, 6):
    print(i)

fruits = ["苹果", "香蕉", "橙子"]

for index, fruit in enumerate(fruits):
    print(f"{index}: {fruit}")


""" 加法函数 int 不是强类型，可以接受字符串 """


def add(a: int, b: int) -> int:
    return a + b


print(add("1", "2"))

from typing import Any

name: str = "大伟"
age: int = 30
score: float = 99.5
is_active: bool = True
tags: list[str] = ["AI", "FastAPI", "Agent"]
user: dict[str, Any] = {"name": "大伟", "age": 30}

print(name)
print(tags)
print(user)


class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def greet(self) -> str:
        return f"我是 {self.name}，今年 {self.age} 岁"


user = User("大伟", 30)

print(user.name)
print(user.age)
print(user.greet())


class Teacher(User):
    def __init__(self, name: str, age: int, subject: str):
        super().__init__(name, age)
        self.subject = subject

    def introduce(self) -> str:
        return f"我是 {self.name}，我教 {self.subject}"


teacher = Teacher("大伟", 30, "AI Agent 开发")

print(teacher.greet())
print(teacher.introduce())


from pydantic import BaseModel, ValidationError


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


try:
    request = ChatRequest(message=123)
except ValidationError as e:
    print(e)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]
    model: str = "deepseek-chat"


request = ChatRequest(
    messages=[
        Message(role="system", content="你是一个 AI 助手"),
        Message(role="user", content="你好"),
    ]
)

print(request.model_dump())


class ModelNotFoundError(Exception):
    pass


def get_model(model_name: str) -> str:
    supported_models = ["deepseek-chat", "qwen-plus", "gpt-4o-mini"]

    if model_name not in supported_models:
        raise ModelNotFoundError(f"不支持的模型：{model_name}")

    return model_name


try:
    model = get_model("unknown-model")
    print(model)
except ModelNotFoundError as e:
    print(f"模型错误：{e}")


import asyncio


async def fetch_data() -> str:
    print("开始获取数据")
    await asyncio.sleep(1)
    print("数据获取完成")
    return "这是数据"


result = asyncio.run(fetch_data())

print(result)


async def query_user():
    await asyncio.sleep(1)
    return "用户信息"


async def query_order():
    await asyncio.sleep(1)
    return "订单信息"


async def query_llm():
    await asyncio.sleep(1)
    return "AI 回答"


async def main():
    user, order, answer = await asyncio.gather(query_user(), query_order(), query_llm())

    print(user)
    print(order)
    print(answer)


asyncio.run(main())


async def generate_tokens():
    tokens = ["你", "好", "，", "我", "是", "AI", "。"]

    for token in tokens:
        await asyncio.sleep(0.2)
        yield token


async def main():
    async for token in generate_tokens():
        print(token, end="", flush=True)

    print()


asyncio.run(main())


class AsyncDatabase:
    async def __aenter__(self):
        print("打开数据库连接")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print("关闭数据库连接")

    async def query(self, sql: str) -> str:
        await asyncio.sleep(0.5)
        return f"查询结果：{sql}"


async def main():
    async with AsyncDatabase() as db:
        result = await db.query("SELECT * FROM users")
        print(result)


asyncio.run(main())
