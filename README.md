# 校园二手交易平台

> Python Flask + Bootstrap + SQLite 课程设计项目

一个专为高校校园设计的二手物品交易 Web 平台，支持用户注册登录、商品发布与搜索、在线购买、购物车、留言评论、私信聊天、管理员后台等完整功能。

## 功能概览

### 用户系统
- **注册**：用户名 + 手机号 + 密码（Werkzeug 哈希加密）
- **登录/退出**：Flask-Login 会话管理
- **管理员**：预设 admin/admin123，拥有后台管理权限

### 商品管理
- **发布商品**：填写标题、分类、价格、描述，支持图片上传
- **商品浏览**：展示所有在售商品，支持多条件搜索
- **关键词搜索**：模糊匹配商品名称和描述
- **分类筛选**：书籍 / 电子产品 / 生活用品 / 衣物 / 运动器材 / 其他
- **价格排序**：最新发布 / 价格升序 / 价格降序
- **价格区间筛选**：最低价 ~ 最高价
- **最新上架**：首页展示最近发布的 8 件商品
- **商品详情**：完整信息 + 卖家联系 + 操作按钮

### 交易流程
- **立即购买**：一键将商品标记为"已售"
- **购物车**：暂存心仪商品，支持添加和移除
- **自动清理**：商品售出后从所有用户购物车中移除

### 互动功能
- **商品留言**：在商品详情页发表公开留言
- **私信聊天**：用户间一对一私信，支持未读消息红点提示
- **联系卖家**：商品详情页快捷入口

### 管理后台
- **用户管理**：查看所有用户，删除违规用户（管理员受保护）
- **商品管理**：查看所有商品，删除违规商品

## 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 后端框架 | **Python Flask 3.1** | 轻量级 Web 框架 |
| 数据库 ORM | **SQLAlchemy 2.0** | Python 最流行的 ORM |
| 数据库 | **SQLite** | 零配置，单文件存储 |
| 用户认证 | **Flask-Login** | 会话管理 |
| 密码加密 | **Werkzeug Security** | 不可逆哈希 |
| 表单处理 | **Flask-WTF** | CSRF 保护 + 验证 |
| 前端框架 | **Bootstrap 5.3** | 响应式 UI |
| 图标库 | **Bootstrap Icons 1.11** | 免费矢量图标 |
| 模板引擎 | **Jinja2** | Flask 内置 |

## 项目结构

```
campus-trade/
├── app.py                        # Flask 主程序 (15 个路由)
├── models.py                     # 数据模型 (5 张表)
├── forms.py                      # 表单验证 (5 个表单)
├── requirements.txt              # Python 依赖
├── .gitignore
├── static/
│   └── uploads/                  # 商品图片目录
└── templates/                    # 前端模板 (12 个)
    ├── base.html                 # 基础布局（导航栏）
    ├── home.html                 # 欢迎首页
    ├── browse.html               # 商品浏览页
    ├── login.html                # 登录
    ├── register.html             # 注册
    ├── publish.html              # 发布商品
    ├── product_detail.html       # 商品详情 + 留言
    ├── cart.html                 # 购物车
    ├── messages.html             # 私信列表
    ├── conversation.html         # 私信对话
    ├── my_products.html          # 我的发布
    └── admin.html                # 管理后台
```

## 数据库设计

### 用户表 (users)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 用户 ID |
| username | String(50) UNIQUE | 用户名 |
| password_hash | String(256) | 密码哈希 |
| phone | String(20) | 手机号 |
| is_admin | Boolean | 是否管理员 |
| created_at | DateTime | 注册时间 |

### 商品表 (products)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 商品 ID |
| title | String(100) | 商品名称 |
| description | Text | 商品描述 |
| price | Float | 价格 |
| category | String(30) | 分类 |
| image | String(200) | 图片路径 |
| status | String(10) | 在售/已售 |
| seller_id | FK→users.id | 卖家 |
| created_at | DateTime | 发布时间 |

### 留言表 (messages)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 留言 ID |
| content | Text | 留言内容 |
| product_id | FK→products.id | 关联商品 |
| user_id | FK→users.id | 留言用户 |
| created_at | DateTime | 留言时间 |

### 私信表 (private_messages)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 私信 ID |
| content | Text | 私信内容 |
| sender_id | FK→users.id | 发送者 |
| receiver_id | FK→users.id | 接收者 |
| is_read | Boolean | 是否已读 |
| created_at | DateTime | 发送时间 |

### 购物车表 (cart_items)
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer PK | 记录 ID |
| user_id | FK→users.id | 用户 |
| product_id | FK→products.id | 商品 |
| created_at | DateTime | 添加时间 |

## 快速开始

### 环境要求
- Python 3.8+

### 安装运行

```bash
# 1. 克隆项目
git clone git@github.com:LiHuaInCh/campus-trade.git
cd campus-trade

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py
```

浏览器访问 **http://127.0.0.1:5000**

### 默认账户

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 管理员 | admin | admin123 |

## 系统路由

| 路由 | 方法 | 说明 | 登录 |
|------|------|------|------|
| `/` | GET | 欢迎首页 | 否 |
| `/browse` | GET | 商品浏览（搜索筛选） | 否 |
| `/register` | GET/POST | 用户注册 | 否 |
| `/login` | GET/POST | 用户登录 | 否 |
| `/logout` | GET | 退出登录 | 是 |
| `/publish` | GET/POST | 发布商品 | 是 |
| `/product/<id>` | GET/POST | 商品详情 + 留言 | 否 |
| `/product/<id>/buy` | POST | 购买商品 | 是 |
| `/cart` | GET | 查看购物车 | 是 |
| `/cart/add/<id>` | POST | 加入购物车 | 是 |
| `/cart/remove/<id>` | POST | 移除购物车 | 是 |
| `/messages` | GET | 私信列表 | 是 |
| `/messages/<id>` | GET/POST | 私信对话 | 是 |
| `/my-products` | GET | 我的发布 | 是 |
| `/admin` | GET | 管理后台 | 管理员 |
| `/admin/users/<id>/delete` | POST | 删除用户 | 管理员 |
| `/admin/products/<id>/delete` | POST | 删除商品 | 管理员 |

## 安全特性

- 密码 Werkzeug 哈希加密存储，不可逆
- Flask-WTF CSRF 跨站请求伪造保护
- 表单前后端双重验证
- 管理员权限验证装饰器
- 文件上传类型限制（仅允许图片格式）
- UUID 重命名上传文件，防冲突

## 许可证

本项目仅用于课程设计学习目的。
