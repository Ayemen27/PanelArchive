#!/bin/bash
#pgsql安装脚本
install_dir=/www/server/pgsql
pgsql_version=$1
down_url=$2

GetCpuStat(){
        time1=$(cat /proc/stat |grep 'cpu ')
        sleep 1
        time2=$(cat /proc/stat |grep 'cpu ')
        cpuTime1=$(echo ${time1}|awk '{print $2+$3+$4+$5+$6+$7+$8}')
        cpuTime2=$(echo ${time2}|awk '{print $2+$3+$4+$5+$6+$7+$8}')
        runTime=$((${cpuTime2}-${cpuTime1}))
        idelTime1=$(echo ${time1}|awk '{print $5}')
        idelTime2=$(echo ${time2}|awk '{print $5}')
        idelTime=$((${idelTime2}-${idelTime1}))
        useTime=$(((${runTime}-${idelTime})*3))
        [ ${useTime} -gt ${runTime} ] && cpuBusy="true"
        if [ "${cpuBusy}" == "true" ]; then
                cpuCore=$((${cpuInfo}/2))
        else
                cpuCore=$((${cpuInfo}-1))
        fi
}

cpuInfo=$(getconf _NPROCESSORS_ONLN)
if [ "${cpuInfo}" -ge "2" ];then
        GetCpuStat
else
        cpuCore="1"
fi

loongarch64Check=$(uname -a|grep loongarch64)
if [ "${loongarch64Check}" ];then
    loongarch64_dis="--disable-spinlocks"
    loongarch64_build="--build=arm-linux"
fi

#进入软件的制定安装目录
echo "Enter the directory /usr/local, download pgsql package"
cd /usr/local
#判断是否有postgre版本的安装包
if [ -d postgresql* ]
then
        rm -rf /usr/local/postgresql*
        echo "Installation package deleted successfully"
fi
#判断是否有旧的编译文件
if [ -d /usr/local/pgsql ]
then
        rm -rf /usr/local/pgsql
        echo "The old compiled file was deleted successfully"
fi

#开始下载pgsql版本10.5并解压
if [ ! -d /usr/local/src ]
then
        mkdir /usr/local/src
fi

cd /usr/local/src
rm -rf post*
wget $down_url --no-check-certificate
if [ $? == 0 ]
then
tar -zxf $pgsql_version -C /usr/local/
fi

echo "pgsql package decompressed successfully"
#判断用户是否存在
user=postgres
group=postgres

#create group if not exists
egrep "^$group" /etc/group >& /dev/null
if [ $? -ne 0 ]
then
    groupadd $group
fi

#create user if not exists
egrep "^$user" /etc/passwd >& /dev/null
if [ $? -ne 0 ]
then
    useradd -m $user -g $group
fi

echo "Rename postgresql and enter the installation directory"
mv /usr/local/post* /usr/local/pgsql
cd /usr/local/pgsql
#-------------------------------安装pgsql------------------------------------
echo "Install some library files"
#yum install -y zlib zlib-devel uuid uuid-devel >& /del/null
yum install -y zlib zlib-devel uuid uuid-devel
apt-get install -y libossp-uuid-dev
echo "Start the configure step"
./configure --prefix=$install_dir --without-readline --with-uuid=ossp
if [ $? == 0 ]
then
        echo "The configure configuration is passed, and the make compilation starts"
        make -j $cpuCore
        if [ $? == 0 ]
        then
                echo "Make compile passed, start the make install installation steps"
                make install
                if [ $? != 0 ];then
                        echo "make install failed"
                fi
                echo "Successful installation"
        else
                echo "Make compilation failed, check for errors."
        fi
else
        echo "configure failed to check the configuration, please check the error to install the library file"
fi
echo "Start the configuration of pgsql"
echo "Create a data directory for pgsql"
mkdir -p ${install_dir}/logs
echo "Modify user group"
chown -R postgres:postgres ${install_dir}
chmod -R 700   ${install_dir}/data

echo "/www/server/pgsql/data" >/www/server/pgsql/data_directory
echo "Add environment variables and enter the home directory of the postgres user"
cd /home/postgres
if [ -f /home/postgres/.bash_profile ] ;then
        /bin/cp /home/postgres/.bash_profile /home/postgres/.bash_profile.bak
        echo "export PGHOME=${install_dir}" >> /home/postgres/.bash_profile
        echo "export PGDATA=${install_dir}/data" >> /home/postgres/.bash_profile
        echo "export PATH=${install_dir}/bin:\$PATH " >> /home/postgres/.bash_profile
        echo "MANPATH=$PGHOME/share/man:$MANPATH" >> /home/postgres/.bash_profile
        echo "LD_LIBRARY_PATH=$PGHOME/lib:$LD_LIBRARY_PATH" >> /home/postgres/.bash_profile
        source /home/postgres/.bash_profile
fi
if [ -f /home/postgres/.profile ] ;then
        /bin/cp /home/postgres/.profile /home/postgres/.profile.bak
        echo "export PGHOME=${install_dir}" >> /home/postgres/.profile
        echo "export PGDATA=${install_dir}/data" >> /home/postgres/.profile
        echo "export PATH=${install_dir}/bin:\$PATH " >> /home/postgres/.profile
        echo "MANPATH=$PGHOME/share/man:$MANPATH" >> /home/postgres/.profile
        echo "LD_LIBRARY_PATH=$PGHOME/lib:$LD_LIBRARY_PATH" >> /home/postgres/.profile
        source /home/postgres/.profile
fi
alias pg_start='pg_ctl -D $PGDATA -l ${install_dir}/logs/pgsql.log start'
alias ps_stop='pg_ctl -D $PGDATA -l ${install_dir}logs/pgsql.log stop'
echo "Switch to the postgres user to initialize the database"
su - postgres -c "${install_dir}/bin/initdb -D ${install_dir}/data"

echo "Enable slow query SQL statement tracking"
cat >> ${install_dir}/data/postgresql.conf <<EOF
logging_collector = on
log_destination = 'stderr'
log_directory = '${install_dir}/logs'
log_filename = 'postgresql-%Y-%m-%d.log'
log_statement = all
log_min_duration_statement = 5000
EOF

su - postgres -c "${install_dir}/bin/postgres -D ${install_dir}/data >>${install_dir}/logs/pgsql.log 2>&1 &"
echo "---------------------------------------------------------------------------------------"
echo "---------------------------------------------------------------------------------------"
echo "----------------------------SUCCESS INSTALLATION OF POSTGRESQL-------------------------"

