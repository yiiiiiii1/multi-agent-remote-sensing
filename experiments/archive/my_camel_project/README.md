# My First CAMEL Agent

这是一个基于 CAMEL `ChatAgent` 的最小可运行示例，对应官方的 “Create Your First Agent” 教程。

## 1. 安装依赖

在仓库根目录执行：

```bash
python3 -m pip install -r my_camel_project/requirements.txt
```

## 2. 配置模型

复制环境变量模板：

```bash
cp my_camel_project/.env.example my_camel_project/.env
```

然后在 `my_camel_project/.env` 中填写：

```dotenv
OPENAI_API_KEY=你的_API_key
OPENAI_API_BASE_URL=https://你的服务地址/v1
CAMEL_MODEL_TYPE=你的模型名称
```

`OPENAI_API_BASE_URL` 是可选的。不填写时，模型客户端会使用默认地址。对于 OpenAI 兼容服务，模型名称必须与服务商实际提供的名称一致。

## 3. 运行

从仓库根目录运行一次提问：

```bash
python3 -m my_camel_project.main "用三句话解释什么是多智能体系统"
```

不带问题时进入交互模式：

```bash
python3 -m my_camel_project.main
```

输入 `/exit` 或 `/quit` 退出。
