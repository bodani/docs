-- 创建虚拟环境
uv venv && source .venv/bin/activate

-- 安装依赖
uv pip install -r requirement.txt -i  https://pypi.doubanio.com/simple/

-- 初始化项目
mkdocs new .

-- 启动服务
mkdocs serve
