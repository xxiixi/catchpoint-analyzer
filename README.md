# Catchpoint Analyzer

## 项目简介

一个用于分析和对比网站性能数据的工具，用于对比 Catchpoint 导出的性能测试数据。

**主要功能：**
- 解析 Catchpoint 导出的 JSON 格式性能数据
- 生成易读的性能分析报告，包含核心 Web 指标（Core Web Vitals）
- 支持多地区性能对比
- 支持优化前后的性能对比
- 自动评级和优化建议
- 支持多项目和多时间点的数据管理

**适用场景：**
- 网站性能基线测试
- 性能优化效果验证
- 多地区性能监控
- 持续性能追踪

**数据来源：**
所有 JSON 数据文件需要从 [Catchpoint](https://www.catchpoint.com/) 平台导出。Catchpoint 是一个专业的网站性能监控平台，可以从全球多个节点测试网站性能。

## 目录结构

```
catchpoint-export/
├── analyze_performance.py    # 主分析脚本
├── README.md                  # 使用说明
├── examples.sh                # 使用示例
├── .gitignore                 # Git忽略配置
└── data/                      # 数据目录（已忽略）
    └── [项目名]/
        └── [日期]/
            ├── *.json         # 性能数据文件
            ├── baseline.json  # 基线数据
            └── report_*.txt   # 生成的报告
```

**示例：**
```
catchpoint-export/
├── analyze_performance.py
├── README.md
└── data/
    ├── myproject/
    │   ├── 0318/
    │   │   ├── myproject-0318-USA.json
    │   │   ├── myproject-0318-Japan.json
    │   │   ├── baseline.json
    │   │   └── report_20260318_104825.txt
    │   └── 0319/
    │       ├── myproject-0319-USA.json
    │       └── ...
    └── another-project/
        └── 0320/
            └── ...
```

## 快速开始

### 0. 准备数据

**从 Catchpoint 导出性能数据：**

1. 登录 Catchpoint 平台
2. 选择你的性能测试
3. 导出测试结果为 JSON 格式
4. 将导出的 JSON 文件放到 `data/项目名/日期/` 目录

```bash
# 创建目录
mkdir -p data/myproject/0318

# 移动 Catchpoint 导出的 JSON 文件
mv *.json data/myproject/0318/
```

### 1. 分析当前性能数据

```bash
# 方式1: 使用项目名和日期
python3 analyze_performance.py --project myproject --date 0318

# 方式2: 直接指定路径
python3 analyze_performance.py --path data/myproject/0318
```

这会：
- 加载指定目录下的所有JSON文件
- 生成详细的性能分析报告
- 保存基线数据到 `baseline.json`
- 保存报告到 `report_[时间].txt`

### 2. 优化后对比性能

```bash
# 优化网站后，导出新数据到新目录（例如 data/myproject/0319）
# 然后运行对比

python3 analyze_performance.py \
  --project myproject \
  --date 0319 \
  --baseline data/myproject/0318/baseline.json
```

这会显示每个指标的改善/恶化情况和百分比变化。

### 3. 自定义输出文件名

```bash
python3 analyze_performance.py \
  --path data/myproject/0318 \
  --output my_custom_report.txt
```

## 命令行参数

| 参数 | 简写 | 说明 | 示例 |
|------|------|------|------|
| `--project` | `-p` | 项目名称 | `--project myproject` |
| `--date` | `-d` | 日期 | `--date 0318` |
| `--path` | | 直接指定数据目录 | `--path data/myproject/0318` |
| `--baseline` | `-b` | 基线文件路径（用于对比） | `--baseline data/myproject/0318/baseline.json` |
| `--output` | `-o` | 输出报告文件名 | `--output report.txt` |

**注意：** 使用 `--project` 和 `--date` 时，会自动在 `data/` 目录下查找。

## 使用场景

### 场景1: 首次分析

```bash
# 1. 将Catchpoint导出的JSON文件放到 data/项目名/日期/ 目录
mkdir -p data/myproject/0318
mv *.json data/myproject/0318/

# 2. 运行分析
python3 analyze_performance.py --project myproject --date 0318
```

### 场景2: 优化后对比

```bash
# 1. 优化网站...

# 2. 导出新数据到新目录
mkdir -p data/myproject/0319
mv *.json data/myproject/0319/

# 3. 对比性能
python3 analyze_performance.py \
  --project myproject \
  --date 0319 \
  --baseline data/myproject/0318/baseline.json
```

### 场景3: 多项目管理

```bash
# 项目A
python3 analyze_performance.py --project projectA --date 0318

# 项目B
python3 analyze_performance.py --project projectB --date 0318

# 对比项目A的两个版本
python3 analyze_performance.py \
  --project projectA \
  --date 0320 \
  --baseline data/projectA/0318/baseline.json
```

### 场景4: 持续监控

```bash
# 每周测试
python3 analyze_performance.py --project myproject --date 0318
python3 analyze_performance.py --project myproject --date 0325 --baseline data/myproject/0318/baseline.json
python3 analyze_performance.py --project myproject --date 0401 --baseline data/myproject/0325/baseline.json
```

## Catchpoint JSON 数据结构

工具会从 Catchpoint 导出的 JSON 文件中提取以下关键字段：

### 核心性能指标字段

| JSON 字段路径 | 指标名称 | 说明 | 评级标准 |
|--------------|---------|------|---------|
| `data.runs.1.firstView.steps[0].LargestContentfulPaint` | LCP | 最大内容绘制时间（ms） | 优秀 ≤ 2500ms |
| `data.runs.1.firstView.steps[0].firstContentfulPaint` | FCP | 首次内容绘制时间（ms） | 优秀 ≤ 1800ms |
| `data.runs.1.firstView.steps[0].CumulativeLayoutShift` | CLS | 累积布局偏移 | 优秀 ≤ 0.1 |
| `data.runs.1.firstView.steps[0].TotalBlockingTime` | TBT | 总阻塞时间（ms） | 优秀 ≤ 200ms |
| `data.runs.1.firstView.steps[0].TTFB` | TTFB | 首字节时间（ms） | 优秀 ≤ 800ms |
| `data.runs.1.firstView.steps[0].SpeedIndex` | SI | 速度指数（ms） | 优秀 ≤ 3400ms |
| `data.runs.1.firstView.steps[0].render` | Render | 首次渲染时间（ms） | - |
| `data.runs.1.firstView.steps[0].fullyLoaded` | Fully Loaded | 完全加载时间（ms） | - |

### 资源统计字段

| JSON 字段路径 | 指标名称 | 说明 |
|--------------|---------|------|
| `data.runs.1.firstView.steps[0].bytesIn` | 下载大小 | 总下载字节数 |
| `data.runs.1.firstView.steps[0].bytesOut` | 上传大小 | 总上传字节数 |
| `data.runs.1.firstView.steps[0].requests` | 请求数量 | HTTP 请求总数（数组长度） |
| `data.latency` | 网络延迟 | 网络延迟（ms） |

### 测试信息字段

| JSON 字段路径 | 说明 |
|--------------|------|
| `data.testUrl` | 测试的网站URL |
| `data.browser.name` | 浏览器名称 |
| `data.browser.version` | 浏览器版本 |
| `data.testRuns` | 测试运行次数 |

**示例 JSON 结构：**
```json
{
  "data": {
    "testUrl": "https://example.com",
    "latency": 28,
    "browser": {
      "name": "Chrome",
      "version": "143.0.0.0"
    },
    "runs": {
      "1": {
        "firstView": {
          "steps": [{
            "LargestContentfulPaint": 2700,
            "firstContentfulPaint": 1003,
            "CumulativeLayoutShift": 0.0019,
            "TotalBlockingTime": 176,
            "TTFB": 390,
            "SpeedIndex": 2697,
            "render": 1000,
            "fullyLoaded": 29914,
            "bytesIn": 16878220,
            "bytesOut": 230416,
            "requests": [...]
          }]
        }
      }
    }
  }
}
```


## 性能评级标准

本工具使用 Google Web Vitals 和行业标准进行性能评级。

### Core Web Vitals（核心指标）

| 指标 | 说明 | 优秀 | 需改进 | 差 | 参考标准 |
|------|------|------|--------|-----|---------|
| **LCP**<br>最大内容绘制 | 衡量页面主要内容加载速度 | ≤ 2.5s | 2.5s - 4s | > 4s | [Google Web Vitals](https://web.dev/lcp/) |
| **FCP**<br>首次内容绘制 | 衡量首次显示内容的时间 | ≤ 1.8s | 1.8s - 3s | > 3s | [Google Lighthouse](https://web.dev/fcp/) |
| **CLS**<br>累积布局偏移 | 衡量视觉稳定性 | ≤ 0.1 | 0.1 - 0.25 | > 0.25 | [Google Web Vitals](https://web.dev/cls/) |
| **TBT**<br>总阻塞时间 | 衡量页面交互响应性 | ≤ 200ms | 200ms - 600ms | > 600ms | [Google Lighthouse](https://web.dev/tbt/) |

### 其他重要指标

| 指标 | 说明 | 优秀 | 需改进 | 差 | 参考标准 |
|------|------|------|--------|-----|---------|
| **TTFB**<br>首字节时间 | 衡量服务器响应速度 | ≤ 800ms | 800ms - 1.8s | > 1.8s | Google PageSpeed Insights |
| **Speed Index**<br>速度指数 | 衡量页面内容填充速度 | ≤ 3.4s | 3.4s - 5.8s | > 5.8s | [Google Lighthouse](https://web.dev/speed-index/) |
| **Fully Loaded**<br>完全加载时间 | 所有资源加载完成的时间 | - | - | - | - |

**注：** 这些标准被 Google 搜索排名、Chrome DevTools、Lighthouse 等广泛采用。


