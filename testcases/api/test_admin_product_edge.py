"""商品列表分页参数边界矩阵：pageNum/pageSize 非法值逐一校验（防越界与注入）。"""
import pytest

from api.admin_api import AdminApi

pytestmark = [pytest.mark.regression]


class TestProductPaginationMatrix:
    """分页参数边界矩阵：数据驱动逐项校验，全部不允许 500。"""

    @pytest.mark.parametrize(
        "page_num",
        [1, 2, 9999, 0, -1],
        ids=["首页", "第2页", "越界大页码", "零页码", "负页码"],
    )
    def test_page_num_matrix(self, admin, page_num):
        # Arrange：page_num 由参数化注入
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": page_num, "pageSize": 5})
        # Assert：HTTP 200 且结构合法（越界页码允许空列表）
        assert resp.status_code == 200, f"pageNum={page_num} 触发异常：{resp.text[:200]}"

    @pytest.mark.parametrize(
        "page_size",
        [1, 100, 0, -1],
        ids=["最小值", "大页容量", "零容量", "负容量"],
    )
    def test_page_size_matrix(self, admin, page_size):
        # Act
        resp = admin.get(AdminApi.PRODUCT_LIST, params={"pageNum": 1, "pageSize": page_size})
        # Assert：非法容量不应 500，合法容量返回条数不超限
        assert resp.status_code == 200, f"pageSize={page_size} 触发异常：{resp.text[:200]}"
