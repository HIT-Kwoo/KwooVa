# API使用指南

## 基本调用步骤

1. 获取访问密钥。
2. 调用API获得模型回复。

## 获取访问密钥

1. 登录 https://www.tgkwai.com/ 获取 `access token`（形如 `sk-xxxx`），**Access Token 只展示一次，请妥善保存**。
2. 调用时使用Authorization Bearer Token方式（与OpenAI API鉴权方式一致）：
   - HTTP header: `Authorization: Bearer sk-xxxx`

## API Endpoint：

`https://api.tgkwai.com/api/v1/qamodel/chat/completions`或`https://api.tgkwai.com/api/v1/qamodel/v1/chat/completions`

两个接口能力一样，便于部分第三方应用接入

## 可选模型

模型名称**可以任意填写以下两个中的一个**，会自动识别并调用模型

1. 问答模型（不具备上传图片能力，具备联网检索和提供引用出处能力）：KwooLa
2. 多模态问答模型（具备上传图片能力，不具备联网检索和提供引用出处能力）：KwooVa

## API调用样例（Restful）

* 此api兼容openai api格式，**但并非所有openai api参数都支持**，[点击查看openai官方文档](https://platform.openai.com/docs/api-reference/chat/create)
* 此api已在[NextChat](https://github.com/ChatGPTNextWeb/NextChat)应用的自定义模型上测试通过，理论上兼容绝大部分的第三方应用和平台
* 如果此api的兼容性存在问题，请提出issue，我们将尽快修复

**请求方法**: POST

**请求路径**: ``https://api.tgkwai.com/api/v1/qamodel/chat/completions`或`https://api.tgkwai.com/api/v1/qamodel/v1/chat/completions``

**请求头**: `Authorization: Bearer sk-xxxx`

### Python SDK

```python
import openai

openai.api_key = "sk-xxxx"
openai.base_url = "https://api.tgkwai.com/api/v1/qamodel/"

model = "Qwen2-7b-q4km"

def test_chat_completion_stream(model):
    messages = [{"role": "user", "content": "番茄常见病虫害有哪些"}]
    res = openai.chat.completions.create(
        model=model, messages=messages, stream=True, temperature=0.5, max_tokens=4096
    )
    for chunk in res:
        try:
            # print(chunk)
            content = chunk.choices[0].delta.content
            if content is None:
                content = ""
        except Exception as e:
            content = chunk.choices[0].message.get("content", "")
        print(content, end="", flush=True)
    print()

# create a chat completion
completion = openai.chat.completions.create(
  model=model,
  messages=[{"role": "user", "content": "你能做什么"}]
)
# print the completion
print(completion.choices[0].message.content)

test_chat_completion_stream(model)

```

### Restful API

**请求示例**:

```json
// 问答模型，支持多轮问答和流式输出
{
    "model": "KwooLa", 
    "stream": true, // true表示使用SSE流式输出，false则不使用流式输出
    "messages": [ // 支持多轮问答
      {
        "role": "user",
        "content": "番茄有哪些常见病症"
      }
    ]
}

// 多模态模型，支持多轮问答和流式输出
{
    "model": "KwooVa",
    "stream": true, // true表示使用SSE流式输出，false则不使用流式输出
    "messages": [ // 支持多轮问答
      {
        "role": "user",
        "content":[
            {
                "type":"text",
                "text":"请描述一下这张图片"
            },
            {
                "type":"image_url",
                "image_url":{
                    "url":"data:image/jpeg;base64,/9j/4AA..." // 支持http/https链接或者base64 datauri格式
                }
            }
        ]
      }
    ]
}
```

**响应示例（非流式输出）**:

```json
{
    "id": "chatcmpl-23579425-8995-4594-b850-95983d27e231",
    "object": "chat.completion",
    "created": 1742490119,
    "model": "KwooLa",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "我能帮助您了解农业方面的知识、提供农业生产的建议、解答有关农作物、土壤管理、病虫害防治、灌溉和施肥等问题。如果您有具体的问题或需要某种农业技术的详细信息，请告诉我，我会尽力提供准确和相关的答案。"
            },
            "finish_reason": "stop"
        }
    ]
}
```

**响应示例（流式输出）**:

```json
data:{"id":"chatcmpl-2a75338b-5180-42c5-af15-a0ef15b7a6bc","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"我能","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-c07c0d95-0765-4251-8db3-f30f23769ca4","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"帮助","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-b73782ef-ef77-4085-9c47-3d7c9ba61344","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"您","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-8c29b147-4856-4a6d-9576-f632f62b3487","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"了解","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-07c3e990-e219-48be-8256-7910c016710f","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"农业","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-4348c10c-f6dc-4937-857e-8af14ef3bc0b","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"方面的","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-08d79583-a347-4067-8f64-e1b836222094","object":"chat.completion.chunk","created":1742490154,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"知识","role":"assistant"},"finish_reason":null}]}

...

data:{"id":"chatcmpl-90a36025-dbe7-4ed1-a92c-0c4a02931e3f","object":"chat.completion.chunk","created":1742490155,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"相关的","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-df4c468a-9d40-4464-9e55-398d9ca85855","object":"chat.completion.chunk","created":1742490155,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"解答","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-0af9830f-6a1c-4c41-a611-282dbe574a3b","object":"chat.completion.chunk","created":1742490155,"model":"KwooLa","choices":[{"index":0,"delta":{"content":"。","role":"assistant"},"finish_reason":null}]}

data:{"id":"chatcmpl-a54c3817-0547-4c3a-9ed0-9c534a19df0f","object":"chat.completion.chunk","created":1742490155,"model":"KwooLa","choices":[{"index":0,"delta":{"content":null,"role":"assistant"},"finish_reason":"stop"}]}

data:[DONE]
```

## 错误响应

- 401 - Incorrect API key provided
- 401 - invalid_request_error
- 500 - Internal Server Error

## FAQs

**Q1: 是否支持工具调用**

**A1:** 暂不支持工具调用，也无法使用相关的api

**Q2: 我在使用某第三方平台/应用时提示404**

**A2:** 请您检查一下填写的api endpoint（接口地址）是否正确，有的应用需要填写完整（包括`/chat/completions`）；有的会自动补全`/chat/completions`，您需要填写`https://api.tgkwai.com/api/v1/qamodel/`；有的应用会自动补全`/v1/chat/completions`（如NextChat），您需要填写`https://api.tgkwai.com/api/v1/qamodel/`。如果您在仔细阅读第三方应用文档后仍无法解决，请提出issue，我们将尽快与您联系。
