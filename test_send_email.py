# -*- coding: utf-8 -*-
# 时间 : 2026/4/21 00:06
# 作者 : mcy
# 文件 : test_send_email.py
import yagmail

from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER

try:
    # 明确指定 QQ 邮箱的 SMTP 服务器和 SSL 端口
    yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD,
                       host='smtp.qq.com', port=465, smtp_ssl=True)
    yag.send(to=EMAIL_RECEIVER, subject="QQ邮箱测试", contents="这是一封通过QQ邮箱发送的测试邮件")
    print("✅ QQ邮箱发送成功")
except Exception as e:
    print(f"❌ 发送失败: {e}")
