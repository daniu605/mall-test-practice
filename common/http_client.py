"""通用 HTTP 客户端：Session 复用 + JWT token 自动携带 + 统一断言辅助。

设计意图（答辩可讲）：
1. 所有请求走同一个 Session，避免重复 TCP 握手，跑批更快；
2. token 获取与业务请求解耦，登录失败时给出明确报错而不是零散断言失败；
3. 断言辅助函数把「HTTP 状态码 + mall 业务码」双校验收敛到一处。
"""
import json
import pathlib

import requests
import yaml

CONFIG_PATH = pathlib.Path(__file__).parent.parent / "config" / "config.yaml"


def load_config() -> dict:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


class HttpClient:
    """按模块（admin/portal）实例化的带鉴权 HTTP 客户端。"""

    def __init__(self, module: str):
        cfg = load_config()
        self.cfg = cfg
        self.module_cfg = cfg[module]
        self.base_url = self.module_cfg["base_url"].rstrip("/")
        self.success_code = cfg["http"]["success_code"]
        self.timeout = cfg["http"]["timeout"]
        self.session = requests.Session()
        self.token = None

    # ---------- 登录与鉴权 ----------
    def login(self) -> str:
        """执行登录并把 token 存入请求头。"""
        resp = self.session.post(
            f"{self.base_url}{self.login_path}",
            json={
                "username": self.module_cfg["username"],
                "password": self.module_cfg["password"],
            },
            timeout=self.timeout,
        )
        body = resp.json()
        assert body.get("code") == self.success_code, f"登录失败：{body}"
        self.token = body["data"]["token"]
        self.session.headers.update(self._auth_header())
        return self.token

    @property
    def login_path(self) -> str:
        raise NotImplementedError

    def _auth_header(self) -> dict:
        raise NotImplementedError

    # ---------- 通用请求 ----------
    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        return self.session.post(f"{self.base_url}{path}", timeout=self.timeout, **kwargs)

    def post_json(self, path: str, payload: dict) -> requests.Response:
        return self.post(path, json=payload)

    # ---------- 断言辅助 ----------
    @staticmethod
    def assert_business_ok(resp: requests.Response):
        """双通道断言：HTTP 200 + mall 业务码 200。"""
        assert resp.status_code == 200, f"HTTP 状态码异常：{resp.status_code}，body={resp.text[:200]}"
        body = resp.json()
        assert body.get("code") == 200, f"业务码异常：{body}"
        return body


class AdminClient(HttpClient):
    """mall-admin 后台管理端。"""

    @property
    def login_path(self) -> str:
        return "/admin/login"

    def _auth_header(self) -> dict:
        return {"Authorization": self.token}


class PortalClient(HttpClient):
    """mall-portal 前台商城端（会员端）。"""

    @property
    def login_path(self) -> str:
        return "/sso/login"

    def _auth_header(self) -> dict:
        return {"Authorization": self.token}
