# PixVerse MCP 使用指南
<div align="left">
<a href="https://app.pixverse.ai" style="margin: 2px">
<img alt="Webapp" src="https://img.shields.io/badge/PixVerse-Web-3961F1?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
</a>
<a href="https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp" style="margin: 2px">
<img alt="API" src="https://img.shields.io/badge/PixVerse-API-3961F1?style=flat-square&labelColor=2C3E50" style="display: inline-block; vertical-align: middle;"/>
</a>
</div>

## 概述

PixVerse MCP 是一个允许您通过支持 Model Context Protocol (MCP) 的应用程序（如 Claude 或 Cursor）访问 PixVerse 最新视频生成模型的工具。通过这个集成，您可以随时随地生成高质量视频，包括文本到视频、图像到视频等多种转换方式。

[English Version](https://github.com/PixVerseAI/PixVerse-MCP/blob/main/README.md)

## 主要功能

* **文本生成视频**：使用文字提示生成创意视频
* **支持多种参数调整**：控制视频质量、长度、宽高比等
* **与AI助手协同创作**：结合Claude等大模型的创意能力

## 系统组件

该系统的主要组件：

1. **UVX MCP 服务器**：
   - 基于 Python 的云端服务器
   - 直接与 PixVerse API 通信
   - 提供完整的视频生成功能

## 安装与配置

### 前提条件

1. **Python 3.10 或更新版本**
2. **UV/UVX**
3. **PixVerse API 密钥**：从 [PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp) 获取 (API Credits 需要从[PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)购买)

### 获取依赖

1. **Python**：
   - 从 [Python 官网](https://www.python.org/downloads/) 下载并安装
   - 确保将 Python 添加到系统路径

2. **UV/UVX**
   - 通过下面方式下载UV / UVX
   - mac/linux
     ```
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   - Windows
     ```
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```

## 如何使用 MCP Server

### 1. 获取 PixVerse API 密钥

- 访问 [PixVerse Platform](https://platform.pixverse.ai/api-key?utm_source=github&utm_medium=readme&utm_campaign=mcp)
- 注册/登录您的账户
- 在个人设置中创建并复制您的 API 密钥
- 创建方法：[API密钥生成指南](https://docs.platform.pixverse.ai/how-to-get-api-key-882968m0)

### 2. 下载必要依赖

- **Python**：安装 Python 3.10 或更高版本
- **UV/UVX**：安装最新稳定版的 UV & UVX

### 3. 配置 MCP 客户端

- 打开您的 MCP 客户端（如 Claude for Desktop 或 Cursor）
- 找到客户端设置
- 找到并打开 `mcp_config.json` 文件（或相应的配置文件）
- 根据您选择的方式添加配置：

```json
{
  "mcpServers": {
    "PixVerse": {
      "command": "uvx",
      "args": [
        "pixverse-mcp"
      ],
      "env": {
        "PIXVERSE_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

- 将从platform.pixverse.ai 获取的API key 写到"PIXVERSE_API_KEY" :"xxxx" 上
- 保存配置文件

### 4. 重启 MCP 客户端或刷新 MCP 服务器

- 完全关闭并重新打开您的 MCP 客户端
- 或者，如果客户端支持，使用刷新 MCP 服务器选项

## 具体客户端配置

### Claude for Desktop 配置

1. 打开 Claude 应用
2. 转到 Claude > 设置 > 开发者 > 编辑配置
3. 打开 `claude_desktop_config.json` 文件
4. 添加上述配置并保存
5. 重启 Claude 应用
   - 如果连接成功, 首页不会提示任何error, 且mcp设置亮绿灯
   - 如果连接失败, 首页会提示连接失败

### Cursor 配置

1. 打开 Cursor 应用
2. 转到设置 > Model Context Protocol
3. 添加新服务器
4. 填写服务器详情（与上面 JSON 配置中的信息相同）
5. 保存并重启 or 刷新mcp server

## 使用方法

### 文生视频

通过 Claude 或 Cursor，您可以使用自然语言描述要生成的视频：

**基础示例**：

```
请生成一个关于海洋日落的视频，金色的阳光洒在海面上，波浪轻轻拍打着岸边。
```

**进阶示例（带参数）**：
```
请使用以下参数生成一个城市夜景视频：
内容：高楼大厦的灯光在夜幕中闪烁，街道上车流形成光线轨迹
宽高比：16:9
质量：540p
时长：5秒
运动模式：normal
负面提示词：模糊、抖动、文字
```

您可以指定以下参数：
* 宽高比（16:9, 4:3, 1:1, 3:4, 9:16）
* 时长（5秒或8秒）
* 质量（360p, 540p, 720p, 1080p）
* 运动模式（正常或快速）

### 脚本 + 视频

通过详细脚本指导，生成更有结构和故事性的视频内容。

**场景描述示例**：

```
请根据以下场景描述生成一段视频：
场景：清晨的海滩
太阳刚刚升起，金色的阳光洒在海面上，形成闪烁的光点。
沙滩上留下一串脚印，延伸到远处。
海浪轻轻拍打岸边，留下白色的泡沫，然后缓缓退去。
远处有一艘小船缓缓驶过平静的海面。
使用16:9的宽高比，质量选择540p，时长5秒。
```

**分镜脚本示例**：

可以把特别简单的分镜脚本放进去
```
请根据以下分镜脚本生成视频：
开始：俯视角度的咖啡杯，热气袅袅上升
特写：咖啡表面的涟漪和纹理
过渡：咖啡被搅动，形成漩涡
结束：杯子旁放着一本打开的书和一副眼镜
使用1:1的正方形格式，540p质量，使用fast运动模式增强液体效果。
```

也可以分镜图片脚本 (Claude Desktop 支持)
```
请根据上传的脚本, 帮我生成一段视频
```

### 一键视频

快速生成特定主题或风格的视频，无需复杂描述。

**主题示例**：

```
请生成一个未来科技主题的视频，包含霓虹灯效果和全息投影元素。
```

**风格示例**：

```
请生成一个水彩画风格的花朵绽放视频，色彩要明亮而梦幻。
```

### 创意 + 视频

结合AI的创意能力构思独特的视频概念。

**风格转换示例**：

```
这是一张城市建筑照片，请用复古风格重新诠释它，并提供相应的视频生成提示词。
```

**故事引导示例**：

```
如果这张街道照片是电影开场，接下来会发生什么？请提供视频创意。
```

**情绪创意示例**：

```
看一下这张森林小径照片，为我构思一个短视频创意，可以是一个微型故事或情绪变化的场景。
```

## 常见问题

**如何获取 PixVerse API 密钥？**
- 访问 [PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)，注册账户后在API-KEY 中生成 API 密钥。

**服务器不响应怎么办？**
1. 检查您的 API 密钥是否有效
2. 确认配置文件路径是否正确
3. 查看错误日志（通常在 Claude 或 Cursor 的日志文件夹中）

**如何获取积分呢？**
- 如尚未在 API 平台完成充值，请先前往充值。直达链接：[PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)

**现在支持图生视频、首尾帧功能吗?**
- 目前MCP方式不支持图生视频和首尾帧功能，您可以前往 [PixVerse Platform](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp) 或 [API文档](https://docs.platform.pixverse.ai) 通过API方式接入这些功能。

**支持哪些视频格式和尺寸？**
- PixVerse 支持多种视频分辨率（从 360p 到 1080p）和宽高比（从竖屏 9:16 到横屏 16:9）。
- 但我们建议先使用 540p、5 秒的视频进行效果测试。

**生成的视频在哪里？**
- 生成的视频会通过 URL 链接提供，您可以点击链接查看、下载或分享视频。

**视频生成需要多长时间？**
- 根据视频复杂度、服务器负载和网络状况，通常需要 30 秒到 2 分钟不等。

**如果遇到spawn uvx ENOENT 问题，怎么解决？**
- 此类问题主要是安装uvx/uv path导致，可以通过以下方式解决

Mac/Linux
```
sudo cp ./uvx /usr/local/bin
```

Windows
1. 首先了解安装的 uv/uvx 在哪个位置，在终端输入
   ```
   where uvx
   ```
2. 打开文件管理器，找到uvx/uv文件
3. 放到 C:\Program Files (x86) , C:\Program Files

## 社区与支持

### 社区支持

加入我们的社区，获取最新更新、分享您的创作、获取帮助或提供反馈：
- [Discord server](https://discord.gg/pixverse) : 加入我们的 Discord 服务器

### 技术支持

如果您遇到任何问题或需要帮助，请通过以下方式联系我们：
- 电子邮件: [api@pixverse.ai](mailto:api@pixverse.ai)
- 官方网站: [https://platform.pixverse.ai](https://platform.pixverse.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp)

## Release Notes (1.0.0)

- 通过MCP支持文生视频，获取视频链接
- 与Claude & Cursor结合创造更多玩法
- 支持Cloud Python MCP server
