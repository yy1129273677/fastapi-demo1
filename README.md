# FastAPI 学习项目（fastapi-demo1）

一个从零学起的空白后端：监听 **3001** 端口，和现有 NestJS 后端一致，前端 [axios.ts](../demo1/src/commJs/axios.ts) 里的 `http://localhost:3001` 可以直接访问这里的接口。

配套代码：[app/main.py](app/main.py)、[app/api.py](app/api.py)。

---

# 一、FastAPI 基本用法

## 1. 最小可运行应用

```python
from fastapi import FastAPI

app = FastAPI()          # 创建应用实例，相当于整个后端的"总路由器"

@app.get("/")            # 把下面的函数挂到 GET / 这个地址上
def read_root():
    return {"message": "hello"}   # 返回字典，FastAPI 自动转成 JSON
```

三件事就够起步：**建 app → 加装饰器 → 返回数据**。

## 2. 路由：URL + HTTP 方法

| 装饰器 | 含义 | 典型用途 |
|---|---|---|
| `@app.get("/xxx")` | 查询 | 列表、详情 |
| `@app.post("/xxx")` | 新增 | 创建数据 |
| `@app.put("/xxx")` | 整体更新 | 替换一条记录 |
| `@app.patch("/xxx")` | 局部更新 | 只改几个字段 |
| `@app.delete("/xxx")` | 删除 | 删除记录 |

同一个路径可以同时挂多个方法，比如 `/user` 上既有 `GET`（查）又有 `POST`（建）。

## 3. 路径参数 vs 查询参数

```python
# 路径参数：值写在 URL 路径里，形如 /user/12
@app.get("/user/{user_id}")
def get_user(user_id: int):     # 声明成 int，FastAPI 会自动转换并校验
    return {"id": user_id}

# 查询参数：值写在问号后面，形如 /user/list?pageIndex=1&pageSize=10
@app.get("/user/list")
def list_users(pageIndex: int = 1, pageSize: int = 10):
    return {"pageIndex": pageIndex, "pageSize": pageSize}
```

判断规则很简单：

- **函数参数名出现在路径字符串 `{}` 里** → 路径参数
- **不在路径里、且是普通类型（int/str/bool…）** → 查询参数
- **类型是 Pydantic 模型** → 请求体（见下一节）

需要额外校验时用 `Query` / `Path`：

```python
from fastapi import Query

@app.get("/user/list")
def list_users(
    pageIndex: int = Query(1, ge=1),              # 必须 >= 1
    pageSize: int = Query(10, ge=1, le=100),      # 1 ~ 100
):
    ...
```

参数不合法时，FastAPI 自动返回 **422** 并说明哪个字段错了，不需要自己写 if 判断。

## 4. 请求体：Pydantic 模型

前端 `axios.post` 发来的 JSON，用一个继承 `BaseModel` 的类来接收：

```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"          # 有默认值 = 选填；没默认值 = 必填

@app.post("/user/create")
def create_user(user: UserCreate):
    return {"code": 200, "msg": "创建成功", "data": user.model_dump()}
```

- 前端多传了模型里没有的字段？默认会被**忽略**（想禁止就用 `model_config = {"extra": "forbid"}`）。
- 类型不对、缺必填字段？自动返回 422，附带精确的错误位置。
- `user.model_dump()` 把模型转回普通字典（Pydantic v2 的写法，v1 是 `.dict()`）。

## 5. 返回值：字典或模型都行

```python
# 方式一：直接返回字典，最灵活
return {"list": [...], "total": 3}

# 方式二：声明 response_model，FastAPI 会按模型过滤字段并生成文档
@app.get("/user/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    ...
```

`response_model` 的好处是**自动脱敏**：模型里没声明的字段（比如 `password`）不会返回给前端。

## 6. 主动报错：HTTPException

```python
from fastapi import HTTPException

@app.get("/user/{user_id}")
def get_user(user_id: int):
    if user_id > 100:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {"id": user_id}
```

前端收到的是标准格式：`{"detail": "用户不存在"}`。

## 7. 自动接口文档（FastAPI 最大的特色）

服务启动后直接浏览器打开：

- <http://localhost:3001/docs> —— Swagger UI，可以**点 "Try it out" 直接发请求**
- <http://localhost:3001/redoc> —— ReDoc，纯阅读版文档
- <http://localhost:3001/openapi.json> —— 机器可读的接口描述

函数名、参数类型、`description`、`Query(...)` 的说明都会自动出现在文档里。**写完一个接口先去 /docs 点一下**，比写 curl 快得多。

> 如果 /docs 页面白屏，通常是 CDN 资源没加载出来，检查一下网络代理。

## 8. `def` 还是 `async def`？

- 处理函数里**没有** `await`（同步查库、纯计算）→ 用普通 `def`，FastAPI 会丢到线程池执行，不阻塞事件循环。
- 里面有 `await`（异步数据库驱动、异步 HTTP 请求）→ 用 `async def`。

两者混用最常见的坑：`async def` 里写同步耗时操作（比如 `requests.get`、`time.sleep`），会把整个服务卡住。

## 9. 接口多了以后：APIRouter 拆分

```python
# routers/user.py
from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["用户"])

@router.get("/list")
def list_users():
    return []
```

```python
# main.py
from routers.user import router as user_router

app.include_router(user_router)     # 最终路径 = /user/list
```

现在只有 3 个接口，全写在 `main.py` 里最简单；超过 10 个再拆，别提前设计。

## 10. CORS：前端为什么能访问

前端 `localhost:5174` 请求后端 `localhost:3001`，端口不同就不是同源，浏览器默认拦截。`main.py` 里已经配好：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", ...],   # 白名单
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

两个容易踩的点：

1. `allow_origins=["*"]` 和 `allow_credentials=True` **不能同时用**，浏览器会拒绝。
2. 浏览器报 CORS 错误时，真正的请求**可能根本没到后端**，先看 Network 面板里的预检（OPTIONS）请求。

---

# 二、开发流程（写代码的顺序）

新增一个接口时，按这个顺序走，基本不会乱：

1. **先定契约**：什么方法？什么路径？前端传什么？返回什么？
   例：`POST /user/create`，传 `{name, email, role}`，返回 `{code, msg, data}`。
2. **定数据模型**：请求体用 `BaseModel` 描述；返回结构简单就直接用字典。
3. **写路由函数**：`@app.post("/user/create")`，参数声明好类型。
4. **写业务逻辑**：先用假数据跑通，再接数据库。
5. **打开 /docs 自测**：点 "Try it out" 发一次请求，看返回是否符合契约。
6. **前端联调**：前端 axios 调同一个路径，确认跨域、字段名、数据结构都对得上。
7. **出错按顺序排查**：
   - 浏览器控制台报 CORS → 检查 `allow_origins` 是否包含前端地址
   - 返回 422 → 打开响应里的 `detail`，看是哪个字段类型不对
   - 连接被拒绝 / `ERR_CONNECTION_REFUSED` → 服务没启动，或端口被别的程序占了
   - 改了代码没生效 → 确认是 `python main.py`（自带 `reload=True`），而不是手动起的无 reload 进程

一个完整的"照抄就能跑"的例子（加到 `main.py` 末尾即可）：

```python
from pydantic import BaseModel
from fastapi import HTTPException

class UserCreate(BaseModel):
    name: str
    email: str
    role: str = "user"

@app.post("/user/create")
def create_user(user: UserCreate):
    """新建用户：先用假数据演示，后续替换成真正的数据库写入。"""
    if not user.email.endswith("@example.com"):
        raise HTTPException(status_code=400, detail="学习阶段只接受 example.com 邮箱")
    return {"code": 200, "msg": "创建成功", "success": True, "data": user.model_dump()}
```

---

# 三、常用命令

除特别标注外，全部在项目根目录 `e:\study\project\fastapi-demo1` 下执行。PowerShell 里路径要带 `.\`。

| 目的 | 命令 |
|---|---|
| 启动服务（推荐） | `uv run python app/main.py` |
| 启动服务（原生解释器） | `.\.venv\Scripts\python.exe app\main.py` |
| 启动服务（uvicorn 原生命令，需先 `cd app`） | `..\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 3001` |
| 停止服务 | 在运行的终端按 `Ctrl + C` |
| 安装/同步依赖 | `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` |
| 安装单个包 | `.\.venv\Scripts\python.exe -m pip install 包名` |
| 查看已安装的包 | `.\.venv\Scripts\python.exe -m pip list` |
| 把当前环境导出成依赖清单 | `.\.venv\Scripts\python.exe -m pip freeze > requirements.txt` |
| 激活虚拟环境（可选） | `.\.venv\Scripts\Activate.ps1`，激活后可直接用 `python`、`pip` |
| PowerShell 禁止运行脚本时 | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`（只对当前窗口生效） |
| 命令行测接口 | `Invoke-RestMethod "http://127.0.0.1:3001/user/list?pageIndex=1&pageSize=2"` |
| 查看 3001 被谁占用 | `Get-NetTCPConnection -LocalPort 3001 -State Listen` |
| 结束占用的进程 | `Stop-Process -Id <上一步查到的 PID>`（先确认这个 PID 是哪个程序） |

> 不激活虚拟环境也完全没问题，直接用 `.\.venv\Scripts\python.exe` 更不容易搞混"到底用的是哪个 Python"。
>
> `pip freeze` 会把间接依赖也一起写进去，适合锁定可复现的环境；只想记录直接依赖，就手写 `requirements.txt`。

---

# 四、uv 常用命令与注意事项

## uv 是什么

uv 是 Astral（Ruff 的作者）用 Rust 写的 Python 工具链，用一个命令替代 pip、venv、pyenv、poetry 的常用功能，速度通常比 pip 快一个数量级。

本机安装情况：

| 项 | 值 |
|---|---|
| 版本 | 0.13.5 |
| 安装目录 | `E:\software\uv`（含 `uv.exe`、`uvx.exe`、`uvw.exe`） |
| PATH | 已写入**用户级** PATH，`E:\software\uv` 排在最前面 |

```powershell
uv --version
# uv 0.13.5 (46776a95d 2026-10-21 x86_64-pc-windows-msvc)
```

**装 uv 之前就打开的终端读不到新的 PATH**，要在 VS Code 里关掉终端重新开一个。

## 本项目怎么用

本项目仍是 `requirements.txt` 模式，没有 `pyproject.toml`，所以只把 uv 当"更快的 pip + 自动找 `.venv`"来用：

| 目的 | 命令 |
|---|---|
| 启动服务（推荐） | `uv run python app/main.py` |
| 安装/同步依赖 | `uv pip install -r requirements.txt` |
| 安装单个包 | `uv pip install 包名` |
| 查看已安装的包 | `uv pip list` |
| 查看某个包的详情 | `uv pip show 包名` |
| 导出依赖清单 | `uv pip freeze > requirements.txt` |
| 确认当前用的解释器 | `uv run python -c "import sys; print(sys.executable)"` |
| 临时运行一个工具 | `uvx ruff check .`（第一次会临时下载 ruff，不装进项目） |
| 查看可用的 Python 版本 | `uv python list` |

`uv run python app/main.py` 的效果 = 找到项目里的 `.venv`，用它执行脚本，不需要激活，也不需要写 `.\.venv\Scripts\python.exe`。实测它解析到的解释器是：

```
E:\study\project\fastapi-demo1\.venv\Scripts\python.exe
```

## 注意事项

1. **现在不要执行 `uv init`**。它会生成 `pyproject.toml` + `uv.lock`，和现有 `requirements.txt` 变成两套依赖模型。混用的后果是：装包只更新其中一边，另一边越来越旧，到底哪边生效说不清。
2. **不要在项目里混用 `uv add` 和 `pip install`**。`uv add` 只属于 pyproject 模式；本项目统一用 `uv pip install`。
3. **`uv run` 会从当前目录向上找 `.venv`**。在项目根或 `app/` 下都能找到同一个环境；在无关目录执行则会用到别的环境，容易串包。
4. **`uv pip` 不会默默装进全局 Python**。找不到 `.venv` 时它会直接报错并提示先运行 `uv venv`，这是好事，能防止包装错地方。
5. **`uv sync` 本项目暂时用不了**，它需要 `pyproject.toml` + `uv.lock`；`uv venv` 也不需要，`.venv` 已经存在。
6. **uv 还能管理 Python 版本**（例如 `uv python install 3.12`）。目前不需要，你已有 3.13.15。
7. **`uv` 命令不生效** = 当前终端是安装前打开的，重开一个终端即可。

---

# 五、项目现状

## 已实现接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/` | 连通性测试 |
| GET | `/health` | 健康检查，返回 `{"status": "ok"}` |
| GET | `/user/list?pageIndex=1&pageSize=10` | 返回假用户列表，结构对齐 NestJS 的 `pagination` + `list` |
| GET | `/demo/health` | 从 `app/api.py` 的 APIRouter 挂载，演示路由拆分 |
| GET | `/docs` | 交互式接口文档 |

## 文件说明

| 文件 | 作用 |
|---|---|
| `app/main.py` | 入口：创建 app、配置 CORS、定义路由、挂载子路由、启动 uvicorn |
| `app/api.py` | 子路由：`APIRouter(prefix="/demo")`，演示如何把接口拆出去 |
| `requirements.txt` | 依赖清单（已锁定实际安装版本） |
| `.env` | 环境变量，目前只有 `PORT=3001` |
| `.venv/` | 虚拟环境，不提交 git |
| `.gitignore` | 忽略缓存和虚拟环境 |

## 端口冲突：和 NestJS 二选一

前端的 axios 写死了 `http://localhost:3001`，NestJS 也用 3001，所以**同一时刻只能启动一个后端**：

- 启动 FastAPI 前，先停掉 NestJS；反之亦然。
- 否则会报 `[WinError 10048]`（端口已被占用，通常还会带上"每个套接字地址只允许使用一次"的说明）。

## 下一步可以学

1. 用 `APIRouter` 拆分路由，按业务建 `routers/` 目录
2. 接数据库：SQLAlchemy + PostgreSQL（本机已有 PostgreSQL 18），或 SQLModel
3. 加统一响应封装、全局异常处理
4. 加 `Depends` 依赖注入，做鉴权和数据库会话管理
5. 写测试：`pytest` + `httpx.AsyncClient`
