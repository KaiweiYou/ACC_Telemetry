# 贡献指南

感谢您对ACC_Telemetry项目的关注！我们欢迎各种形式的贡献，包括但不限于代码贡献、文档改进、问题报告和功能建议。本指南将帮助您了解如何参与项目开发。

## 开发环境设置

1. Fork本仓库到您的GitHub账户
2. 克隆您的Fork到本地：
   ```bash
   git clone https://github.com/您的用户名/ACC_Telemetry.git
   cd ACC_Telemetry
   ```
3. 安装开发依赖：
   ```bash
   pip install -r dev-requirements.txt
   # 或者
   pip install -e ".[dev]"
   ```

## 代码规范

我们使用以下工具来确保代码质量：

- **flake8**：代码风格检查
- **black**：代码格式化
- **isort**：导入语句排序
- **mypy**：类型检查

在提交代码前，请运行质量检查脚本：

```bash
python -m scripts.quality_check
```

### Python代码风格指南

- 遵循[PEP 8](https://www.python.org/dev/peps/pep-0008/)代码风格指南
- 使用4个空格进行缩进（不使用制表符）
- 最大行长度为100个字符
- 使用类型注解（Python 3.8+）
- 为所有公共API提供文档字符串
- 使用有意义的变量名和函数名

## 提交流程

1. 创建一个新的分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. 进行您的修改

3. 运行测试确保所有测试通过：
   ```bash
   pytest
   ```

4. 运行代码质量检查：
   ```bash
   python -m scripts.quality_check
   ```

5. 提交您的更改：
   ```bash
   git commit -m "描述您的更改"
   ```

6. 推送到您的Fork：
   ```bash
   git push origin feature/your-feature-name
   ```

7. 创建Pull Request

## Pull Request指南

- 清晰描述您的更改内容和目的
- 如果解决了现有issue，请在PR描述中引用该issue
- 确保所有测试通过
- 确保代码质量检查通过
- 如果添加了新功能，请添加相应的测试和文档

## 版本控制规范

我们使用[语义化版本控制](https://semver.org/lang/zh-CN/)：

- **主版本号**：当进行不兼容的API更改时
- **次版本号**：当以向后兼容的方式添加功能时
- **修订号**：当进行向后兼容的缺陷修复时

## 文档

如果您的更改影响了用户体验或API，请同时更新相关文档。

## 问题报告

如果您发现了问题但没有时间修复，请创建一个issue，包含以下信息：

- 问题的简要描述
- 重现问题的步骤
- 预期行为和实际行为
- 环境信息（操作系统、Python版本等）
- 如果可能，提供截图或错误日志

## 功能请求

如果您有新功能的想法，请创建一个issue，描述该功能及其用例。

## 行为准则

- 尊重所有贡献者
- 提供建设性的反馈
- 专注于改进代码和项目质量

## 许可证

通过贡献代码，您同意您的贡献将在项目的MIT许可证下发布。

感谢您的贡献！