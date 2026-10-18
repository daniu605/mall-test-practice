# mall 功能测试用例（AAA 格式，节选 15 条代表性用例）

> 完整用例 90+ 条，按模块拆分维护；优先级定义：P0 核心交易链路 / P1 主功能 / P2 边界与异常 / P3 兼容与体验。

## 模块一：后台登录（P0）

| 用例编号 | 用例标题 | 优先级 | Arrange 准备 | Act 执行 | Assert 断言 |
|---|---|---|---|---|---|
| TC-LOGIN-001 | 正确账号密码登录 | P0 | 已部署 mall-admin，存在 admin 账号 | POST /admin/login，正确用户名密码 | HTTP 200，业务码 200，返回非空 token |
| TC-LOGIN-002 | 密码错误登录 | P1 | 同上 | POST /admin/login，错误密码 | 业务码非 200，提示「用户名或密码错误」 |
| TC-LOGIN-003 | 用户名为空 | P2 | 同上 | POST /admin/login，username="" | 业务码非 200，有参数校验提示，无 500 |
| TC-LOGIN-004 | 未携带 token 访问受保护接口 | P0 | 不登录构造裸客户端 | GET /product/list | HTTP 401 |

## 模块二：商品管理（P1）

| 用例编号 | 用例标题 | 优先级 | Arrange | Act | Assert |
|---|---|---|---|---|---|
| TC-PROD-001 | 商品分页列表默认查询 | P1 | 登录 admin | GET /product/list?pageNum=1&pageSize=5 | 返回 list 长度 ≤5，含 total 字段 |
| TC-PROD-002 | 页码越界返回空列表 | P2 | 同上 | pageNum=9999 | 业务码 200 且 list 为空 |
| TC-PROD-003 | pageSize 传负数 | P2 | 同上 | pageSize=-1 | 无 500，返回兜底分页或校验提示 |
| TC-PROD-004 | 品牌列表查询 | P1 | 同上 | GET /brand/list | 返回 list 数组 |

## 模块三：购物车（P0）

| 用例编号 | 用例标题 | 优先级 | Arrange | Act | Assert |
|---|---|---|---|---|---|
| TC-CART-001 | 未登录加购被拦截 | P0 | 裸客户端 | POST /cart/add | HTTP 401 |
| TC-CART-002 | 登录后正常加购 | P0 | 已登录会员，存在在售商品 SKU | POST /cart/add | 业务码 200；GET /cart/list 出现该商品 |
| TC-CART-003 | 修改购物车数量 | P1 | 购物车已有商品 | POST /cart/update/quantity quantity=3 | 业务码 200，再次查询数量为 3 |
| TC-CART-004 | 加购数量为 0 | P2 | 已登录 | POST /cart/add quantity=0 | 业务校验拒绝，无 500 |
| TC-CART-005 | 删除购物车商品 | P1 | 购物车已有商品 | POST /cart/delete | 业务码 200，列表中不再存在 |

## 模块四：订单（P0）

| 用例编号 | 用例标题 | 优先级 | Arrange | Act | Assert |
|---|---|---|---|---|---|
| TC-ORDER-001 | 购物车商品正常下单 | P0 | 购物车有商品，存在收货地址 | POST /order/generateOrder | 业务码 200，返回订单号；订单列表可见 |
| TC-ORDER-002 | 空购物车下单 | P2 | 购物车为空 | cartItemIds=[] | 业务错误提示，无 500 |
| TC-ORDER-003 | 未登录下单被拦截 | P0 | 裸客户端 | POST /order/generateOrder | HTTP 401 |

## 模块六：品牌管理（写操作数据自清理）

| 用例编号 | 用例标题 | 优先级 | Arrange | Act | Assert |
|---|---|---|---|---|---|
| TC-BRAND-001 | 创建品牌全链路 | P1 | uuid 唯一品牌名 | POST /brand/create → 检索 → 更新 → 删除 | 各步业务码 200，列表可见，清理后环境复原 |
| TC-BRAND-002 | 缺 name 创建被拦截 | P2 | 缺 name 的 payload | POST /brand/create | 业务码非 200，不 500 |
| TC-BRAND-003 | 删除不存在品牌 | P3 | 超大 id | POST /brand/delete/99999999 | 业务报错，不 500 |

## 模块七：分页与登录数据驱动矩阵

| 用例编号 | 用例标题 | 优先级 | Arrange | Act | Assert |
|---|---|---|---|---|---|
| TC-PAGE-001~005 | pageNum 边界矩阵 | P2 | 参数化 [1,2,9999,0,-1] | GET /product/list | 全部 HTTP 200，越界页空列表 |
| TC-PAGE-006~009 | pageSize 边界矩阵 | P2 | 参数化 [1,100,0,-1] | GET /product/list | HTTP 200，合法容量不超限 |
| TC-LOGIN-D01~D06 | 登录异常凭据矩阵 | P0 | YAML 数据驱动（空用户名/错密码/注入片段/超长输入/XSS） | POST /admin/login | 全部登录失败，接口不 500 |
| TC-CART-Q01~Q05 | 加购数量边界 | P0 | YAML 数据驱动（0/-1/999999/1/999） | POST /cart/add | 非法数量被拦截（防资损），正常数量成功 |

## 覆盖率统计口径

- 功能用例：90+ 条，按模块分布——登录鉴权 12 / 商品 18 / 购物车 16 / 订单 20 / 优惠券 10 / 会员 8 / 兼容性 6
- 需求覆盖：mall 官方文档「业务篇」全部模块均有用例映射
