import qianfan
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 可选：直接在代码中设置（不推荐用于生产环境）
# qianfan.get_config().ACCESS_KEY = "你的_access_key"
# qianfan.get_config().SECRET_KEY = "你的_secret_key"

def gen_wenxin_messages(prompt):
    '''
    构造文心模型请求参数 messages

    请求参数：
    prompt: 对应的用户提示词
    '''


    messages = [{"role": "user", "content": prompt}]
    return messages


def get_completion(prompt, model="ERNIE-Bot", temperature=0.01):
    '''
    获取文心模型调用结果

    请求参数：
    prompt: 对应的提示词
    model: 调用的模型，默认为 ERNIE-Bot，也可以按需选择 Yi-34B-Chat 等其他模型
    temperature: 模型输出的温度系数，控制输出的随机程度，不同模型取值范围不同（比如ERNIE-4.0-8K的temperature为0-1.0），且不能设置为 0。温度系数越低，输出内容越一致。
        '''


    chat_comp = qianfan.ChatCompletion()
    message = gen_wenxin_messages(prompt)


    resp = chat_comp.do(messages=message,
                        model=model,
                        temperature=temperature,
                        system="你是一名个人助理-小鲸鱼")

    return resp["result"]


# 测试代码
if __name__ == "__main__":
    # 测试函数
    test_prompt = "你好，请简单介绍一下自己"
    result = get_completion(test_prompt)
    print(f"提示: {test_prompt}")
    print(f"响应: {result}")
