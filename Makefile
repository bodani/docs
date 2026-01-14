.PHONY: run build clean install

# 运行文档服务（开发模式）
run:
	bash -c "source .venv/bin/activate && mkdocs serve"

# 构建静态网站
build:
	bash -c "source .venv/bin/activate && mkdocs build"

# 清理构建产物
clean:
	rm -rf site/

# 安装依赖
install:
	# 创建虚拟环境（如果不存在）
	test -d .venv || python3 -m venv .venv
	# 激活虚拟环境并安装依赖
	bash -c "source .venv/bin/activate && pip install --break-system-packages --upgrade -r requirement.txt"

# 检查虚拟环境是否存在
check:
	@if [ ! -d ".venv" ]; then \
		echo "Virtual environment not found. Please run 'make install' first."; \
		exit 1; \
	fi
.PHONY: run build clean install check

