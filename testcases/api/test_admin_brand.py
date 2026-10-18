"""品牌管理模块：CRUD 全链路 + 异常参数（写操作数据自清理，保证可重复执行）。"""
import uuid

import pytest

from api.admin_api import AdminApi

pytestmark = [pytest.mark.regression]


class TestBrandList:
    """品牌列表查询：分页与筛选。"""

    def test_list_default(self, admin):
        # Act
        resp = admin.get(AdminApi.BRAND_LIST, params={"pageNum": 1, "pageSize": 10})
        # Assert
        body = admin.assert_business_ok(resp)
        assert body["data"]["pageNum"] == 1
        assert isinstance(body["data"]["list"], list)

    def test_list_page_size_edge(self, admin):
        # Act：pageSize=1 边界
        resp = admin.get(AdminApi.BRAND_LIST, params={"pageNum": 1, "pageSize": 1})
        # Assert
        body = admin.assert_business_ok(resp)
        assert len(body["data"]["list"]) <= 1

    def test_list_invalid_page_num(self, admin):
        # Act：pageNum 为 0/负数
        for page in (0, -1):
            resp = admin.get(AdminApi.BRAND_LIST, params={"pageNum": page, "pageSize": 5})
            # Assert：非法页码不应 500
            assert resp.status_code == 200, f"pageNum={page} 触发异常响应：{resp.text[:200]}"


class TestBrandCrud:
    """品牌增改删：新增数据用 uuid 命名并在 finally 清理，保证用例独立可重跑。"""

    def test_create_update_delete_flow(self, admin):
        # Arrange：uuid 唯一品牌名
        brand_name = f"测试品牌_{uuid.uuid4().hex[:8]}"
        payload = {"name": brand_name, "sort": 0, "factoryStatus": 1, "showStatus": 1}
        created_id = None
        try:
            # Act：创建
            resp = admin.post_json(AdminApi.BRAND_CREATE, payload)
            body = admin.assert_business_ok(resp)
            # Assert：业务码 200，返回品牌 id
            created_id = body["data"]
            assert created_id, "创建品牌应返回 id"

            # Act：更新展示状态
            update_payload = dict(payload, showStatus=0)
            resp = admin.post_json(AdminApi.BRAND_UPDATE.format(id=created_id), update_payload)
            # Assert
            admin.assert_business_ok(resp)

            # Act：按名称检索确认可见
            resp = admin.get(AdminApi.BRAND_LIST, params={"pageNum": 1, "pageSize": 50, "name": brand_name})
            body = admin.assert_business_ok(resp)
            # Assert：新品牌应出现在列表中
            names = [item["name"] for item in body["data"]["list"]]
            assert brand_name in names, f"新创建品牌未出现在列表：{names[:5]}"
        finally:
            # Cleanup：删除测试数据，保证环境可重复执行
            if created_id:
                admin.post(f"{AdminApi.BRAND_DELETE}/{created_id}")

    def test_create_missing_name_rejected(self, admin):
        # Arrange：缺 name 的非法 payload
        payload = {"sort": 0, "factoryStatus": 1, "showStatus": 1}
        # Act
        resp = admin.post_json(AdminApi.BRAND_CREATE, payload)
        # Assert：应返回业务错误而非 500
        assert resp.status_code == 200, f"缺 name 触发 500：{resp.text[:200]}"
        assert resp.json().get("code") != 200, "缺 name 应被业务校验拦截"

    def test_delete_nonexistent_brand(self, admin):
        # Act：删除不存在的 id（超大 id）
        resp = admin.post(f"{AdminApi.BRAND_DELETE}/99999999")
        # Assert：不应 500，业务码非 200 即可
        assert resp.status_code == 200, f"删除不存在品牌触发 500：{resp.text[:200]}"
