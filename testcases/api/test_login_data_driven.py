"""登录鉴权数据驱动：用户名/密码异常组合矩阵（数据外置 YAML，新增场景零代码改动）。"""
import pathlib

import pytest
import yaml

from common.http_client import AdminClient

pytestmark = [pytest.mark.regression]

DATA_PATH = pathlib.Path(__file__).parent.parent.parent / "data" / "login_cases.yaml"
with open(DATA_PATH, encoding="utf-8") as _f:
    _LOGIN_CASES = yaml.safe_load(_f)["cases"]


class TestLoginDataDriven:
    """登录异常流数据驱动：覆盖空值/错误值/注入片段/超长输入。"""

    @pytest.mark.parametrize(
        "case",
        _LOGIN_CASES,
        ids=[c["name"] for c in _LOGIN_CASES],
    )
    def test_login_invalid_credentials_rejected(self, case):
        # Arrange：按 YAML 用例构造凭据
        client = AdminClient()
        client.module_cfg["username"] = case["username"]
        client.module_cfg["password"] = case["password"]
        # Act / Assert：非法凭据必须登录失败，且接口不 500
        with pytest.raises(AssertionError, match="登录失败"):
            client.login()
