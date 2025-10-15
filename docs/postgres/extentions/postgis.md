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
### proj  4.9
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

