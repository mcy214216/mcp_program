# -*- coding: utf-8 -*-
# 时间 : 2026/4/21 00:06
# 作者 : mcy
# 文件 : cs1.py
# import yagmail
#
# EMAIL_USER = "953302984@qq.com"          # 你的邮箱
# EMAIL_PASSWORD = "epzverrwrrngbfii" # 邮箱授权码（不是密码）
# EMAIL_RECEIVER = "953302984@qq.com"    # 接收计划的邮箱（可以是自己）
#
# try:
#     # 明确指定 QQ 邮箱的 SMTP 服务器和 SSL 端口
#     yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD,
#                        host='smtp.qq.com', port=465, smtp_ssl=True)
#     yag.send(to=EMAIL_RECEIVER, subject="QQ邮箱测试", contents="这是一封通过QQ邮箱发送的测试邮件")
#     print("✅ QQ邮箱发送成功")
# except Exception as e:
#     print(f"❌ 发送失败: {e}")
