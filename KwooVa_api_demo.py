import os
import math
import json
import shutil

from tqdm import tqdm


import requests
import websocket
import json
import time

# 从环境中获取访问密钥
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
if not ACCESS_TOKEN:
    raise Exception("请设置环境变量 ACCESS_TOKEN")

BASE_URL = 'https://api.tgkwai.com'

# 上传附件
def upload_attachment(file_path):
    """
    上传附件到服务器

    Args:
        file_path (str): 上传图片的本地路径

    Raises:
        Exception: 上传失败的报错信息

    Returns:
        str: 图片上传到服务器后的URL
    """
    url = f"{BASE_URL}/api/v1/attachments/upload"
    headers = {
        'X-Token': f'Bearer {ACCESS_TOKEN}'
    }
    files = {
        'type': (None, 'image'),
        'file': open(file_path, 'rb')
    }
    response = requests.post(url, headers=headers, files=files)
    response_data = response.json()
    if response_data['code'] == 200:
        return response_data['data']
    else:
        raise Exception(f"上传附件失败: {response_data['msg']}")

# 创建WebSocket连接
def create_websocket_connection(session_id=None):
    """
    创建WebSocket连接

    Args:
        session_id (str): 会话ID，可选

    Raises:
        Exception: 创建连接失败的报错信息

    Returns:
        tuple: WebSocket对象和会话ID
    """
    ws_url = f"wss://api.tgkwai.com/api/v1/qamodel/session?x-token={ACCESS_TOKEN}"
    if session_id:
        ws_url += f"&session_id={session_id}"
    # 由于存在跨域限制，因此建立连接时不能携带Origin头
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    result = ws.recv()
    response_data = json.loads(result)
    if response_data['code'] == 200:
        return ws, response_data['data']
    else:
        raise Exception(f"创建WebSocket连接失败: {response_data['msg']}")

# 发送消息
def send_message(session_id, messages, stream=True):
    """
    发送消息到WebSocket连接

    Args:
        session_id (str): 会话ID
        messages (list): 消息列表
        stream (bool): 是否流式输出
    """
    ws, session_id = create_websocket_connection(session_id)
    payload = {
        "session_id": session_id,
        "messages": messages,
        "stream": stream
    }
    ws.send(json.dumps(payload))
    response_content = ""
    while True:
        result = ws.recv()
        response_data = json.loads(result)
        if response_data['data']['is_finished']:
            break
        print(response_data)
        response_content += response_data['data']['content']
    ws.close()
    print("大模型回复：", response_content)
    # 将服务器的回复添加到历史记录中
    messages.append({
        "role": "assistant",
        "type": "text",
        "content": response_content
    })
    return session_id

# 删除附件
def delete_attachment(file_path):
    """
    删除服务器上的附件

    Args:
        file_path (str): 附件路径

    Raises:
        Exception: 删除失败的报错信息
    """
    url = f"{BASE_URL}/api/v1/attachments/delete"
    headers = {
        'X-Token': f'Bearer {ACCESS_TOKEN}'
    }
    params = {
        'file_path': file_path
    }
    response = requests.delete(url, headers=headers, params=params)
    response_data = response.json()
    if response_data['code'] != 200:
        raise Exception(f"删除附件失败: {response_data['msg']}")

def test():
    try:
        # 上传附件
        file_path = 'D:\\Development\\tgkwai\\test_image.jpg'
        attachment_url = upload_attachment(file_path)
        print(f"附件上传成功: {attachment_url}")

        # 初始化会话ID和历史记录
        session_id = None
        history = []

        # 发送第一条消息
        messages = [
            {
                "role": "user",
                "type": "multimodal",
                "content": "这张图片里的作物得了什么疾病？",
                "attachments": [
                    { "type": "image", "url": attachment_url }
                ]
            }
        ]
        history.extend(messages)
        session_id = send_message(session_id, history)

        # 进行多轮对话
        additional_messages = [
            {
                "role": "user",
                "type": "text",
                "content": "上述病症主要感染作物有哪些？"
            },
            {
                "role": "user",
                "type": "text",
                "content": "该如何防治这种病害？"
            }
        ]
        for message in additional_messages:
            history.append(message)
            session_id = send_message(session_id, history)

        # 删除附件
        delete_attachment(attachment_url)
        print("附件删除成功")
        print("\n完整的对话历史：", json.dumps(history, ensure_ascii=False))
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    test()

if __name__ == '__main__':
    main()
