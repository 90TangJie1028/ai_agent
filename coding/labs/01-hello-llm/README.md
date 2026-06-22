# Lab-01：Hello LLM（DeepSeek）

最小 API 调用，理解 messages / model / usage。国内环境默认使用 **DeepSeek**。

## 运行

```powershell
# 需配置仓库根目录 .env 中 DEEPSEEK_API_KEY
python main.py
```

## 验收

- [x] 打印模型回复
- [x] 打印 prompt/completion tokens（如有）

## 说明

各厂商 Chat Completions 接口原理相近；后续有时间可同样方式接入 OpenAI。