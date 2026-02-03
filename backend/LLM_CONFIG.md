# LLM 服务配置说明

## 快速开始

### 1. 配置 Django settings.py

在您的 `backend/dvadmin/settings.py` 中添加以下配置：

```python
# LLM 服务配置
USE_LLM_FOR_PPT = True  # 是否使用大模型生成PPT（True=使用大模型，False=使用规则生成）

# LM Studio 配置（默认）
LLM_BASE_URL = "http://localhost:1234/v1"
LLM_API_KEY = "not-needed"
LLM_MODEL = "qwen2.5-7b-instruct:2"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2000
LLM_TIMEOUT = 30
```

### 2. 启动 LM Studio

1. 安装 LM Studio（如果还没有）
2. 启动 LM Studio 应用
3. 加载一个模型（如 qwen2.5-7b-instruct）
4. 启动服务器（确保端口是 1234）

### 3. 测试连接

```bash
cd backend
python -m dvadmin.utils.llm_service
```

如果看到 "LLM 服务连接成功"，说明配置正确。

## 配置选项说明

| 参数 | 说明 | 默认值 | 建议 |
|------|------|--------|------|
| `USE_LLM_FOR_PPT` | 是否启用大模型 | `False` | 测试通过后改为 `True` |
| `LLM_BASE_URL` | API 地址 | `http://localhost:1234/v1` | 根据您的服务调整 |
| `LLM_API_KEY` | API 密钥 | `not-needed` | LM Studio不需要，其他服务可能需要 |
| `LLM_MODEL` | 模型名称 | `qwen2.5-7b-instruct:2` | 根据加载的模型调整 |
| `LLM_TEMPERATURE` | 温度参数 | `0.7` | 0.0-1.0，越低越确定 |
| `LLM_MAX_TOKENS` | 最大令牌数 | `2000` | 根据需求调整 |
| `LLM_TIMEOUT` | 超时时间（秒） | `30` | 根据网络情况调整 |

## 兼容的其他服务

这个服务也支持其他兼容 OpenAI API 的服务：

### OpenAI
```python
LLM_BASE_URL = "https://api.openai.com/v1"
LLM_API_KEY = "your-api-key"
LLM_MODEL = "gpt-3.5-turbo"
```

### Azure OpenAI
```python
LLM_BASE_URL = "https://your-resource.openai.azure.com/v1"
LLM_API_KEY = "your-api-key"
LLM_MODEL = "gpt-35-turbo"
```

### 其他兼容服务
任何提供 `/v1/chat/completions` 接口的服务都可以使用。

## 使用方式

### 在代码中调用

```python
from dvadmin.utils.llm_service import call_llm

# 简单调用
response = call_llm("请生成一个PPT大纲")

# 带系统提示词
system_prompt = "你是一个专业的PPT生成助手，擅长将文本内容转化为结构化的PPT大纲。"
response = call_llm("请分析以下文本...", system_prompt=system_prompt)
```

### 检查服务可用性

```python
from dvadmin.utils.llm_service import is_llm_available

if is_llm_available():
    print("LLM服务可用")
else:
    print("LLM服务不可用")
```

## 在 genppt.py 中的使用

`genppt.py` 已经配置了自动调用 `call_llm` 函数：

1. 当 `USE_LLM_FOR_PPT = True` 时，自动使用大模型生成内容
2. 当大模型不可用时，自动降级到规则生成
3. 完善的错误处理和日志记录

## 调试建议

### 查看日志

在 Django settings.py 中配置日志：

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'dvadmin.utils.llm_service': {
            'handlers': ['console'],
            'level': 'DEBUG',  # 开发环境使用 DEBUG，生产环境使用 INFO
            'propagate': False,
        },
    },
}
```

### 常见问题

1. **连接失败**
   - 检查 LM Studio 是否启动
   - 检查端口是否正确（默认 1234）
   - 检查防火墙设置

2. **超时**
   - 增加 `LLM_TIMEOUT` 值
   - 检查模型是否已加载

3. **返回格式错误**
   - 查看日志中的原始响应
   - 调整 `LLM_TEMPERATURE` 值
   - 确保使用支持 JSON 生成的模型

4. **内存不足**
   - 使用更小的模型
   - 减少 `LLM_MAX_TOKENS` 值

## 性能优化

1. **使用更小的模型**：7B 模型比 14B 模型快 2-3 倍
2. **减少 max_tokens**：根据实际需求设置合理的最大令牌数
3. **启用缓存**：考虑对相似请求进行缓存
4. **批量处理**：如果需要生成多个 PPT，考虑并行处理

## 安全建议

1. 不要在生产环境中暴露 `LLM_BASE_URL` 和 `LLM_API_KEY`
2. 使用环境变量存储敏感配置：
   ```python
   import os
   LLM_API_KEY = os.environ.get('LLM_API_KEY', 'not-needed')
   ```
3. 限制 API 访问频率，防止滥用
4. 记录所有 API 调用，便于审计

## 升级建议

1. 首次使用建议设置 `USE_LLM_FOR_PPT = False`，使用规则生成测试
2. 确认规则生成正常后，改为 `True` 测试大模型生成
3. 在测试环境中充分测试后再部署到生产环境
4. 监控 API 调用成本和性能指标
