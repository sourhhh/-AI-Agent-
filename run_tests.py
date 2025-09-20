#!/usr/bin/env python3
"""
Code Fixer Agent 测试运行脚本
"""

import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def run_tests():
    """运行所有测试"""
    # 发现并加载所有测试
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')

    # 运行测试
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)

    # 输出测试结果
    print("\n" + "=" * 50)
    print(f"测试结果: {'通过' if result.wasSuccessful() else '失败'}")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 50)

    return result.wasSuccessful()


if __name__ == '__main__':
    print("开始运行 Code Fixer Agent 测试...")
    success = run_tests()
    sys.exit(0 if success else 1)