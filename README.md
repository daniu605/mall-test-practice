# mall-test-practice — mall 开源电商系统全链路测试实战

对 GitHub 60k+ Star 的开源电商项目 [macrozheng/mall](https://github.com/macrozheng/mall) 进行的独立测试实战，覆盖**接口自动化、UI 自动化、性能压测与缺陷报告**全流程。

## 成果总览

| 产出 | 数量 |
|---|---|
| 功能测试用例（AAA 格式） | 90+ 条 |
| 接口自动化用例（Pytest+Requests） | 80+ 条 |
| UI 自动化场景（Playwright PO 模式） | 20+ 个 |
| JMeter 性能场景 | 2 组（登录/商品搜索） |
| 缺陷/优化建议 | 提交至官方仓库（见 docs/defects.md） |

## 被测环境部署

```bash
# 方式一：仅跑 mall-admin（最轻量，需 MySQL + Redis）
# 方式二：Docker Compose 全套（推荐）
git clone https://github.com/macrozheng/mall.git
cd mall/document/docker/docker-compose
docker-compose up -d
```

部署完成后核对两件事：
1. 后台接口文档：`http://localhost:8080/swagger-ui.html`（mall-admin）
2. 前台接口文档：`http://localhost:8085/swagger-ui.html`（mall-portal）

> ⚠️ **接口路径以本地 Swagger 为准**。本工程的接口封装集中在 `api/` 目录，如与你部署版本有出入，只需改 `api/` 下的路径常量，用例层不动。

## 运行测试

```bash
pip install -r requirements.txt
playwright install chromium

# 接口自动化（生成 Allure 报告）
pytest testcases/api -v --alluredir=allure-results
allure serve allure-results

# UI 自动化（有界面模式）
pytest testcases/ui -v --headed

# 性能压测（需先启动 JMeter）
jmeter -n -t perftest/mall_login.jmx -l perftest/result.jtl
```

## 目录结构

```
mall-test-practice/
├── config/config.yaml          # 环境地址、测试账号
├── common/http_client.py       # 请求封装（Session 复用、JWT token 管理）
├── api/                        # 接口定义层（admin/portal 两模块）
├── testcases/api/              # 接口自动化用例（按模块拆分）
├── testcases/ui/               # UI 自动化用例
├── pages/                      # Playwright PO 模式页面对象
├── data/                       # 测试数据（YAML 数据驱动）
├── perftest/                   # JMeter 压测脚本
└── docs/                       # 测试用例文档、缺陷清单
```

## 测试设计说明

- 用例全部按 **AAA（Arrange-Act-Assert）** 格式编写，见 `docs/test_cases.md`
- 接口用例分层：正常流 → 参数边界 → 异常码 → 鉴权/越权
- 断言不仅校验 HTTP 状态码，同时校验业务码（mall 统一返回 `code=200`）与关键字段
- 缺陷必须先在本地复现确认后才会提交 issue，样例见 `docs/defects.md`
