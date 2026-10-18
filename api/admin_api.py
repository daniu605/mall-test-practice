"""mall-admin 后台管理接口定义。

接口路径以本地 Swagger（http://localhost:8080/swagger-ui.html）为准，
集中在此维护，用例层不写死路径。
"""


class AdminApi:
    LOGIN = "/admin/login"
    ADMIN_INFO = "/admin/info"
    PRODUCT_LIST = "/product/list"
    BRAND_LIST = "/brand/list"
    BRAND_UPDATE = "/brand/update/{id}"
    PRODUCT_CATEGORY_LIST = "/productCategory/list/{parentId}"
    ORDER_LIST = "/order/list"
