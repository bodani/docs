# postgis 安装

## 版本对应关系矩阵

3.3 对应 pg 17 实践有问题
https://trac.osgeo.org/postgis/wiki/UsersWikiPostgreSQLPostGIS

export POSTGIS_VERSION=3.4.0
curl -sSL "https://download.osgeo.org/postgis/source/postgis-${POSTGIS_VERSION}.tar.gz" | tar -xz && \
 cd postgis-"${POSTGIS_VERSION}" && \
    ./configure \
    --prefix="/opt/drycc/postgresql/${PG_MAJOR}/postgis/${POSTGIS_VERSION}" \
    --with-pgconfig=/opt/drycc/postgresql/"${PG_MAJOR}"/bin/pg_config

sudo apt install build-essential cmake
sudo apt-get install postgresql-server-dev-all \
 libgdal-dev \
 libgeos-dev \
 libjson-c-dev \
 libproj-dev \
 libprotobuf-c-dev \
 protobuf-c-compiler

## 编译安装， 前面的不成功就放弃吧！！！

## 前期准备

### proj 4.9

https://download.osgeo.org/proj/

### GEOS 3.7

https://download.osgeo.org/geos/

tar -xjvf geos-3.9.6.tar.bz2

mkdir build && cd build && cmake -DCMAKE_BUILD_TYPE=Release ..

# gdal 1.9

https://gdal.org/en/stable/download_past.html#download-past

export CXXFLAGS="-fpermissive"

### postgis 准备

下载安装包
wget https://download.osgeo.org/postgis/source/postgis-2.4.9.tar.gz

sudo apt-get install libgeos-dev

sudo apt-get install libpq-dev \
 libxml2-dev \

geos-config --version
geos-config --libs

# Ubuntu 2024 + postgersql10 + postgis2.5

wget https://download.osgeo.org/postgis/source/postgis-2.5.0.tar.gz
./configure --with-pgconfig=/usr/lib/postgresql/10/bin/pg_config

configure: error: could not find proj_api.h - you may need to specify the directory of a PROJ.4 installation using --with-projdir

重要提示关于 PROJ 版本:

PROJ 6.0+: 从 PROJ 6.0 开始，proj*api.h（旧的 C API）已被完全移除，并由新的 C++ API 替代。
软件兼容性:
如果你正在编译一个 需要旧版 PROJ API (proj_api.h) 的软件（通常是依赖于 GDAL <3.x 或直接集成旧 PROJ API 的软件），你需要安装 PROJ 5.x 或更早版本。软件本身的源代码通常需要能够兼容。
较新的软件（GDAL 3.x+）不再依赖 proj_api.h，而是使用新的 proj.h。如果你的软件较新但仍然提示找不到 proj_api.h，可能是软件的 configure 脚本有点旧或者有依赖关系没处理好。这时安装 libproj-dev 通常也足够了。
确认版本:
安装后运行 proj 命令（如果安装了命令行工具）通常显示版本信息。
或者查看库文件路径：ls /usr/lib/libproj.* 或 /usr/local/lib/libproj.\_，版本可能包含在文件名中。

apt list libproj-dev
Listing... Done
libproj-dev/noble,now 9.4.0-1build2 amd64 [installed]

sudo apt update
添加旧版本软件源（如适用于 Ubuntu Focal 20.04）：
注意： 混用不同版本源的软件包有风险，可能导致其他依赖问题。通常用于临时编译。
在 /etc/apt/sources.list 文件中添加一行：
<BASH>
deb http://archive.ubuntu.com/ubuntu focal universe

# 如果只用于安装指定包，可以创建临时文件：

sudo sh -c 'echo "deb http://archive.ubuntu.com/ubuntu focal universe" > /etc/apt/sources.list.d/focal-proj.list'

sudo apt update
sudo apt install libproj-dev/focal

# 可能会提示确认，接受即可

dpkg -l libproj-dev

wget https://download.osgeo.org/proj/proj-4.9.3.tar.gz
tar xf proj-4.9.3.tar.gz
cd proj-4.9.3
./configure && make -j$(nproc)
sudo make install
sudo ldconfig

# 安装编译依赖

sudo apt install libxml2-dev libgeos-dev libgdal-dev

# 编译安装 PostGIS

wget https://download.osgeo.org/postgis/source/postgis-2.5.0.tar.gz
tar xf postgis-2.5.0.tar.gz
cd postgis-2.5.0
./configure \
 --with-pgconfig=/usr/lib/postgresql/10/bin/pg_config \
 --with-projdir=/usr/local
make -j$(nproc)
sudo make install
