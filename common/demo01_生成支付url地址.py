from alipay import AliPay

# 第一步准备：支付宝的应用数据(调试阶段使用沙箱环境)
# 应用id
app_id = '*'
# 商户号
pid = '*'
# 公钥和私钥
public_key = open('alipay_public_key.pem').read()
private_key = open('app_private_key.pem').read()

# 订单支付的信息(自己系统的订单信息)
# 订单号
order_on = '20225635009090'
# 订单金额
amount = '399'
# 支付页面展示的标题
subject = f"商城订单{order_on}支付"

# 初始化
pay = AliPay(
    appid=app_id,
    # 支付宝回调我们自己系统的url 等到部署到服务器配置就好了
    app_notify_url=None,
    # 私钥
    app_private_key_string=private_key,
    # 公钥
    alipay_public_key_string=public_key,
    # 开启debug(如果是部署好的项目要关掉)
    debug=True,
)
# 4.生成手机应用的支付地址
# url = pay.api_alipay_trade_wap_pay(
#     # 支付页面的标题
#     subject=subject,
#     # 商户生成的订单号(自己系统中的订单号)
#     out_trade_no=order_on,
#     # 订单支付的金额
#     total_amount=amount,
#     # 部署好项目以后在配置
#     return_url=None,
#     notify_url=None,
# )
# 5. 生成pc端浏览器网站的支付页面地址
url = pay.api_alipay_trade_page_pay(
    # 支付页面的标题
    subject=subject,
    # 商户生成的订单号(自己系统中的订单号)
    out_trade_no=order_on,
    # 订单支付的金额
    total_amount=amount,
    # 部署好项目以后在配置
    return_url=None,
    notify_url=None,
)
# # 6.生成app端支付页面地址
# url = pay.api_alipay_trade_app_pay(
#     # 支付页面的标题
#     subject=subject,
#     # 商户生成的订单号(自己系统中的订单号)
#     out_trade_no=order_on,
#     # 订单支付的金额
#     total_amount=amount,
#     # 部署好项目以后在配置
#     return_url=None,
#     notify_url=None,
# )

pay_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do?' + url
print(pay_url)
