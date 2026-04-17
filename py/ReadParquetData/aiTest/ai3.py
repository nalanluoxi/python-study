import requests
import json

def wenxin_embedding(text: str):


    """
    curl --location 'https://qianfan.baidubce.com/v2/embeddings' \
    --header 'Content-Type: application/json' \
    --header 'Authorization: Bearer bce-v3/ALTAK-*********/614fb**********' \
    --data '{
        "model": "embedding-v1",
        "input":["White T-shirt"]
    }'

    """


    # 获取环境变量 wenxin_api_key、wenxin_secret_key
    api_key = "YOUR_BAIDU_API_KEY"
    secret_key = "YOUR_BAIDU_SECRET_KEY"

    # 使用API Key、Secret Key向https://aip.baidubce.com/oauth/2.0/token 获取Access token
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={0}&client_secret={1}".format(api_key, secret_key)
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    token_response = response.json()
    print('Token获取响应:', token_response)  # 调试信息

    access_token = token_response.get("access_token")
    if not access_token:
        print('获取access_token失败:', token_response)
        raise Exception(f"获取access_token失败: {token_response}")

    # 通过获取的Access token 来embedding text
    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/embeddings/embedding-v1?access_token=" + str(access_token)
    input = []
    input.append(text)
    payload = json.dumps({
        "input": input
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)


    #return json.loads(response.text)
# text应为List(string)
text = "要生成 embedding 的输入文本，字符串形式。"
response = wenxin_embedding(text=text)
print('完整响应:', json.dumps(response, indent=2, ensure_ascii=False))

# 检查响应中有哪些键
print('响应中包含的键:', list(response.keys()))

# 只有在键存在的情况下才打印
if 'id' in response:
    print('本次embedding id为：{}'.format(response['id']))
else:
    print('响应中没有id字段')

if 'created' in response:
    print('本次embedding产生时间戳为：{}'.format(response['created']))
else:
    print('响应中没有created字段')

if 'object' in response:
    print('返回的embedding类型为:{}'.format(response['object']))
else:
    print('响应中没有object字段')

if 'data' in response and len(response['data']) > 0:
    print('embedding长度为：{}'.format(len(response['data'][0]['embedding'])))
    print('embedding（前10）为：{}'.format(response['data'][0]['embedding'][:10]))
else:
    print('响应中没有data字段或data为空')
