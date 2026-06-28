# Xiaoyi SDK Makefile
# 常用开发命令集合

.PHONY: help install dev-install test test-cov lint format type-check clean build publish security all

# 默认目标：显示帮助信息
help:
	@echo "Xiaoyi SDK 开发命令集合"
	@echo ""
	@echo "使用方法: make [目标]"
	@echo ""
	@echo "可用目标:"
	@echo "  help          - 显示此帮助信息"
	@echo "  install       - 安装生产依赖"
	@echo "  dev-install   - 安装开发依赖"
	@echo "  test          - 运行单元测试"
	@echo "  test-cov      - 运行测试并生成覆盖率报告"
	@echo "  lint          - 运行代码格式检查 (black, isort, flake8)"
	@echo "  format        - 自动格式化代码"
	@echo "  type-check    - 运行类型检查 (mypy)"
	@echo "  security      - 运行安全检查 (bandit, safety)"
	@echo "  clean         - 清理构建产物"
	@echo "  build         - 构建Python包"
	@echo "  publish       - 发布到PyPI (需要配置)"
	@echo "  all           - 运行所有检查"
	@echo ""

# 安装生产依赖
install:
	pip install --upgrade pip
	pip install -e .

# 安装开发依赖
dev-install:
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

# 运行单元测试
test:
	pytest tests/ -v --tb=short

# 运行测试并生成覆盖率报告
test-cov:
	pytest tests/ -v --tb=short --cov=src/xiaoyi_sdk --cov-report=term-missing --cov-report=html
	@echo ""
	@echo "覆盖率报告已生成: htmlcov/index.html"

# 运行代码格式检查
lint:
	@echo "运行Black检查..."
	black --check --diff src/ tests/
	@echo "运行isort检查..."
	isort --check-only --diff src/ tests/
	@echo "运行flake8检查..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

# 自动格式化代码
format:
	@echo "格式化代码..."
	black src/ tests/
	isort src/ tests/
	@echo "格式化完成！"

# 运行类型检查
type-check:
	mypy src/xiaoyi_sdk --strict --ignore-missing-imports

# 运行安全检查
security:
	@echo "运行bandit安全检查..."
	bandit -r src/xiaoyi_sdk -ll --skip B101
	@echo "检查依赖安全..."
	safety check --full-report || true

# 清理构建产物
clean:
	@echo "清理构建产物..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "清理完成！"

# 构建Python包
build:
	@echo "构建Python包..."
	python -m build
	@echo "检查包格式..."
	twine check dist/*
	@echo "构建完成！产物位于 dist/ 目录"

# 发布到PyPI (测试环境)
publish-test:
	@echo "发布到TestPyPI..."
	twine upload --repository testpypi dist/*
	@echo "发布完成！"

# 发布到PyPI (正式环境)
publish:
	@echo "发布到PyPI..."
	twine upload dist/*
	@echo "发布完成！"

# 运行所有检查
all: lint type-check test-cov security
	@echo ""
	@echo "✅ 所有检查完成！"

# 快速开发流程
dev: format lint test
	@echo ""
	@echo "✅ 开发流程完成！代码已格式化并检查通过"

# Windows兼容版本 (使用PowerShell)
# 如果在Windows上运行，可以使用以下命令

install-win:
	pip install --upgrade pip
	pip install -e .

dev-install-win:
	pip install --upgrade pip
	pip install -e ".[dev]"
	pip install pre-commit
	pre-commit install

test-win:
	pytest tests/ -v --tb=short

test-cov-win:
	pytest tests/ -v --tb=short --cov=src/xiaoyi_sdk --cov-report=term-missing --cov-report=html

lint-win:
	@echo "运行Black检查..."
	black --check --diff src/ tests/
	@echo "运行isort检查..."
	isort --check-only --diff src/ tests/
	@echo "运行flake8检查..."
	flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503

format-win:
	@echo "格式化代码..."
	black src/ tests/
	isort src/ tests/
	@echo "格式化完成！"

clean-win:
	@echo "清理构建产物..."
	if exist build rmdir /s /q build
	if exist dist rmdir /s /q dist
	if exist *.egg-info rmdir /s /q *.egg-info
	if exist .pytest_cache rmdir /s /q .pytest_cache
	if exist .mypy_cache rmdir /s /q .mypy_cache
	if exist .coverage del .coverage
	if exist htmlcov rmdir /s /q htmlcov
	if exist coverage.xml del coverage.xml
	@echo "清理完成！"

build-win:
	@echo "构建Python包..."
	python -m build
	@echo "检查包格式..."
	twine check dist/*
	@echo "构建完成！"