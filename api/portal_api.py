"""mall-portal 前台商城（会员端）接口定义。

以本地 Swagger（http://localhost:8085/swagger-ui.html）为准。
"""


class PortalApi:
    REGISTER = "/sso/register"
    LOGIN = "/sso/login"
    MEMBER_INFO = "/sso/info"

    PRODUCT_DETAIL = "/product/detail/{id}"
    PRODUCT_SEARCH = "/product/search"
    PRODUCT_CATEGORY = "/product/productCategoryList"

    CART_ADD = "/cart/add"
    CART_UPDATE = "/cart/update/quantity"
    CART_DELETE = "/cart/delete"
    CART_LIST = "/cart/list"

    ORDER_GENERATE = "/order/generateOrder"
    ORDER_LIST = "/order/list"
    ORDER_CANCEL = "/order/cancelUserOrder"
