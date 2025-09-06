#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目质量检查脚本

检查代码质量、项目结构和配置完整性
使用flake8、black、isort和mypy等工具进行代码质量检查
"""

import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 定义代码质量工具列表
CODE_QUALITY_TOOLS = {
    "flake8": "flake8 --max-line-length=100 --exclude=.git,__pycache__,build,dist,.venv,venv,examples",
    "black": 'black --check --diff --exclude="/(.git|__pycache__|build|dist|.venv|venv|examples)/"',
    "isort": "isort --profile black --check --diff --skip=examples .",
    "mypy": 'mypy --ignore-missing-imports --exclude="(build|dist|\\.venv|venv|examples)"',
}


class QualityChecker:
    """项目质量检查器"""

    def __init__(self):
        self.project_root = project_root
        self.issues = []
        self.warnings = []
        self.suggestions = []
        self.tool_results = {}

    def _check_tools_installed(self) -> Dict[str, bool]:
        """检查代码质量工具是否已安装

        Returns:
            Dict[str, bool]: 工具安装状态字典
        """
        tools_status = {}

        for tool in CODE_QUALITY_TOOLS:
            try:
                # 尝试导入模块
                if tool == "black":
                    import black

                    tools_status[tool] = True
                elif tool == "flake8":
                    import flake8

                    tools_status[tool] = True
                elif tool == "isort":
                    import isort

                    tools_status[tool] = True
                elif tool == "mypy":
                    import mypy

                    tools_status[tool] = True
                else:
                    tools_status[tool] = False
            except ImportError:
                tools_status[tool] = False
                self.add_warning("工具", f"{tool} 未安装，跳过相关检查")

        return tools_status

    def _run_code_quality_tools(self, tools_status: Dict[str, bool]) -> None:
        """运行代码质量工具

        Args:
            tools_status: 工具安装状态字典
        """
        print("运行代码质量工具...")

        for tool, installed in tools_status.items():
            if not installed:
                continue

            print(f"运行 {tool}...")
            cmd = f"{CODE_QUALITY_TOOLS[tool]} {self.project_root}"

            try:
                result = subprocess.run(
                    cmd, shell=True, capture_output=True, text=True, encoding="utf-8"
                )

                if result.returncode != 0:
                    self.add_issue(
                        tool,
                        f"检查失败，请修复以下问题:\n{result.stdout}\n{result.stderr}",
                    )
                    self.tool_results[tool] = result.stdout + "\n" + result.stderr
                else:
                    print(f"{tool} 检查通过")
                    self.tool_results[tool] = "检查通过"
            except Exception as e:
                self.add_warning(tool, f"运行失败: {str(e)}")
                self.tool_results[tool] = f"运行失败: {str(e)}"

    def add_issue(self, category: str, message: str):
        """添加问题"""
        self.issues.append(f"[{category}] {message}")

    def add_warning(self, category: str, message: str):
        """添加警告"""
        self.warnings.append(f"[{category}] {message}")

    def add_suggestion(self, category: str, message: str):
        """添加建议"""
        self.suggestions.append(f"[{category}] {message}")

    def check_project_structure(self):
        """检查项目结构"""
        print("检查项目结构...")

        required_files = [
            "README.md",
            "requirements.txt",
            "setup.py",
            ".gitignore",
            "LICENSE",
        ]

        required_dirs = [
            "acc_telemetry",
            "acc_telemetry/core",
            "acc_telemetry/ui",
            "acc_telemetry/utils",
            "tests",
            "examples",
            "docs",
        ]

        # 检查必需文件
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                self.add_issue("结构", f"缺少必需文件: {file_path}")

        # 检查必需目录
        for dir_path in required_dirs:
            if not (self.project_root / dir_path).exists():
                self.add_issue("结构", f"缺少必需目录: {dir_path}")

        # 检查__init__.py文件
        python_dirs = [
            "acc_telemetry",
            "acc_telemetry/core",
            "acc_telemetry/ui",
            "acc_telemetry/utils",
            "tests",
            "scripts",
        ]

        for dir_path in python_dirs:
            init_file = self.project_root / dir_path / "__init__.py"
            if (self.project_root / dir_path).exists() and not init_file.exists():
                self.add_warning("结构", f"缺少__init__.py文件: {dir_path}")

    def check_code_quality(self):
        """检查代码质量"""
        print("检查代码质量...")

        # 检查是否安装了代码质量工具
        tools_status = self._check_tools_installed()

        # 如果安装了工具，则使用工具进行检查
        if any(tools_status.values()):
            self._run_code_quality_tools(tools_status)

        # 继续进行基本的代码质量检查
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            # 跳过虚拟环境和构建目录
            file_str = str(py_file)
            if any(
                skip_dir in file_str
                for skip_dir in [
                    ".venv",
                    "venv",
                    "__pycache__",
                    "build",
                    "dist",
                    ".git",
                ]
            ):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # 检查语法
                try:
                    ast.parse(content)
                except SyntaxError as e:
                    self.add_issue(
                        "语法", f"{py_file.relative_to(self.project_root)}: {e}"
                    )

                # 检查编码声明
                lines = content.split("\n")
                if len(lines) > 1:
                    first_two_lines = "\n".join(lines[:2])
                    if (
                        "coding" not in first_two_lines
                        and "utf-8" not in first_two_lines
                    ):
                        self.add_warning(
                            "编码",
                            f"{py_file.relative_to(self.project_root)}: 建议添加编码声明",
                        )

                # 检查文档字符串
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                            if not ast.get_docstring(node):
                                self.add_suggestion(
                                    "文档",
                                    f"{py_file.relative_to(self.project_root)}: "
                                    f"{node.name} 缺少文档字符串",
                                )
                except:
                    pass

            except Exception as e:
                self.add_warning("读取", f"无法读取文件 {py_file}: {e}")

    def check_dependencies(self):
        """检查依赖配置"""
        print("检查依赖配置...")

        # 检查requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, "r", encoding="utf-8") as f:
                    requirements = f.read().strip().split("\n")

                required_deps = ["customtkinter", "python-osc", "Pillow"]
                for dep in required_deps:
                    if not any(dep in req for req in requirements):
                        self.add_warning(
                            "依赖", f"requirements.txt中可能缺少依赖: {dep}"
                        )
            except Exception as e:
                self.add_issue("依赖", f"无法读取requirements.txt: {e}")

        # 检查setup.py
        setup_file = self.project_root / "setup.py"
        if setup_file.exists():
            try:
                with open(setup_file, "r", encoding="utf-8") as f:
                    setup_content = f.read()

                if "install_requires=requirements" in setup_content:
                    if 'with open("requirements.txt"' not in setup_content:
                        self.add_warning("依赖", "setup.py引用requirements但未读取文件")
            except Exception as e:
                self.add_issue("依赖", f"无法读取setup.py: {e}")

    def check_configuration(self):
        """检查配置文件"""
        print("检查配置文件...")

        config_file = self.project_root / "acc_telemetry" / "config.py"
        if config_file.exists():
            try:
                spec = importlib.util.spec_from_file_location("config", config_file)
                config = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(config)

                # 检查必需的配置项
                required_configs = ["OSC_CONFIG", "DASHBOARD_CONFIG", "ADVANCED_CONFIG"]
                for config_name in required_configs:
                    if not hasattr(config, config_name):
                        self.add_issue("配置", f"缺少配置项: {config_name}")

                # 检查OSC配置
                if hasattr(config, "OSC_CONFIG"):
                    osc_config = config.OSC_CONFIG
                    required_osc_keys = ["ip", "port", "update_rate"]
                    for key in required_osc_keys:
                        if key not in osc_config:
                            self.add_issue("配置", f"OSC_CONFIG缺少键: {key}")

            except Exception as e:
                self.add_issue("配置", f"无法加载配置文件: {e}")

    def check_tests(self):
        """检查测试文件"""
        print("检查测试文件...")

        test_dir = self.project_root / "tests"
        if test_dir.exists():
            test_files = list(test_dir.glob("test_*.py"))
            if not test_files:
                self.add_warning("测试", "tests目录中没有找到测试文件")

            for test_file in test_files:
                try:
                    with open(test_file, "r", encoding="utf-8") as f:
                        content = f.read()

                    if "unittest" not in content and "pytest" not in content:
                        self.add_warning(
                            "测试", f"{test_file.name}: 未使用标准测试框架"
                        )

                except Exception as e:
                    self.add_warning("测试", f"无法读取测试文件 {test_file}: {e}")

    def check_documentation(self):
        """检查文档"""
        print("检查文档...")

        readme_file = self.project_root / "README.md"
        if readme_file.exists():
            try:
                with open(readme_file, "r", encoding="utf-8") as f:
                    readme_content = f.read()

                required_sections = ["安装", "使用", "功能", "项目结构"]
                for section in required_sections:
                    if section not in readme_content:
                        self.add_suggestion(
                            "文档", f"README.md建议添加{section}相关内容"
                        )

                if len(readme_content) < 500:
                    self.add_suggestion("文档", "README.md内容较少，建议补充更多信息")

            except Exception as e:
                self.add_warning("文档", f"无法读取README.md: {e}")

    def run_all_checks(self):
        """运行所有检查"""
        print("开始项目质量检查...")
        print("=" * 50)

        self.check_project_structure()
        self.check_code_quality()
        self.check_dependencies()
        self.check_configuration()
        self.check_tests()
        self.check_documentation()

        print("\n" + "=" * 50)
        print("检查完成！")

        # 输出结果
        if self.issues:
            print(f"\n❌ 发现 {len(self.issues)} 个问题:")
            for issue in self.issues:
                print(f"  {issue}")

        if self.warnings:
            print(f"\n⚠️  发现 {len(self.warnings)} 个警告:")
            for warning in self.warnings:
                print(f"  {warning}")

        if self.suggestions:
            print(f"\n💡 发现 {len(self.suggestions)} 个建议:")
            for suggestion in self.suggestions:
                print(f"  {suggestion}")

        if not self.issues and not self.warnings:
            print("\n✅ 项目质量检查通过！")

        return len(self.issues) == 0


def main():
    """主函数"""
    checker = QualityChecker()
    success = checker.run_all_checks()

    # 显示代码质量工具的详细结果
    if checker.tool_results:
        print("\n代码质量工具检查结果:")
        for tool, result in checker.tool_results.items():
            print(f"\n--- {tool} 检查结果 ---")
            print(result)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
