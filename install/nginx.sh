#!/bin/bash
PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
LANG=en_US.UTF-8

public_file=/www/server/panel/install/public.sh
publicFileMd5=$(md5sum ${public_file} 2>/dev/null | awk '{print $1}')
md5check="484c945780dc4a802cff267f3fb15a66"
if [ "${publicFileMd5}" != "${md5check}" ]; then
    wget -O Tpublic.sh https://node.aapanel.com/install/public.sh -T 20
    publicFileMd5=$(md5sum Tpublic.sh 2>/dev/null | awk '{print $1}')
    if [ "${publicFileMd5}" == "${md5check}" ]; then
        \cp -rpa Tpublic.sh $public_file
    fi
    rm -f Tpublic.sh
fi
. $public_file
download_Url=$NODE_URL

tengine='3.1.0'
nginx_108='1.8.1'
nginx_112='1.12.2'
nginx_114='1.14.2'
nginx_115='1.15.10'
nginx_116='1.16.1'
nginx_117='1.17.10'
nginx_118='1.18.0'
nginx_119='1.19.8'
nginx_120='1.20.2'
nginx_121='1.21.4'
nginx_122='1.22.1'
nginx_123='1.23.4'
nginx_124='1.24.0'
nginx_125='1.25.5'
nginx_126='1.26.3'
nginx_127='1.27.5'
nginx_128='1.28.0'
openresty='1.25.3.2'

Root_Path=$(cat /var/bt_setupPath.conf)
Setup_Path=$Root_Path/server/nginx
run_path="/root"
Is_64bit=$(getconf LONG_BIT)

ARM_CHECK=$(uname -a | grep -E 'aarch64|arm|ARM')
if [ "$2" == "1.24" ];then
    ARM_CHECK=""
    JEM_CHECK="disable"
fi
LUAJIT_VER="2.0.4"
LUAJIT_INC_PATH="luajit-2.0"

if [ "${ARM_CHECK}" ]; then
    LUAJIT_VER="2.1.0-beta3"
    LUAJIT_INC_PATH="luajit-2.1"
fi

if [ "$2" == "openresty" ] || [ "$2" == "openresty127" ];then
    wget -O nginx.sh ${download_Url}/install/0/nginx.sh && sh nginx.sh install $2
    exit 0
fi

Get_Sys_Version(){
	if [ -f "/etc/os-release" ];then
		. /etc/os-release
		OS_V=${VERSION_ID%%.*}
		if [ "${ID}" == "debian" ] && [[ "${OS_V}" =~ ^(10|11|12|13)$ ]];then
			OS_NAME=${ID}
		elif [ "${ID}" == "ubuntu" ] && [[ "${OS_V}" =~ ^(18|20|22|24)$ ]];then
			OS_NAME=${ID}
		elif [ "${ID}" == "centos" ] && [[ "${OS_V}" =~ ^(7)$ ]];then
			OS_NAME="el"
		elif [ "${ID}" == "opencloudos" ] && [[ "${OS_V}" =~ ^(9)$ ]];then
			OS_NAME=${ID}
		elif [ "${ID}" == "tencentos" ] && [[ "${OS_V}" =~ ^(4)$ ]];then
			OS_NAME=${ID}
		elif [ "${ID}" == "hce" ] && [[ "${OS_V}" =~ ^(2)$ ]];then
		    OS_NAME=${ID}
        elif { [ "${ID}" == "almalinux" ] || [ "${ID}" == "centos" ] || [ "${ID}" == "rocky" ] || [ "${ID}" == "rhel" ]; } && [[ "${OS_V}" =~ ^(9)$ ]]; then
            OS_NAME="el"
		fi
	fi

    X86_CHECK=$(uname -m|grep x86_64)

    if [ -z "${OS_NAME}" ] || [ -z "${X86_CHECK}" ];then
        wget -O nginx.sh ${download_Url}/install/0/nginx.sh && sh nginx.sh $actionType $version
        exit
    fi
}

loongarch64Check=$(uname -a | grep loongarch64)
if [ "${loongarch64Check}" ]; then
    wget -O nginx.sh ${download_Url}/install/0/loongarch64/nginx.sh && sh nginx.sh $1 $2
    exit
fi

FNOS_CHECK=$(grep fnOS /etc/issue)
if [ "${FNOS_CHECK}" ];then
    re_match1=$(grep listen /usr/trim/nginx/conf/nginx.conf|grep "0.0.0.0:80 ")
    re_match2=$(grep listen /usr/trim/nginx/conf/nginx.conf|grep "443 ssl default")
    sed -i "s/${re_match1}/#${re_match1}/g" /usr/trim/nginx/conf/nginx.conf
    sed -i "s/${re_match2}/#${re_match2}/g" /usr/trim/nginx/conf/nginx.conf
    sed -i "s/listen          \[::\]:80 ipv6only=on/#listen          [::]:80 ipv6only=on/g" /usr/trim/nginx/conf/nginx.conf
    sed -i "s/listen          \[::\]:443 ssl ipv6only/#listen          [::]:443 ssl ipv6only/g" /usr/trim/nginx/conf/nginx.conf
    systemctl stop trim_nginx
    wget -O /www/server/panel/vhost/nginx/0.default.conf ${download_Url}/install/conf/fnos-0.default.conf
    systemctl start trim_nginx
fi
#HUAWEI_CLOUD_EULER=$(cat /etc/os-release |grep '"Huawei Cloud EulerOS 1')
#EULER_OS=$(cat /etc/os-release |grep "EulerOS 2.0 ")
#if [ "${HUAWEI_CLOUD_EULER}" ] || [ "${EULER_OS}" ];then
#        wget -O nginx.sh ${download_Url}/install/1/nginx.sh && sh nginx.sh $1 $2
#        exit
#fi

if [ -z "${cpuCore}" ]; then
    cpuCore="1"
fi

Ready_Check(){
    WWW_DISK_SPACE=$(df |grep /www|awk '{print $4}')
    ROOT_DISK_SPACE=$(df |grep /$|awk '{print $4}')
 
   if [ "${ROOT_DISK_SPACE}" -le 112000 ];then
	df -h
        echo -e "系统盘剩余空间不足100M 无法继续安装！"
        echo -e "请尝试清理磁盘空间后再重新进行安装"
        exit 1
    fi
    if [ "${WWW_DISK_SPACE}" ] && [ "${WWW_DISK_SPACE}" -le 112000 ] ;then
        echo -e "/www盘剩余空间不足100M 无法继续安装！"
        echo -e "请尝试清理磁盘空间后再重新进行安装"
        exit 1
    fi

    # ROOT_DISK_INODE=$(df -i|grep /$|awk '{print $2}')
	# if [ "${ROOT_DISK_INODE}" != "0" ];then
	# 	ROOT_DISK_INODE_FREE=$(df -i|grep /$|awk '{print $4}')
	# 	if [ "${ROOT_DISK_INODE_FREE}" -le 1000 ];then
	# 		echo -e "系统盘剩余inodes空间不足1000,无法继续安装！"
	# 		echo -e "请尝试清理磁盘空间后再重新进行安装"
	# 		exit 1
	# 	fi
	# fi

	# WWW_DISK_INODE==$(df -i|grep /www|awk '{print $2}')
	# if [ "${WWW_DISK_INODE}" ] && [ "${WWW_DISK_INODE}" != "0" ] ;then
	# 	WWW_DISK_INODE_FREE=$(df -i|grep /www|awk '{print $4}')
	# 	if [ "${WWW_DISK_INODE_FREE}" ] && [ "${WWW_DISK_INODE_FREE}" -le 1000 ] ;then
	# 		echo -e "/www盘剩余inodes空间不足1000, 无法继续安装！"
	# 		echo -e "请尝试清理磁盘空间后再重新进行安装"
	# 		exit 1
	# 	fi
	# fi

    SYS_BIN=(wget tar xz unzip)
    for RUN_BIN in ${SYS_BIN[@]};
    do
        which ${RUN_BIN} > /dev/null 2>&1
        if [ $? -ne 0 ];then
            if [ "${PM}" == "yum" ];then
                yum reinstall ${RUN_BIN} -y
            elif [ "${PM}" == "apt-get" ];then
                apt-get reinstall ${RUN_BIN} -y
            fi
            which ${RUN_BIN} > /dev/null 2>&1
            if [ $? -ne 0 ];then
                echo -e "检测到系统组件${RUN_BIN}不存在，无法继续安装"
                echo -e "请截图以上报错信息发帖至论坛www.bt.cn/bbs求助"
                exit 1
            fi
        fi
    done
}
System_Lib() {
    if [ "${PM}" == "yum" ] || [ "${PM}" == "dnf" ]; then
        Pack="gcc gcc-c++ curl curl-devel libtermcap-devel ncurses-devel libevent-devel readline-devel libuuid-devel"
        ${PM} install ${Pack} -y
	wget -O fix_install.sh $download_Url/tools/fix_install.sh
	nohup bash fix_install.sh > /www/server/panel/install/fix.log 2>&1 &
    elif [ "${PM}" == "apt-get" ]; then
        apt-get update
        LIBCURL_VER=$(dpkg -l | grep libx11-6 | awk '{print $3}')
        if [ "${LIBCURL_VER}" == "2:1.6.9-2ubuntu1.3" ]; then
            apt remove libx11* -y
            apt install libx11-6 libx11-dev libx11-data -y
        fi
        Pack="gcc g++ libgd3 libgd-dev libevent-dev libncurses5-dev libreadline-dev uuid-dev"
        ${PM} install ${Pack} -y
    fi

}

Service_Add() {
    if [ "${PM}" == "yum" ] || [ "${PM}" == "dnf" ]; then
        chkconfig --add nginx
        chkconfig --level 2345 nginx on
    elif [ "${PM}" == "apt-get" ]; then
        update-rc.d nginx defaults
    fi
	if [ "$?" == "127" ];then
		wget -O /usr/lib/systemd/system/nginx.service ${download_Url}/init/systemd/nginx.service
		systemctl enable nginx.service
	fi
}
Service_Del() {
    if [ "${PM}" == "yum" ] || [ "${PM}" == "dnf" ]; then
        chkconfig --del nginx
        chkconfig --level 2345 nginx off
    elif [ "${PM}" == "apt-get" ]; then
        update-rc.d nginx remove
    fi
}
Set_Time() {
    BASH_DATE=$(stat nginx.sh | grep Modify | awk '{print $2}' | tr -d '-')
    SYS_DATE=$(date +%Y%m%d)
    [ "${SYS_DATE}" -lt "${BASH_DATE}" ] && date -s "$(curl https://www.bt.cn//api/index/get_date)"
}
Install_Jemalloc() {
    if [ ! -f '/usr/local/lib/libjemalloc.so' ]; then
        wget -O ${OS_NAME}-${OS_V}-jemalloc-5.0.1.tar.gz ${download_Url}/soft/lib/jemalloc/${OS_NAME}-${OS_V}-jemalloc-5.0.1.tar.gz
        tar -xvf ${OS_NAME}-${OS_V}-jemalloc-5.0.1.tar.gz
        cd jemalloc-5.0.1
        make install
        ldconfig
        cd ..
        rm -rf jemalloc*
        rm -f ${OS_NAME}-${OS_V}-jemalloc-5.0.1.tar.gz
    fi
}
Install_LuaJIT2(){
    LUAJIT_INC_PATH="luajit-2.1"
    wget -O ${OS_NAME}-${OS_V}-luajit2.tar.gz ${download_Url}/soft/lib/luajit2/${OS_NAME}-${OS_V}-luajit2.tar.gz
    tar -xvf ${OS_NAME}-${OS_V}-luajit2.tar.gz
    cd luajit2-2.1-20230410
    make install
    cd .. 
    ln -sf /usr/local/lib/libluajit-5.1.so.2 /usr/local/lib64/libluajit-5.1.so.2
    LD_SO_CHECK=$(cat /etc/ld.so.conf|grep /usr/local/lib)
    if [ -z "${LD_SO_CHECK}" ];then
         echo "/usr/local/lib" >>/etc/ld.so.conf
    fi
    ldconfig
    rm -rf luajit2-2.1-20230410
    rm -f ${OS_NAME}-${OS_V}-luajit2.tar.gz
}
Install_LuaJIT() {
    if [ "${version}" == "1.23" ] || [ "${version}" == "1.24" ] || [ "${version}" == "tengine" ] || [ "${version}" == "1.25" ] || [ "${version}" == "1.26" ]  || [ "${version}" == "1.27" ] || [ "${version}" == "1.28" ];then
        Install_LuaJIT2
        return
    fi
    OEPN_LUAJIT=$(cat /usr/local/include/luajit-2.1/luajit.h|grep 2022)
    if [ ! -f '/usr/local/lib/libluajit-5.1.so' ] || [ ! -f "/usr/local/include/${LUAJIT_INC_PATH}/luajit.h" ] || [ "${OEPN_LUAJIT}" ]; then
        wget -O ${OS_NAME}-${OS_V}-luajit.tar.gz ${download_Url}/soft/lib/luajit/${OS_NAME}-${OS_V}-luajit.tar.gz
        tar -xvf ${OS_NAME}-${OS_V}-luajit.tar.gz
        cd LuaJIT-2.0.4
        make install
        cd ..
        rm -rf LuaJIT-2.0.4
        rm -f ${OS_NAME}-${OS_V}-luajit.tar.gz
        export LUAJIT_LIB=/usr/local/lib
        export LUAJIT_INC=/usr/local/include/${LUAJIT_INC_PATH}/
        ln -sf /usr/local/lib/libluajit-5.1.so.2 /usr/local/lib64/libluajit-5.1.so.2
        LD_SO_CHECK=$(cat /etc/ld.so.conf|grep /usr/local/lib)
        if [ -z "${LD_SO_CHECK}" ];then
             echo "/usr/local/lib" >>/etc/ld.so.conf
        fi
        ldconfig
    fi
}
Install_cjson() {
    if [ ! -f /usr/local/lib/lua/5.1/cjson.so ]; then
        wget -O lua-cjson-2.1.0.tar.gz $download_Url/install/src/lua-cjson-2.1.0.tar.gz -T 20
        tar xvf lua-cjson-2.1.0.tar.gz
        rm -f lua-cjson-2.1.0.tar.gz
        cd lua-cjson-2.1.0
        make
        make install
        cd ..
        rm -rf lua-cjson-2.1.0
    fi
}
Install_Nginx() {
	Run_User="www"
    wwwUser=$(cat /etc/passwd | grep www)
    if [ "${wwwUser}" == "" ]; then
        groupadd ${Run_User}
        useradd -s /sbin/nologin -g ${Run_User} ${Run_User}
    fi

    # cd /www/server
    # wget -O nginx.tar.gz ${download_Url}/soft/nginx/${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz
    # tar -xvf nginx.tar.gz
    # rm -f nginx.tar.gz
    
    cd /www/server
    rm -f nginx.tar.gz
    wget -O ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz ${download_Url}/soft/nginx/${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz
    wget -O ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum ${download_Url}/soft/nginx/${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum

    if [ -f "${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum" ] && [ -f "/usr/bin/sha256sum" ];then
        sha256sum -c ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum
        if [ "$?" -ne 0 ];then
            wget -O ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz ${download_Url}/soft/nginx/${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz
            sha256sum -c ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum
            if [ "$?" -ne 0 ];then
                wget -O nginx.sh ${download_Url}/install/0/nginx.sh && sh nginx.sh install $version
                exit 0
            fi
        fi
    fi
    rm -f ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz.256sum
    mv ${OS_NAME}-${OS_V}-nginx-$nginxVersion.tar.gz nginx.tar.gz
    tar -xvf nginx.tar.gz
    if [ "$?" -ne 0 ];then
        wget -O nginx.sh ${download_Url}/install/0/nginx.sh && sh nginx.sh install $version
        exit 0
    fi
    rm -f nginx.tar.gz

    # if [ ! -f "/www/server/nginx/sbin/nginx" ];then
    #     GetSysInfo
    #     echo -e "安装失败，请截图以上报错信息发帖至论坛www.bt.cn/bbs求助"
    #     exit 1
    # fi

    /www/server/nginx/sbin/nginx -V > /dev/null  2>&1
    if [ "$?" -ne 0 ];then
        wget -O nginx.sh ${download_Url}/install/0/nginx.sh && sh nginx.sh install $version
        exit 0
    fi

    \cp -rpa ${Setup_Path}/sbin/nginx /www/backup/nginxBak
	chmod -x /www/backup/nginxBak
	md5sum ${Setup_Path}/sbin/nginx > /www/server/panel/data/nginx_md5.pl
	ln -sf ${Setup_Path}/sbin/nginx /usr/bin/nginx
    rm -f ${Setup_Path}/conf/nginx.conf

    cd ${Setup_Path}
    rm -f src.tar.gz
}
Set_Conf() {
    Default_Website_Dir=$Root_Path'/wwwroot/default'
    mkdir -p ${Default_Website_Dir}
    mkdir -p ${Root_Path}/wwwlogs
    mkdir -p ${Setup_Path}/conf/vhost
    mkdir -p /usr/local/nginx/logs
    mkdir -p ${Setup_Path}/conf/rewrite

    mkdir -p /www/wwwlogs/load_balancing/tcp
    mkdir -p /www/server/panel/vhost/nginx/tcp

    wget -O ${Setup_Path}/conf/nginx.conf ${download_Url}/conf/nginx1.conf -T20
    wget -O ${Setup_Path}/conf/pathinfo.conf ${download_Url}/conf/pathinfo.conf -T20
    wget -O ${Setup_Path}/conf/enable-php.conf ${download_Url}/conf/enable-php.conf -T20
    wget -O ${Setup_Path}/html/index.html ${download_Url}/error/index.html -T 20

    chmod 755 /www/server/nginx/
    chmod 755 /www/server/nginx/html/
    chmod 755 /www/wwwroot/
    chmod 644 /www/server/nginx/html/*

    cat >${Root_Path}/server/panel/vhost/nginx/phpfpm_status.conf <<EOF
server {
    listen 80;
    server_name 127.0.0.1;
    allow 127.0.0.1;
    location /nginx_status {
        stub_status on;
        access_log off;
    }
EOF
    echo "" >/www/server/nginx/conf/enable-php-00.conf
    for phpV in 52 53 54 55 56 70 71 72 73 74 75 80 81 82 83 84; do
        cat >${Setup_Path}/conf/enable-php-${phpV}.conf <<EOF
    location ~ [^/]\.php(/|$)
    {
        try_files \$uri =404;
        fastcgi_pass  unix:/tmp/php-cgi-${phpV}.sock;
        fastcgi_index index.php;
        include fastcgi.conf;
        include pathinfo.conf;
    }
EOF
        cat >>${Root_Path}/server/panel/vhost/nginx/phpfpm_status.conf <<EOF
    location /phpfpm_${phpV}_status {
        fastcgi_pass unix:/tmp/php-cgi-${phpV}.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$fastcgi_script_name;
    }
EOF
    done
    echo \} >>${Root_Path}/server/panel/vhost/nginx/phpfpm_status.conf

    cat >${Setup_Path}/conf/proxy.conf <<EOF
proxy_temp_path ${Setup_Path}/proxy_temp_dir;
proxy_cache_path ${Setup_Path}/proxy_cache_dir levels=1:2 keys_zone=cache_one:20m inactive=1d max_size=5g;
client_body_buffer_size 512k;
proxy_connect_timeout 60;
proxy_read_timeout 60;
proxy_send_timeout 60;
proxy_buffer_size 32k;
proxy_buffers 4 64k;
proxy_busy_buffers_size 128k;
proxy_temp_file_write_size 128k;
proxy_next_upstream error timeout invalid_header http_500 http_503 http_404;
proxy_cache cache_one;
EOF

    cat >${Setup_Path}/conf/luawaf.conf <<EOF
lua_shared_dict limit 10m;
lua_package_path "/www/server/nginx/waf/?.lua";
init_by_lua_file  /www/server/nginx/waf/init.lua;
access_by_lua_file /www/server/nginx/waf/waf.lua;
EOF

    cat >${Root_Path}/server/panel/vhost/nginx/waf2monitor_data.conf <<EOF
map \$http_host \$waf2monitor_blocked {
    default  "";
}
map \$remote_addr \$waf_ip_remote_addr {
    default  "";
}
map \$http_host \$waf_status_infos {
    default  "";
}
EOF

    mkdir -p /www/wwwlogs/waf
    chown www.www /www/wwwlogs/waf
    chmod 744 /www/wwwlogs/waf
    mkdir -p /www/server/panel/vhost
    #wget -O waf.zip ${download_Url}/install/waf/waf.zip
    #unzip -o waf.zip -d $Setup_Path/ >/dev/null
    if [ ! -d "/www/server/panel/vhost/wafconf" ]; then
        mv $Setup_Path/waf/wafconf /www/server/panel/vhost/wafconf
    fi

    sed -i "s#include vhost/\*.conf;#include /www/server/panel/vhost/nginx/\*.conf;#" ${Setup_Path}/conf/nginx.conf
    sed -i "s#/www/wwwroot/default#/www/server/phpmyadmin#" ${Setup_Path}/conf/nginx.conf
    sed -i "/pathinfo/d" ${Setup_Path}/conf/enable-php.conf
    sed -i "s/#limit_conn_zone.*/limit_conn_zone \$binary_remote_addr zone=perip:10m;\n\tlimit_conn_zone \$server_name zone=perserver:10m;/" ${Setup_Path}/conf/nginx.conf
    sed -i "s/mime.types;/mime.types;\n\t\tinclude proxy.conf;\n/" ${Setup_Path}/conf/nginx.conf
    #if [ "${nginx_version}" == "1.12.2" ] || [ "${nginx_version}" == "openresty" ] || [ "${nginx_version}" == "1.14.2" ];then
    sed -i "s/mime.types;/mime.types;\n\t\t#include luawaf.conf;\n/" ${Setup_Path}/conf/nginx.conf
    #fi

    PHPVersion=""
    for phpVer in 52 53 54 55 56 70 71 72 73 74 80 81 82 83; do
        if [ -d "/www/server/php/${phpVer}/bin" ]; then
            PHPVersion=${phpVer}
        fi
    done

    if [ "${PHPVersion}" ]; then
        \cp -r -a ${Setup_Path}/conf/enable-php-${PHPVersion}.conf ${Setup_Path}/conf/enable-php.conf
    fi
    
    if [ ! -f "/www/server/nginx/conf/enable-php.conf" ];then
        touch /www/server/nginx/conf/enable-php.conf
    fi

    AA_PANEL_CHECK=$(cat /www/server/panel/config/config.json | grep "English")
    if [ "${AA_PANEL_CHECK}" ]; then
        #\cp -rf /www/server/panel/data/empty.html /www/server/nginx/html/index.html
        wget -O /www/server/nginx/html/index.html ${download_Url}/error/index_en_nginx.html -T 20
        chmod 644 /www/server/nginx/html/index.html
        wget -O /www/server/panel/vhost/nginx/0.default.conf ${download_Url}/conf/nginx/en.0.default.conf
        for phpV in 52 53 54 55 56 70 71 72 73 74 75 80 81 82 83; do
            wget -O ${Setup_Path}/conf/enable-php-${phpV}-wpfastcgi.conf ${download_Url}/install/wordpress_conf/nginx/enable-php-${phpV}-wpfastcgi.conf
        done
    fi
    
    wget -O /etc/init.d/nginx ${download_Url}/init/nginx.init -T 20

    if [ "${version}" == "1.23" ] || [ "${version}" == "1.24" ] || [ "${version}" == "tengine" ] || [ "${version}" == "1.25" ] ||  [ "${version}" == "1.26" ]  || [ "${version}" == "1.27" ] || [ "${version}" == "1.28" ];then
        if [ -d "/www/server/btwaf" ];then
            rm -rf /www/server/btwaf/ngx
            rm -rf /www/server/btwaf/resty
            \cp -rpa /www/server/nginx/lib/lua/* /www/server/btwaf
        elif [ -d "/www/server/free_waf" ];then
            rm -rf /www/server/btwaf/ngx
            rm -rf /www/server/btwaf/resty
            \cp -rpa /www/server/nginx/lib/lua/* /www/server/free_waf
        else
            sed -i "/lua_package_path/d" /www/server/nginx/conf/nginx.conf
            sed -i '/include proxy\.conf;/a \        lua_package_path "/www/server/nginx/lib/lua/?.lua;;";' /www/server/nginx/conf/nginx.conf
        fi
        wget -O /etc/init.d/nginx ${download_Url}/init/124nginx.init -T 20
    fi

    HTTP3_CHECK=$(nginx -V 2>&1|grep http_v3)
    if [ -z "${HTTP3_CHECK}" ];then
        QUIC_CHECK=$(grep quic /www/server/panel/vhost/nginx/*.conf)
        if [ "${QUIC_CHECK}" ];then
            sed -i "/listen 443 quic/d" /www/server/panel/vhost/nginx/*.conf
            sed -i "/quic=/d" /www/server/panel/vhost/nginx/*.conf
            sed -i "/http2 on/d" /www/server/panel/vhost/nginx/*.conf
        fi
    fi


    chmod +x /etc/init.d/nginx
}
Set_Version() {
    if [ "${version}" == "tengine" ]; then
        echo "-Tengine2.2.3" >${Setup_Path}/version.pl
        echo "2.2.4(${tengine})" >${Setup_Path}/version_check.pl
    elif [ "${version}" == "openresty" ]; then
        echo "openresty" >${Setup_Path}/version.pl
        echo "openresty-${openresty}" >${Setup_Path}/version_check.pl
    else
        echo "${nginxVersion}" >${Setup_Path}/version.pl
    fi

    if [ "${GMSSL}" ]; then
        echo "1.18国密版" >${Setup_Path}/version_check.pl
    fi
}

Uninstall_Nginx() {
    if [ -f "/etc/init.d/nginx" ]; then
        Service_Del
        /etc/init.d/nginx stop
        rm -f /etc/init.d/nginx
    fi
    [ -f "${Setup_Path}/rpm.pl" ] && yum remove bt-$(cat ${Setup_Path}/rpm.pl) -y
    [ -f "${Setup_Path}/deb.pl" ] && apt-get remove bt-$(cat ${Setup_Path}/deb.pl) -y
    pkill -9 nginx
    rm -rf ${Setup_Path}
    rm -rf /www/server/btwaf/ngx
    rm -rf /www/server/btwaf/resty
    rm -rf /www/server/btwaf/librestysignal.so
    rm -rf /www/server/btwaf/rds
    rm -rf /www/server/btwaf/redis
    rm -rf /www/server/btwaf/tablepool.lua
}

actionType=$1
version=$2

if [ "${actionType}" == "uninstall" ]; then
    Service_Del
    Uninstall_Nginx
else
    case "${version}" in
    '1.10')
        nginxVersion=${nginx_112}
        ;;
    '1.12')
        nginxVersion=${nginx_112}
        ;;
    '1.14')
        nginxVersion=${nginx_114}
        ;;
    '1.15')
        nginxVersion=${nginx_115}
        ;;
    '1.16')
        nginxVersion=${nginx_116}
        ;;
    '1.17')
        nginxVersion=${nginx_117}
        ;;
    '1.18')
        nginxVersion=${nginx_118}
        ;;
    '1.18.gmssl')
        nginxVersion=${nginx_118}
        GMSSL="True"
        ;;
    '1.19')
        nginxVersion=${nginx_119}
        ;;
    '1.20')
        nginxVersion=${nginx_120}
        ;;
    '1.21')
        nginxVersion=${nginx_121}
        ;;
    '1.22')
        nginxVersion=${nginx_122}
        ;;
    '1.23')
        nginxVersion=${nginx_123}
        ;;
    '1.24')
        nginxVersion=${nginx_124}
        ;;
    '1.25')
        nginxVersion=${nginx_125}
        ;;
    '1.26')
        nginxVersion=${nginx_126}
        ;;
    '1.27')
        nginxVersion=${nginx_127}
        ;;
    '1.28')
        nginxVersion=${nginx_128}
        ;;
    '1.8')
        nginxVersion=${nginx_108}
        ;;
    'openresty')
        nginxVersion=${openresty}
        ;;
    *)
        nginxVersion=${tengine}
        version="tengine"
        ;;
    esac
    if [ "${actionType}" == "install" ]; then
        Get_Sys_Version
        if [ -f "/www/server/nginx/sbin/nginx" ]; then
            Uninstall_Nginx
        fi
        Ready_Check
        System_Lib
        if [ -z "${ARM_CHECK}" ]; then
            Install_Jemalloc
            Install_LuaJIT
            Install_cjson
        fi
        Install_Nginx
        Set_Conf
        Set_Version
        Service_Add
        /etc/init.d/nginx start
        if [ -f "/usr/bin/sqlite3" ] && [ -f "/www/server/panel/install/ins_lib.pl" ];then
            sqlite3 /www/server/panel/data/db/task.db "DELETE FROM tasks WHERE name = '安装必要环境库';"
            rm -f /www/server/panel/install/ins_lib.pl
        fi

        # echo "安装基础网站流量统计程序..."
        # wget -O site_new_total.sh ${download_Url}/site_total/install.sh &> /dev/null 
        # bash site_new_total.sh &> /dev/null
        # rm -f site_new_total.sh
        # echo "安装基础网站流量统计程序完成"
        
        #免费试用网站监控报表
        # if [ ! -f "/www/server/panel/plugin/monitor/info.json" ] && [ -f "/usr/bin/btpython" ];then
        #     if [ -z "${AA_PANEL_CHECK}" ];then
        #         cd /www/server/panel/install
        #         wget -O plugin_install.py ${download_Url}/tools/plugin_install.py -T 20
        #         nohup /usr/bin/btpython plugin_install.py monitor 4.1.2 >/dev/null 2>&1 &
        #     fi
        # fi

    elif [ "${actionType}" == "update" ]; then
        Download_Src
        Install_Configure
        Update_Nginx
    fi
fi

