#!/bin/bash
PATH=/www/server/panel/pyenv/bin:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH
export HOME=/root
install_tmp='/tmp/bt_install.pl'
install_path=/www/server/panel/plugin/pgsql_manager

#安装
Install()
{
	
	echo 'Installing...'
	#==================================================================
	#打包插件目录上传的情况下
	#依赖安装开始
	#pip install psycopg2

	#依赖安装结束
	#==================================================================

	#==================================================================
	#使用命令行安装的情况下，如果使用面板导入的，请删除以下代码
	
	#创建插件目录


	#文件下载结束
	#==================================================================
	if [ -e /www/server/pgsql/data_directory ]; then
    cat /www/server/pgsql/data_directory
    else
        mkdir -p /www/server/pgsql/
        echo "/www/server/pgsql/data" >/www/server/pgsql/data_directory
    fi

	\cp -a -r $install_path/pgsql.sh /etc/init.d/pgsql
	chmod +x /etc/init.d/pgsql
  if [ -f "/usr/bin/systemd" ];then
    systemctl enable pgsql
  elif [ -f "/usr/bin/apt-get" ];then
    update-rc.d pgsql defaults
  else
    chkconfig --add pgsql
    chkconfig pgsql on
  fi
	echo '================================================'
	echo 'The installation is complete'
}

#卸载
Uninstall()
{
	rm -rf $install_path
	if [ -f "/usr/bin/systemd" ];then
    systemctl disable pgsql
  elif [ -f "/usr/bin/apt-get" ];then
    update-rc.d pgsql remove
  else
    chkconfig pgsql off
  fi
}

#操作判断
if [ "${1}" == 'install' ];then
	Install
elif [ "${1}" == 'uninstall' ];then
	Uninstall
else
	echo 'Error!';
fi

