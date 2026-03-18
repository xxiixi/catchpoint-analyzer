#!/usr/bin/env python3
"""
性能数据分析工具 - 支持多项目多日期
用于解析Catchpoint导出的性能数据并生成可读报告
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


class PerformanceAnalyzer:
    """性能数据分析器"""
    
    def __init__(self, data_dir: str = "."):
        self.data_dir = Path(data_dir)
        self.regions = []
        self.performance_data = {}
        
    def load_data(self):
        """加载所有JSON文件"""
        json_files = list(self.data_dir.glob("*.json"))
        
        if not json_files:
            print(f"✗ 在 {self.data_dir} 目录下未找到JSON文件")
            return False
        
        for file_path in json_files:
            # 跳过baseline和report文件
            if file_path.stem in ['baseline', 'comparison'] or 'report' in file_path.stem:
                continue
            
            # 从文件名提取地区名（支持多种命名格式）
            filename = file_path.stem
            parts = filename.split('-')
            region_name = parts[-1] if len(parts) > 0 else filename
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.regions.append(region_name)
                    self.performance_data[region_name] = self._extract_metrics(data)
                    print(f"✓ 已加载: {region_name}")
            except Exception as e:
                print(f"✗ 加载失败 {file_path.name}: {e}")
        
        return len(self.regions) > 0
    
    def _extract_metrics(self, data: Dict) -> Dict:
        """提取关键性能指标"""
        try:
            test_data = data.get('data', {})
            medians = test_data.get('medians', {})
            
            # 获取第一次运行的详细数据
            runs = test_data.get('runs', {})
            first_run = runs.get('1', {}).get('firstView', {}).get('steps', [{}])[0]
            
            metrics = {
                # 核心Web指标 (Core Web Vitals)
                'LCP': first_run.get('LargestContentfulPaint', 0),
                'FCP': first_run.get('firstContentfulPaint', 0),
                'CLS': first_run.get('CumulativeLayoutShift', 0),
                'TBT': first_run.get('TotalBlockingTime', 0),
                
                # 其他重要指标
                'TTFB': first_run.get('TTFB', 0),
                'SI': first_run.get('SpeedIndex', 0),
                'render': first_run.get('render', 0),
                'fullyLoaded': first_run.get('fullyLoaded', 0),
                
                # 资源统计
                'bytesIn': first_run.get('bytesIn', 0),
                'bytesOut': first_run.get('bytesOut', 0),
                'requests': len(first_run.get('requests', [])),
                
                # 网络
                'latency': test_data.get('latency', 0),
                'testUrl': test_data.get('testUrl', ''),
                'browser': test_data.get('browser', {}).get('name', ''),
            }
            
            return metrics
        except Exception as e:
            print(f"提取指标时出错: {e}")
            return {}
    
    def _format_bytes(self, bytes_val: int) -> str:
        """格式化字节数"""
        if bytes_val < 1024:
            return f"{bytes_val} B"
        elif bytes_val < 1024 * 1024:
            return f"{bytes_val / 1024:.2f} KB"
        else:
            return f"{bytes_val / (1024 * 1024):.2f} MB"
    
    def _get_performance_rating(self, metric: str, value: float) -> str:
        """获取性能评级"""
        ratings = {
            'LCP': [(2500, '优秀'), (4000, '需改进'), (float('inf'), '差')],
            'FCP': [(1800, '优秀'), (3000, '需改进'), (float('inf'), '差')],
            'CLS': [(0.1, '优秀'), (0.25, '需改进'), (float('inf'), '差')],
            'TBT': [(200, '优秀'), (600, '需改进'), (float('inf'), '差')],
            'TTFB': [(800, '优秀'), (1800, '需改进'), (float('inf'), '差')],
            'SI': [(3400, '优秀'), (5800, '需改进'), (float('inf'), '差')],
        }
        
        if metric not in ratings:
            return ''
        
        for threshold, rating in ratings[metric]:
            if value <= threshold:
                return rating
        return ''
    
    def generate_report(self) -> str:
        """生成性能分析报告"""
        report = []
        report.append("=" * 80)
        report.append("网站性能分析报告")
        report.append("=" * 80)
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据目录: {self.data_dir}")
        report.append(f"测试地区数量: {len(self.regions)}")
        
        if self.performance_data:
            test_url = list(self.performance_data.values())[0].get('testUrl', 'N/A')
            report.append(f"测试URL: {test_url}")
        
        report.append("")
        
        # 按地区展示详细数据
        for region in sorted(self.regions):
            metrics = self.performance_data[region]
            report.append("-" * 80)
            report.append(f"地区: {region}")
            report.append("-" * 80)
            
            report.append("\n【核心Web指标 (Core Web Vitals)】")
            report.append(f"  LCP (最大内容绘制):     {metrics['LCP']:>6} ms  [{self._get_performance_rating('LCP', metrics['LCP'])}]")
            report.append(f"  FCP (首次内容绘制):     {metrics['FCP']:>6} ms  [{self._get_performance_rating('FCP', metrics['FCP'])}]")
            report.append(f"  CLS (累积布局偏移):     {metrics['CLS']:>6.4f}     [{self._get_performance_rating('CLS', metrics['CLS'])}]")
            report.append(f"  TBT (总阻塞时间):       {metrics['TBT']:>6} ms  [{self._get_performance_rating('TBT', metrics['TBT'])}]")
            
            report.append("\n【加载性能指标】")
            report.append(f"  TTFB (首字节时间):      {metrics['TTFB']:>6} ms  [{self._get_performance_rating('TTFB', metrics['TTFB'])}]")
            report.append(f"  Speed Index (速度指数): {metrics['SI']:>6} ms  [{self._get_performance_rating('SI', metrics['SI'])}]")
            report.append(f"  首次渲染:               {metrics['render']:>6} ms")
            report.append(f"  完全加载:               {metrics['fullyLoaded']:>6} ms")
            
            report.append("\n【资源统计】")
            report.append(f"  下载大小:               {self._format_bytes(metrics['bytesIn']):>12}")
            report.append(f"  上传大小:               {self._format_bytes(metrics['bytesOut']):>12}")
            report.append(f"  请求数量:               {metrics['requests']:>6} 个")
            report.append(f"  网络延迟:               {metrics['latency']:>6} ms")
            
            report.append("")
        
        # 生成对比总结
        report.append("=" * 80)
        report.append("地区性能对比总结")
        report.append("=" * 80)
        
        key_metrics = ['LCP', 'FCP', 'TTFB', 'SI', 'fullyLoaded']
        
        for metric in key_metrics:
            report.append(f"\n{metric}:")
            sorted_regions = sorted(self.regions, 
                                   key=lambda r: self.performance_data[r][metric])
            
            for i, region in enumerate(sorted_regions, 1):
                value = self.performance_data[region][metric]
                rating = self._get_performance_rating(metric, value)
                rating_str = f" [{rating}]" if rating else ""
                report.append(f"  {i}. {region:15} {value:>8.2f} ms{rating_str}")
        
        report.append("\n" + "=" * 80)
        report.append("性能评级说明")
        report.append("=" * 80)
        report.append("LCP:  优秀 ≤ 2.5s  |  需改进 ≤ 4s  |  差 > 4s")
        report.append("FCP:  优秀 ≤ 1.8s  |  需改进 ≤ 3s  |  差 > 3s")
        report.append("CLS:  优秀 ≤ 0.1   |  需改进 ≤ 0.25 |  差 > 0.25")
        report.append("TBT:  优秀 ≤ 200ms |  需改进 ≤ 600ms|  差 > 600ms")
        report.append("TTFB: 优秀 ≤ 800ms |  需改进 ≤ 1.8s |  差 > 1.8s")
        report.append("SI:   优秀 ≤ 3.4s  |  需改进 ≤ 5.8s |  差 > 5.8s")
        
        return "\n".join(report)
    
    def save_baseline(self, filename=None):
        """保存基线数据用于后续对比"""
        if filename is None:
            filename = self.data_dir / "baseline.json"
        else:
            filename = Path(filename)
        
        baseline = {
            'timestamp': datetime.now().isoformat(),
            'data_dir': str(self.data_dir),
            'regions': self.regions,
            'metrics': self.performance_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(baseline, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 基线数据已保存到: {filename}")
        return filename
    
    def compare_with_baseline(self, baseline_file: str):
        """与基线数据对比"""
        baseline_path = Path(baseline_file)
        
        if not baseline_path.exists():
            print(f"✗ 未找到基线文件: {baseline_file}")
            return ""
        
        with open(baseline_path, 'r', encoding='utf-8') as f:
            baseline = json.load(f)
        
        report = []
        report.append("=" * 80)
        report.append("性能优化对比报告")
        report.append("=" * 80)
        report.append(f"基线时间: {baseline['timestamp']}")
        report.append(f"基线目录: {baseline.get('data_dir', 'N/A')}")
        report.append(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"当前目录: {self.data_dir}")
        report.append("")
        
        for region in self.regions:
            if region not in baseline['metrics']:
                continue
            
            report.append("-" * 80)
            report.append(f"地区: {region}")
            report.append("-" * 80)
            
            current = self.performance_data[region]
            old = baseline['metrics'][region]
            
            metrics_to_compare = [
                ('LCP', '最大内容绘制'),
                ('FCP', '首次内容绘制'),
                ('TTFB', '首字节时间'),
                ('TBT', '总阻塞时间'),
                ('SI', '速度指数'),
                ('fullyLoaded', '完全加载'),
            ]
            
            for metric_key, metric_name in metrics_to_compare:
                old_val = old.get(metric_key, 0)
                new_val = current.get(metric_key, 0)
                diff = new_val - old_val
                diff_pct = (diff / old_val * 100) if old_val > 0 else 0
                
                if diff < 0:
                    status = "✓ 改善"
                    symbol = "↓"
                elif diff > 0:
                    status = "✗ 变差"
                    symbol = "↑"
                else:
                    status = "→ 无变化"
                    symbol = "="
                
                report.append(f"  {metric_name:12} {old_val:>8.2f} → {new_val:>8.2f} ms  "
                            f"{symbol} {abs(diff):>7.2f} ms ({diff_pct:>+6.1f}%)  {status}")
            
            report.append("")
        
        return "\n".join(report)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='分析Catchpoint性能数据',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 分析指定项目和日期的数据
  python3 analyze_performance.py --project 2077 --date 0318
  
  # 使用自定义路径
  python3 analyze_performance.py --path 2077/0318
  
  # 对比两个日期的数据
  python3 analyze_performance.py --project 2077 --date 0319 --baseline 2077/0318/baseline.json
        """
    )
    
    parser.add_argument('--project', '-p', help='项目名称 (例如: 2077)')
    parser.add_argument('--date', '-d', help='日期 (例如: 0318)')
    parser.add_argument('--path', help='直接指定数据目录路径 (例如: 2077/0318)')
    parser.add_argument('--baseline', '-b', help='基线文件路径，用于对比')
    parser.add_argument('--output', '-o', help='输出报告文件名')
    
    args = parser.parse_args()
    
    # 确定数据目录
    if args.path:
        data_dir = args.path
    elif args.project and args.date:
        data_dir = f"data/{args.project}/{args.date}"
    else:
        print("请指定数据目录:")
        print("  方式1: --project 2077 --date 0318")
        print("  方式2: --path data/2077/0318")
        sys.exit(1)
    
    # 检查目录是否存在
    if not Path(data_dir).exists():
        print(f"✗ 目录不存在: {data_dir}")
        sys.exit(1)
    
    print(f"正在加载性能数据: {data_dir}\n")
    
    analyzer = PerformanceAnalyzer(data_dir)
    
    if not analyzer.load_data():
        sys.exit(1)
    
    # 如果指定了基线文件，进行对比
    if args.baseline:
        comparison_report = analyzer.compare_with_baseline(args.baseline)
        if comparison_report:
            print("\n" + comparison_report)
            
            # 保存对比报告
            if args.output:
                report_file = args.output
            else:
                report_file = Path(data_dir) / f"comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(comparison_report)
            print(f"\n✓ 对比报告已保存到: {report_file}")
    else:
        # 生成当前报告
        report = analyzer.generate_report()
        print("\n" + report)
        
        # 保存报告到文件
        if args.output:
            report_file = args.output
        else:
            report_file = Path(data_dir) / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ 报告已保存到: {report_file}")
        
        # 保存基线数据
        baseline_file = Path(data_dir) / "baseline.json"
        analyzer.save_baseline(baseline_file)
        
        print("\n" + "=" * 80)
        print("后续使用说明:")
        print("=" * 80)
        print("1. 优化网站后，导出新的性能数据")
        print(f"2. 将新数据放到新目录 (例如: {args.project}/{datetime.now().strftime('%m%d')})")
        print(f"3. 运行对比: python3 analyze_performance.py --path {args.project}/新日期 --baseline {data_dir}/baseline.json")
        print("=" * 80)


if __name__ == "__main__":
    main()
