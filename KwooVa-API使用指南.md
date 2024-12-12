# API 使用指南

## 基本调用步骤

1. 获取访问密钥。
2. （可选）上传附件以使用多模态能力。
3. 调用API获得模型回复。

## 获取访问密钥

1. 登录 https://www.tgkwai.com/ 获取 `access token`（形如 `sk-xxxx`），**Access Token 只展示一次，请妥善保存**。
2. 调用时在 HTTP header 或 WebSocket 参数中增加：
   - HTTP header: `X-Token: Bearer sk-xxxx`
   - WebSocket 参数: `?x-token=sk-xxxx`

## 附件上传

### 允许的附件类型

| 类型名 | 可用后缀名                                          | 最大大小 |
| ------ | --------------------------------------------------- | -------- |
| image  | "jpg", "jpeg", "png", "bmp", "webp"（不区分大小写） | 10MB     |

### 上传附件

**请求方法**: POST
**请求路径**: `/api/v1/attachments/upload`
**请求头**: `X-Token: Bearer sk-xxxxxx`
**请求参数（form）**:

- `type`: 上传的文件类型，目前仅可选 `image`

- `file`: 文件内容。

**请求示例**:

```bash
curl -X POST "https://api.tgkwai.com/api/v1/attachments/upload" \

-H "X-Token: Bearer sk-xxxxxx" \

-F "type=image" \

-F "file=@/path/to/your/image.jpg"
```

**响应参数**:

- `data`: 上传的文件在服务器上的路径，下载时前面补上 `https://static.tgkwai.com/uploads/`

**响应示例**:

```json
{

  "code": 200,

  "msg": "成功",

  "data": "38/image/f841828d-709f-4d85-b787-b2ca221233bd.png"

}
```

// 上传的图片的下载链接为 https://static.tgkwai.com/uploads/38/image/f841828d-709f-4d85-b787-b2ca221233bd.png

**错误信息**:

- 400 - 上传附件失败：<具体错误原因>

### 删除附件

**请求方法**: DELETE
**请求路径**: `/api/v1/attachments/delete`
**请求头**: `X-Token: Bearer sk-xxxx`

**请求参数（param）**:

- `file_path`: 从上传接口获取的附件路径

**请求示例**:

```bash
curl -X DELETE "https://api.tgkwai.com/api/v1/attachments/delete?file_path=38/image/f841828d-709f-4d85-b787-b2ca221233bd.png" \

-H "X-Token: Bearer sk-xxxxxx"
```

**响应示例**:

```json
{

  "code": 200,

  "msg": "成功",

  "data": null

}
```

**错误信息**:

- 403 - 无权删除附件
- 400 - 删除附件失败：<具体错误原因>

## WebSocket 连接

### 创建 WebSocket 连接

**请求方法**: WebSocket connect
**请求路径**: `/api/v1/qamodel/session`
**请求头**: `X-Token: Bearer sk-xxxx` 或 `?x-token=sk-xxxx`

**请求参数**:

- `session_id`（string）: 会话号，用来记录上下文，可以不带（新会话）

**请求示例**:

```bash
# 如果没有 session_id
wscat -c "wss://api.tgkwai.com/api/v1/qamodel/session?x-token=sk-xxxx"

# 如果有 session_id
wscat -c "wss://api.tgkwai.com/api/v1/qamodel/session?x-token=sk-xxxx&session_id=a8d10ffa-60ba-4af1-916e-6a918c0096e3"
```

**响应参数**:

- `data`: 会话号 `session_id`

**响应示例**:

```json
{

  "code": 200,

  "msg": "OK",

  "data": "a8d10ffa-60ba-4af1-916e-6a918c0096e3"

}
```

### 发送消息（含多模态能力）

**请求方法**: WebSocket send

**请求参数**:

- `session_id`（string）: 会话号
- messages（list）: 会话历史记录
  - `role`（string）: "user" 或 "assistant" 或 "system"
  - `content`（string）: 会话内容
  - `type`（string）: "text" 或 "multimodal"
  - `attachments`（dict）: 可选，`type` 目前只有 `image`，`url` 为附件上传接口的返回值
- `stream`（boolean）: 是否流式输出

**请求示例**:

```json
{

  "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

  "messages": [

    {

      "role": "user",

      "type": "multimodal",

      "content": "这张图片里的作物得了什么疾病？",

      "attachments": [

        { "type": "image", "url": "38/image/e72ebf89-f2e9-43d0-b584-5f30e2516ac1.jpg" }

      ]

    },

    {

      "role": "assistant",

      "type": "text",

      "content": "图片里的作物患有玉米大斑病。"

    },

    {

      "role": "user",

      "type": "text",

      "content": "上述病症主要感染作物有哪些"

    },

    {

      "role": "assistant",

      "type": "text",

      "content": "主要是玉米"

    },

    {

      "role": "user",

      "type": "multimodal",

      "content": "这张图片里的作物得的是上面说的病症吗？",

      "attachments": [
        { "type": "image", "url": "38/image/e72ebf89-f2e9-43d0-b584-5f30e2516ac1.jpg" }

      ]

    }

  ],

  "stream": true

}
```

**响应参数**:

- `session_id`（string）: 会话号
- `content`（string）: 流式输出的消息
- `title`（string）: 可选，第一轮问答时会给一个 `title`
- `is_finished`（bool）: 是否已经回答结束

**响应示例**:

```json
{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "你好！",

    "is_finished": false

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "我是",

    "is_finished": false

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "天工开悟",

    "is_finished": false

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "你好！",

    "is_finished": false

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "<BOS>[1] 唯农209 审定意见：<EOS>[2] 唯农209 审定意见：<EOS>[3] 唯农209 审定意见：<EOS>[4] 唯农209 审定意见：<EOS>[5] 唯农209 审定意见：",

    "is_finished": false

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "content": "[DONE]",

    "is_finished": true

  }

}

{

  "code": 200,

  "msg": "成功",

  "data": {

    "session_id": "a8d10ffa-60ba-4af1-916e-6a918c0096e3",

    "title": "问候",

    "is_finished": true

  }

}
```
*注：在请求多轮对话时，**每次发送消息要建立ws连接，服务端流式输出完毕后就会自动断开连接**。 


### 错误响应

- 400 - `session_id` 不能为空
- 400 - `session_id` 不匹配
- 500 - 问答模型发送消息失败

## FAQs

**Q1: 在多轮对话时，模型会遗忘之前的上下文信息。**

**A1:** 这可能是由于您在发送请求时，`message` 中缺少了之前会话的消息。在进行多轮对话时，请将历史请求和模型之前的回复一并拼接到 `message` 中，以确保上下文信息的完整性。

**Q2: 使用 Python 的 websocket 库进行访问时，无法建立连接。**

**A2:** 在使用 websocket 库建立连接时，默认会发送一个不受信任的 `Origin` 报头，导致服务器拒绝该访问请求。您可以通过禁用 `Origin` 头来解决此问题，示例如下：

```python
ws = websocket.create_connection(f"wss://api.tgkwai.com/api/v1/qamodel/session?x-token={ACCESS_TOKEN}", suppress_origin=True)
```

