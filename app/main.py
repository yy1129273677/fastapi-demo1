"""
文件：main.py
作用：【应用入口】FastAPI 后端的启动文件，执行 `python main.py` 时第一个被运行。

它做三件事：
    1. 创建 FastAPI 应用实例（app）
    2. 配置 CORS（跨域），让 localhost:5174 的前端能访问 localhost:3001 的后端
    3. 定义路由（URL 和处理函数的对应关系）

启动后可以访问：
    - http://localhost:3001/            根路由，测试服务是否活着
    - http://localhost:3001/health      健康检查，给运维/容器探活用
    - http://localhost:3001/user/list   示例接口，返回假用户列表
    - http://localhost:3001/docs        FastAPI 自动生成的交互式接口文档（重点，能直接在网页上点按钮试接口）
"""

import os
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from api import router as demo_router

# 读取项目根目录下的 .env 文件，把里面的键值对塞进环境变量。
# 比如 .env 里写了 PORT=3001，下面 os.getenv("PORT") 就能拿到 "3001"。
# 注意：必须在读取 PORT 之前调用，顺序不能反。
load_dotenv()

# FastAPI 应用实例：可以理解成整个后端的"总路由器"。
# 之后所有接口都通过 @app.get / @app.post 这类装饰器挂到它身上。
# title、version 只是文档信息，会显示在 /docs 页面顶部。
app = FastAPI(title="FastAPI 学习项目", version="0.1.0")
app.include_router(demo_router)

# ── 跨域配置（CORS）───────────────────────────────────────
# 为什么需要它：
#   浏览器有一条安全规则叫"同源策略"——网页只能请求和它"同源"的地址。
#   前端跑在 http://localhost:5174，后端跑在 http://localhost:3001，
#   端口不同就不算同源，浏览器默认会拦截请求并报 CORS 错误。
#   这里把前端地址加入白名单，浏览器才会放行。
#
# 为什么用具体地址而不是 ["*"]：
#   下面开启了 allow_credentials=True（允许携带 Cookie / 登录凭证），
#   而浏览器规定"允许携带凭证"时不能把来源写成 "*"（通配符），
#   否则请求依然会被拒绝。所以这里明确列出前端可能用到的地址。
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # 前端 Vite 默认端口
        "http://127.0.0.1:5173",
        "http://localhost:5174",  # 本项目前端 .env.development 里配置的端口
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    # 允许的请求方法。["*"] 表示 GET/POST/PUT/PATCH/DELETE 全都允许。
    allow_methods=["*"],
    # 允许的请求头。前端 axios 默认会带 Content-Type 和 Authorization，
    # 这里放开全部，学习阶段最省事。
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    """
    根路由：GET /

    干什么：
        最简单的连通性测试。浏览器打开 http://localhost:3001/ 能看到这段文字，
        就说明后端已经正常启动了。

    参数：
        无

    返回：
        一个字典。FastAPI 会自动把它转成 JSON，形如：
        {"message": "FastAPI 服务已启动"}

    注意：
        返回字典即可，不需要手动写 JSON 字符串，也不用设置响应头，
        FastAPI 会自动把 Content-Type 设成 application/json。
    """
    return {"message": "FastAPI 服务已启动"}


@app.get("/health")
def health_check():
    """
    健康检查：GET /health

    干什么：
        给部署工具、容器编排或监控系统调用的接口。
        它们会定时请求这个地址，返回 200 就认为服务活着，不返回就重启服务。

    参数：
        无

    返回：
        {"status": "ok"}

    注意：
        这个接口不查数据库、不调外部服务，保证"只要能响应就说明进程没死"。
    """
    return {"status": "ok"}


# 一份假的用户数据，当作"数据库"用。
# 真实项目里这里会换成查数据库（比如 SQLAlchemy 或 Prisma），
# 学习阶段先用内存里的列表，能跑通接口就行。
FAKE_USERS = [
    {"id": 3, "name": "王五", "email": "wangwu@example.com", "role": "admin"},
    {"id": 2, "name": "李四", "email": "lisi@example.com", "role": "user"},
    {"id": 1, "name": "张三", "email": "zhangsan@example.com", "role": "user"},
]


@app.get("/user/list")
def list_users(
    pageIndex: int = Query(1, ge=1, description="页码，从 1 开始"),
    pageSize: int = Query(10, ge=1, le=100, description="每页条数，最多 100"),
):
    """
    用户列表：GET /user/list?pageIndex=1&pageSize=10

    干什么：
        返回分页后的用户列表，返回结构和现有 NestJS 后端保持一致，
        方便前端以后直接切过来。

    参数：
        pageIndex：第几页，从 1 开始。不传默认 1。
        pageSize：每页几条，不传默认 10，最多 100。
            这两个参数不是从请求体里读的，而是从 URL 问号后面读的，
            所以用 Query(...) 声明。写成普通参数 FastAPI 也会自动识别为查询参数，
            用 Query 是为了顺便加上校验规则和文档说明。

    返回：
        字典，包含两部分：
        - pagination：分页信息（当前页、每页条数、总数、总页数）
        - list：当前页的用户数据

    注意：
        - ge=1 表示"大于等于 1"，le=100 表示"小于等于 100"。
          参数不合法时 FastAPI 会自动返回 422 错误，并说明哪个字段错了，
          不用自己写 if 判断。
        - 这里的数据是写死的假数据，重启服务不会保留任何修改。
    """
    # 先算出这一页要从第几条开始切。
    # 第 1 页：(1 - 1) * 10 = 0，从索引 0 开始
    # 第 2 页：(2 - 1) * 10 = 10，跳过前 10 条
    start = (pageIndex - 1) * pageSize

    # Python 切片 [start:end] 会取出索引 start 到 end-1 的元素。
    # 超出范围不会报错，只会返回空列表。
    page_items = FAKE_USERS[start : start + pageSize]

    # 总页数用向上取整：3 条数据、每页 2 条，需要 2 页。
    # (3 + 2 - 1) // 2 = 2，这是整数运算版的向上取整写法。
    total = len(FAKE_USERS)
    total_pages = (total + pageSize - 1) // pageSize

    return {
        "pagination": {
            "page": pageIndex,
            "pageSize": pageSize,
            "total": total,
            "totalPages": total_pages,
        },
        "list": page_items,
    }


# ── 启动入口 ───────────────────────────────────────────────
# 这行判断的意思是：只有"直接运行本文件"（python main.py）时才启动服务；
# 如果本文件是被别的文件 import 进去的，就不启动。
# 这样测试代码或其他程序可以安全地导入 app 而不真的起一个服务器。
if __name__ == "__main__":
    # 端口优先读 .env 里的 PORT，没有就用 3001。
    # int(...) 是因为环境变量读出来永远是字符串，uvicorn 要的是数字。
    port = int(os.getenv("PORT", "3001"))

    # host="127.0.0.1" 表示只允许本机访问，不对外网开放，本地学习更安全。
    # reload=True 表示改了代码后自动重启服务，不用手动关掉再开。
    #   注意：reload 模式要求把应用写成 "main:app" 这种"文件:变量"的字符串形式，
    #   不能直接传 app 对象，否则自动重载不生效。
    uvicorn.run("main:app", host="127.0.0.1", port=port, reload=True)
