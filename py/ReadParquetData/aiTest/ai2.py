# 请安装 OpenAI SDK : pip install openai
# apiKey 获取地址： https://console.bce.baidu.com/qianfan/ais/console/apiKey
# 支持的模型列表： https://cloud.baidu.com/doc/qianfan-docs/s/7m95lyy43

from openai import OpenAI


def send(promot):
    client = OpenAI(
        base_url='https://qianfan.baidubce.com/v2',
        api_key='bce-v3/ALTAK-ueAC4noLnhKUZaQPDuHi1/180e444e3442375ad13137d38f19573d35e4a172'
    )
    system_promot = """
    ###角色身份
    你的名字叫发财,你的身份是一个java面试官的身份,高级java工程师的身份,作为一个面试官对用户进行提问,同时对用户的回答进行分析,指出用户回答的不足和优点,懂得java基础,javaweb,redis,mysql,kafka,操作系统,计算机网络,springboot,springclould等领域的知识和底层原理,如果用户有其他方向的技术了解可以进一步提问.同时每当一次提问,需要进行等待用户回答,对用户回答进行分析,指出不足和优待你,之后询问用户继续提问下一个方向,或者继续深入提问,或者结束面试.
    
    ###提问示例
    
    ##示例1
    Q:你了解过Java底层么,能介绍一下Java的HashMap底层是如何实现的么?
    A:不太了解
    Q:在 Java 中，HashMap 是一个基于哈希表实现的映射（Map）接口，它通过键（key）和值（value）对来存储数据。HashMap 的底层实现涉及多个关键数据结构和机制......
    是否进行深入的提问,或者换一个方向进行提问?
    A:深入提问
    Q:HashMap是线程安全的么,会有什么线程安全问题?是否有线程安全的map类?如何实现的?
    
    ##示例2:
    Q:你了解过Java底层么,能介绍一下Java的HashMap底层是如何实现的么?
    A:在 Java 中，HashMap 是一个基于哈希表实现的映射（Map）接口，它通过键（key）和值（value）对来存储数据。HashMap 的底层实现涉及多个关键数据结构和机制......
    Q:你说的没问题,准确的说道的核心机制......但是还有一些不足地方,比如.......是否进行深入的提问,或者换一个方向进行提问?
    """
    response = client.chat.completions.create(
        model="ernie-4.5-turbo-128k",
        messages=[
            {
                "role": "system",
                "content": f"{system_promot}"
            },
            {
                "role": "user",
                "content": f"{promot}"
            },
        ],
        temperature=0.8,
        top_p=0.8,
        extra_body={
            "penalty_score": 1,
            "stop": [],
            "web_search": {
                "enable": False,
                "enable_trace": False
            }
        }
    )
    return response.choices[0].message.content


def main():
    i = 0
    while i == 0:
        promot = input("请输入提示词：(输入[结束回话]结束对话)")
        if promot == "结束回话":
            break
        s = send(promot)
        print(s)
    print("结束回话")


if __name__ == "__main__":
    main()
