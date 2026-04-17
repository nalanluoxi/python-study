#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/nalan/IdeaProjects/python-test/py/ReadParquetData/aiTest')

from ai import get_completion

def test_api_call():
    """测试实际的 API 调用"""

    print("=== 测试 API 调用 ===")

    try:
        # 测试一个简单的提示
        prompt = "你好，请介绍一下自己"
        response = get_completion(prompt, model="ERNIE-Bot")

        print(f"提示: {prompt}")
        print(f"响应: {response}")
        print("\n✅ API 调用成功！")

    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")
        return False

    return True

if __name__ == "__main__":
    test_api_call()