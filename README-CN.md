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

PixVerse MCP 是一个允许您通过支持 Model Context Protocol (MCP) 的应用程序（如 Claude 或 Cursor）访问 PixVerse 最新的视频生成模型。从文本生成视频、动画图片、创建过渡、添加唇形同步、音效等等！

[English Version](https://github.com/PixVerseAI/PixVerse-MCP/blob/main/README.md)

## 主要功能

- **文本转视频**：使用文本提示生成创意视频
- **图片转视频**：将静态图片转换为动态视频
- **视频扩展**：无缝扩展现有视频以创建更长的序列
- **首尾帧**：在不同图片之间创建平滑变形
- **唇形同步**：为说话人头像视频添加逼真的唇形同步（支持TTS或自定义音频）
- **音效生成**：基于视频内容生成情境音效
- **多主体**：将多个主体合成到一个场景中
- **资源管理**：从本地文件或URL上传图片和视频
- **与AI助手协同创作**：与Claude等AI模型协作增强您的创意工作流程

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

## 功能使用指南

### 文本转视频
```
生成一个日落海景视频，金色阳光反射在水面上
```
**参数示例**：
```
提示词: "雄鹰在日出时翱翔于山峰之上"
质量: 720p
时长: 5秒
模型: v5
宽高比: 16:9
```

### 图片转视频
```
1. 上传图片 → 获得img_id
2. 使用img_id生成动画视频
```
**参数示例**：
```
提示词: "角色走过充满发光树木的魔法森林"
img_id: 12345
质量: 720p
时长: 5秒
模型: v5
```

### 视频扩展
```
使用source_video_id扩展现有视频
```
**参数示例**：
```
提示词: "场景继续，角色发现了一个隐藏的洞穴"
source_video_id: 67890
时长: 5秒
质量: 720p
模型: v5
```

### 场景过渡
```
上传两张图片，创建平滑变形动画
```
**参数示例**：
```
提示词: "从阳光海滩转变为暴风雨夜空"
first_frame_img: 11111
last_frame_img: 22222
时长: 5秒
质量: 720p
模型: v5
```

### 唇形同步
```
视频: 
TTS: 选择说话人 + 输入文本
音频: 上传音频文件 + 视频
```
**参数示例**：
```
# 方法1: 生成视频 + TTS
source_video_id: 33333
lip_sync_tts_speaker_id: "speaker_001"
lip_sync_tts_content: "欢迎来到我们的精彩视频教程"

# 方法2: 生成视频 + 自定义音频
source_video_id: 33333
audio_media_id: 44444

# 方法3: 上传视频 + TTS
video_media_id: 55555  # 先上传您的视频
lip_sync_tts_speaker_id: "speaker_002"
lip_sync_tts_content: "这是自定义旁白"

# 方法4: 上传视频 + 自定义音频
video_media_id: 55555  # 先上传您的视频
audio_media_id: 44444  # 先上传您的音频
```

### 音效生成
```
描述音效: "海浪声、海鸥叫声、轻柔的风声"
```
**参数示例**：
```
# 方法1: 生成视频 + 音效
sound_effect_content: "轻柔的海浪声、海鸥叫声、柔和的风声"
source_video_id: 55555
original_sound_switch: true  # 保留原音频

# 方法2: 上传视频 + 音效
sound_effect_content: "城市交通声、脚步声、城市氛围"
video_media_id: 66666  # 先上传您的视频
original_sound_switch: false  # 替换原音频

# 方法3: 完全替换音频
sound_effect_content: "史诗管弦乐、雷声、戏剧性紧张感"
video_media_id: 77777  # 先上传您的视频
original_sound_switch: false  # 用新音频替换
```

### 融合视频
```
上传多个图片，使用@ref_name引用
例如: @人物 站在 @城市 前，@无人机 在背景中飞行
```
**参数示例**：
```
提示词: "@英雄 站在@城市 前，@无人机 在头顶飞行"
image_references: [
  {type: "subject", img_id: 66666, ref_name: "英雄"},
  {type: "background", img_id: 77777, ref_name: "城市"},
  {type: "subject", img_id: 88888, ref_name: "无人机"}
]
时长: 5秒
模型: v4.5
质量: 720p
宽高比: 16:9
```

### 状态监控
```
每6秒检查一次video_id状态，直到完成
```
**参数示例**：
```
video_id: 99999
# 每6秒检查一次，直到状态变为"completed"或"failed"
# 典型生成时间: 60-120秒
```
**状态**: pending → in_progress → completed/failed



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

## Release Notes 
v2.0.0 (最新)
- **新增**: 图片转视频
- **新增**: 视频扩展和首尾帧
- **新增**: 唇形同步和音效生成
- **新增**: 融合视频和资源上传
- **新增**: 实时状态监控
- **改进**: 增强错误处理和并行生成

v1.0.0
- 通过MCP支持文生视频，获取视频链接
- 与Claude & Cursor结合创造更多玩法
- 支持Cloud Python MCP server
