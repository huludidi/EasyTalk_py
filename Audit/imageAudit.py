import requests
import base64

# 设置 API 访问地址和请求参数
url = 'https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined'
params = {'access_token': '24.b50d1598e39258d8a54322e57202421c.2592000.1686235940.282335-33358209'}
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
def image_audit(image_path):
    # 读取待审核的图片文件
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # 将图片数据进行 Base64 编码
    image_base64 = base64.b64encode(image_data)

    # 构造 POST 请求体
    data = {
        'image': image_base64,
        'scenes': ['antiporn', 'terror', 'politician']
    }

    # 发送 POST 请求
    response = requests.post(url, data=data, headers=headers, params=params)

    # 解析响应结果
    result = response.json()
    if result['conclusion'] == '合规':
        return True
    else:
        return False
