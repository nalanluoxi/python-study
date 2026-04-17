#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import qianfan
import os

def test_qianfan_config():
    """测试 Qianfan 配置"""

    # 获取配置
    config = qianfan.get_config()

    print("=== Qianfan 配置检查 ===")
    print(f"ACCESS_KEY: {'已设置' if config.ACCESS_KEY else '未设置'}")
    print(f"SECRET_KEY: {'已设置' if config.SECRET_KEY else '未设置'}")
    print(f"AK: {'已设置' if config.AK else '未设置'}")
    print(f"SK: {'已设置' if config.SK else '未设置'}")

    # 检查环境变量
    print("\n=== 环境变量检查 ===")
    print(f"QIANFAN_ACCESS_KEY: {'已设置' if os.getenv('QIANFAN_ACCESS_KEY') else '未设置'}")
    print(f"QIANFAN_SECRET_KEY: {'已设置' if os.getenv('QIANFAN_SECRET_KEY') else '未设置'}")

    # 尝试创建 ChatCompletion 实例
    try:
        chat_comp = qianfan.ChatCompletion()
        print("\n✅ ChatCompletion 实例创建成功")
        return True
    except Exception as e:
        print(f"\n❌ ChatCompletion 实例创建失败: {e}")
        return False

if __name__ == "__main__":
    test_qianfan_config()