#!/bin/bash
# 性能分析工具 - 快速使用示例

echo "================================"
echo "性能分析工具使用示例"
echo "================================"
echo ""

# 示例1: 分析当前数据
echo "示例1: 分析 myproject 项目 0318 的数据"
echo "命令: python3 analyze_performance.py --project myproject --date 0318"
echo ""

# 示例2: 使用路径方式
echo "示例2: 使用路径方式分析"
echo "命令: python3 analyze_performance.py --path data/myproject/0318"
echo ""

# 示例3: 对比两个日期
echo "示例3: 对比优化前后（假设优化后数据在 0319）"
echo "命令: python3 analyze_performance.py --project myproject --date 0319 --baseline data/myproject/0318/baseline.json"
echo ""

# 示例4: 多项目
echo "示例4: 分析其他项目"
echo "命令: python3 analyze_performance.py --project another-project --date 0320"
echo ""

echo "================================"
echo "当前目录结构:"
echo "================================"
echo "catchpoint-export/"
echo "├── analyze_performance.py"
echo "├── README.md"
echo "└── data/"
echo "    └── myproject/"
echo "        └── 0318/"
echo "            ├── *.json (性能数据)"
echo "            ├── baseline.json (基线)"
echo "            └── report_*.txt (报告)"
echo ""

echo "================================"
echo "快速开始:"
echo "================================"
echo "1. 将新的JSON文件放到对应目录"
echo "   mkdir -p data/项目名/日期"
echo "   mv *.json data/项目名/日期/"
echo ""
echo "2. 运行分析"
echo "   python3 analyze_performance.py --project 项目名 --date 日期"
echo ""
echo "3. 优化后对比"
echo "   python3 analyze_performance.py --project 项目名 --date 新日期 --baseline data/项目名/旧日期/baseline.json"
echo ""
