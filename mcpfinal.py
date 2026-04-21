# -*- coding: utf-8 -*-
# 时间 : 2026/4/21 17:07
# 作者 : mcy
# 文件 : mcpfinal.py
# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# 时间 : 2026/4/21 17:07
# 作者 : mcy
# 文件 : mcpfinal.py
# -*- coding: utf-8 -*-
"""
MCP Server: 邮件助手 - 包含两个工具
1. 生成今日计划并发送（带任务解析和格式）
2. 发送自定义邮件（AI 自由生成主题和正文）
"""

import os
import re
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import yagmail

# ==================== 邮件配置（优先级：环境变量 > config.py）====================
from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER
DEFAULT_RECEIVER = EMAIL_RECEIVER # 默认收件人

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))

# ==================== 新增：联系人映射（从 config.py 导入，若无则为空）====================
try:
    from config import CONTACTS  # 期望格式: CONTACTS = {"张三": "zhang@example.com", "李四": "li@example.com"}
except ImportError:
    CONTACTS = {}

def resolve_recipient(recipient: str) -> str:
    """
    解析收件人：
    - 如果输入包含 '@' 则直接返回
    - 否则从 CONTACTS 字典中查找（不区分大小写），返回对应邮箱
    - 未找到则返回原值
    """
    if not recipient:
        return recipient
    recipient = recipient.strip()
    if '@' in recipient:
        return recipient
    # 大小写不敏感查找
    for name, email in CONTACTS.items():
        if name.lower() == recipient.lower():
            return email
    return recipient  # 未找到则原样返回（后续发送会失败，但保留提示）
# ====================================================================

mcp = FastMCP("MailAssistant")  # 更名为更通用的名称


def send_email(to: str, subject: str, content: str) -> None:
    """通用邮件发送函数（使用 yagmail）"""
    yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD,
                       host=SMTP_HOST, port=SMTP_PORT, smtp_ssl=True)
    yag.send(to=to, subject=subject, contents=content)
    yag.close()


# -------------------- 工具1：生成计划并发送 --------------------
def parse_tasks(raw_text: str) -> list:
    """将用户输入的自然语言解析为任务列表"""
    tasks = re.split(r'[，,。；;、\n]+', raw_text)
    tasks = [t.strip() for t in tasks if t.strip()]
    if not tasks:
        tasks = [raw_text.strip()]
    return tasks


def generate_plan_content(user_input: str) -> str:
    """生成今日计划的文本内容（带格式）"""
    tasks = parse_tasks(user_input)
    today = datetime.now().strftime("%Y-%m-%d %A")
    weekday_cn = {
        "Monday": "星期一", "Tuesday": "星期二", "Wednesday": "星期三",
        "Thursday": "星期四", "Friday": "星期五", "Saturday": "星期六",
        "Sunday": "星期日"
    }.get(today.split()[-1], "")
    date_str = f"{today.split()[0]} {weekday_cn}"

    plan = f"📋 今日计划（{date_str}）\n\n"
    plan += f"基于你说：\n「{user_input}」\n\n"
    plan += "我为你整理了以下待办事项：\n"
    for i, task in enumerate(tasks, 1):
        plan += f"{i}. □ {task}\n"
    plan += "\n---\n✨ 保持专注，今天也要加油哦！"
    return plan


@mcp.tool()
def generate_and_send_plan(user_input: str, to: str = None) -> str:
    """
    根据用户输入的任务描述，生成今日计划，并发送邮件到指定邮箱。
    如果不提供 to 参数，则发送到默认邮箱。
    注意：to 参数可以是邮箱地址，也可以是联系人名称（需在 config.py 中定义 CONTACTS 映射）。

    参数:
        user_input: 任务描述，例如 "写作业，买菜，锻炼"
        to: 收件人邮箱地址或联系人名称（可选）

    返回:
        发送结果和计划内容
    """
    if not user_input or not user_input.strip():
        return "❌ 输入不能为空，请提供今天的任务描述。"

    # 处理收件人：如果提供了 to，则解析联系人；否则使用默认
    if to and to.strip():
        raw_receiver = to.strip()
        receiver = resolve_recipient(raw_receiver)
        if raw_receiver != receiver and '@' not in raw_receiver:
            # 说明是通过联系人名称转换的，可以增加提示（可选）
            pass
    else:
        receiver = DEFAULT_RECEIVER

    if not receiver:
        return "❌ 未指定收件人且未配置默认收件人。"

    plan_content = generate_plan_content(user_input)
    try:
        subject = f"今日计划 - {datetime.now().strftime('%Y-%m-%d')}"
        send_email(to=receiver, subject=subject, content=plan_content)
        return f"✅ 计划已成功发送至 {receiver}\n\n{plan_content}"
    except Exception as e:
        return f"❌ 邮件发送失败: {str(e)}\n\n生成的计划内容：\n{plan_content}"


# -------------------- 工具2：发送自定义邮件（无计划格式） --------------------
@mcp.tool()
def send_custom_email(to: str, subject: str, body: str) -> str:
    """
    发送自定义邮件。AI 应根据用户的口头要求，生成合适的主题和正文，然后调用此工具。
    注意：to 参数可以是邮箱地址，也可以是联系人名称（需在 config.py 中定义 CONTACTS 映射）。

    参数:
        to: 收件人邮箱地址或联系人名称（必填）
        subject: 邮件主题（AI 根据对话内容生成）
        body: 邮件正文（AI 根据对话内容生成，可以是纯文本或简单 HTML）

    返回:
        发送结果
    """
    if not to or not to.strip():
        return "❌ 收件人地址不能为空。"
    if not subject or not subject.strip():
        return "❌ 邮件主题不能为空。"
    if not body or not body.strip():
        return "❌ 邮件正文不能为空。"

    # 解析联系人
    raw_receiver = to.strip()
    receiver = resolve_recipient(raw_receiver)
    if raw_receiver != receiver and '@' not in raw_receiver:
        # 可选：可以添加日志或提示，但不需要修改返回信息
        pass

    try:
        send_email(to=receiver, subject=subject.strip(), content=body.strip())
        return f"✅ 自定义邮件已成功发送至 {receiver}"
    except Exception as e:
        return f"❌ 邮件发送失败: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport='stdio')