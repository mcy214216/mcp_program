# -*- coding: utf-8 -*-
# 时间 : 2026/4/20 18:39
# 作者 : mcy
# 文件 : mcp_test1.py
"""
MCP Server: 今日计划生成器
功能：根据用户输入的任务描述，生成今日计划表单，并通过QQ邮箱发送
"""
import re
from datetime import datetime
from mcp.server.fastmcp import FastMCP
import yagmail
# ==================== 邮件配置（请修改为你的信息）====================
from config import EMAIL_USER, EMAIL_PASSWORD, EMAIL_RECEIVER
# ====================================================================

# 创建MCP服务器实例
mcp = FastMCP("DailyPlanMaker")
def parse_tasks(raw_text: str) -> list:
    """将用户输入的自然语言解析为任务列表"""
    # 按常见分隔符分割：中文/英文逗号、句号、分号、顿号、换行等
    tasks = re.split(r'[，,。；;、\n]+', raw_text)
    tasks = [t.strip() for t in tasks if t.strip()]
    if not tasks:
        tasks = [raw_text.strip()]
    return tasks


def generate_plan_content(user_input: str) -> str:
    """生成今日计划的文本内容"""
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
def generate_and_send_plan(user_input: str) -> str:
    """
    根据用户输入的任务描述，生成今日计划并发送到指定邮箱。
    参数 user_input: 字符串，例如 "写作业，买菜，锻炼"
    返回发送结果和计划内容。
    """
    if not user_input.strip():
        return "❌ 输入不能为空，请提供今天的任务描述。"

    plan_content = generate_plan_content(user_input)

    try:
        # 使用QQ邮箱的SMTP SSL配置
        yag = yagmail.SMTP(user=EMAIL_USER, password=EMAIL_PASSWORD,
                           host='smtp.qq.com', port=465, smtp_ssl=True)
        subject = f"今日计划 - {datetime.now().strftime('%Y-%m-%d')}"
        yag.send(to=EMAIL_RECEIVER, subject=subject, contents=plan_content)
        return f"✅ 计划已成功发送至 {EMAIL_RECEIVER}\n\n{plan_content}"
    except Exception as e:
        return f"❌ 邮件发送失败: {str(e)}\n\n生成的计划内容：\n{plan_content}"


@mcp.tool()
def generate_plan_only(user_input: str) -> str:
    """仅生成计划文本，不发送邮件（用于预览）"""
    if not user_input.strip():
        return "❌ 输入不能为空。"
    return generate_plan_content(user_input)


if __name__ == "__main__":
    # 以 stdio 模式运行，供 MCP 客户端调用
    mcp.run(transport='stdio')