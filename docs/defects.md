# 缺陷清单与 issue 提交记录

> ⚠️ 诚实原则：以下样例是测试设计中的「预期缺陷观察点」。**必须在本地实测复现确认后**才能提 issue / 写进简历，复现不了就删掉——答辩被问到 issue 链接时打不开是致命的。

## 缺陷记录模板（对齐官方仓库 issue 格式）

### DEF-001（样例）商品搜索接口对超长关键字无长度校验

- **严重级别**：P2（功能健壮性）
- **环境**：Windows 11 / Docker Compose 部署 mall（master 分支）/ 版本日期
- **复现步骤**：
  1. 启动 mall-portal，登录测试会员
  2. POST /product/search，keyword 传入 500 个字符
  3. 观察响应
- **实际结果**：（实测填写，如 500 Internal Server Error）
- **期望结果**：入参长度校验，返回友好业务错误
- **状态**：待实测确认 → 确认后提交至 https://github.com/macrozheng/mall/issues

### DEF-002（样例）pageSize 传负数时的分页行为

- **严重级别**：P3
- **复现步骤**：GET /product/list?pageNum=1&pageSize=-1
- **实际结果**：（实测填写）
- **期望结果**：参数校验或兜底为默认分页大小
- **状态**：待实测确认

### 优化建议（样例）

- Swagger 文档中部分 portal 接口缺少参数示例，建议补充（若属实可作为文档类 issue，通过率高）

## 提交记录

| 编号 | issue 链接 | 状态 |
|---|---|---|
| DEF-001 | （提交后回填） | open/closed |
