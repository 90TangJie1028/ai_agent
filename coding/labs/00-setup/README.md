# Lab-00：环境与工具链

验证虚拟环境、依赖、`.env` 加载正常。

## 运行

```powershell
pytest tests/
```

## 验收

- [x] `test_imports.py` 通过
- [x] `test_dotenv.py` 通过（无 key 时 skip）