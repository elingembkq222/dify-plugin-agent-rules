.PHONY: help test test-verbose test-automated test-db-connection test-missing-table test-comprehensive test-api test-generate-rule test-uuid test-uuid-validation clean install

# 默认目标
help:
	@echo "可用的测试命令:"
	@echo "  make test              - 运行所有测试"
	@echo "  make test-verbose      - 运行所有测试(详细输出)"
	@echo "  make test-automated    - 运行自动化测试套件"
	@echo "  make test-db-connection - 运行数据库连接错误测试"
	@echo "  make test-missing-table - 运行数据表不存在测试"
	@echo "  make test-comprehensive - 运行全面数据库错误测试"
	@echo "  make test-api          - 运行API测试"
	@echo "  make test-generate-rule - 运行规则生成测试"
	@echo "  make test-uuid         - 运行UUID生成测试"
	@echo "  make test-uuid-validation - 运行UUID验证测试"
	@echo "  make install           - 安装依赖"
	@echo "  make clean             - 清理临时文件"

# 安装依赖
install:
	pip install pytest pytest-cov pymysql requests python-dotenv

# 运行所有测试
test:
	chmod +x tests/run_all_tests.sh
	./tests/run_all_tests.sh

# 运行所有测试(详细输出)
test-verbose:
	chmod +x tests/run_all_tests.sh
	python tests/test_automated.py -v

# 运行自动化测试套件
test-automated:
	python tests/test_automated.py

# 运行数据库连接错误测试
test-db-connection:
	python tests/test_db_connection_error.py

# 运行数据表不存在测试
test-missing-table:
	python tests/test_missing_table.py

# 运行全面数据库错误测试
test-comprehensive:
	python tests/test_comprehensive_db_errors.py

# 运行API测试
test-api:
	python tests/test_api.py

# 运行规则生成测试
test-generate-rule:
	python tests/test_generate_rule.py

# 运行UUID生成测试
test-uuid:
	python tests/test_uuid_generation.py

# 运行UUID验证测试
test-uuid-validation:
	python tests/test_uuid_validation.py

# 运行pytest并生成覆盖率报告
coverage:
	pip install pytest-cov
	pytest tests/ --cov=. --cov-report=html --cov-report=term

# 清理临时文件
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/