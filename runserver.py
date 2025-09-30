#coding: utf-8
# +-------------------------------------------------------------------
# | aaPanel
# +-------------------------------------------------------------------
# | Copyright (c) 2015-2099 aaPanel(www.aapanel.com) All rights reserved.
# +-------------------------------------------------------------------
# | Author: hwliang <hwl@aapanel.com>
# +-------------------------------------------------------------------
import sys
import os
from os import environ

# Add required paths to sys.path before importing BTPanel
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if os.path.join(current_dir, 'class') not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, 'class'))
if os.path.join(current_dir, 'class_v2') not in sys.path:
    sys.path.insert(0, os.path.join(current_dir, 'class_v2'))

from BTPanel import app
from config_factory import get_config

if __name__ == '__main__':
    # استخدام config factory للحصول على الإعدادات
    config = get_config()
    
    # استخدام HOST و PORT من الإعدادات
    HOST = config.HOST
    PORT = config.PORT
    
    # طباعة معلومات التشغيل
    print(f"=" * 60)
    print(f"🚀 بدء تشغيل aaPanel")
    print(f"=" * 60)
    print(f"البيئة: {config.ENVIRONMENT}")
    print(f"المضيف: {HOST}")
    print(f"المنفذ: {PORT}")
    print(f"وضع التصحيح: {config.DEBUG if hasattr(config, 'DEBUG') else 'غير محدد'}")
    print(f"=" * 60)
    
    # تشغيل التطبيق
    app.run(host=HOST, port=PORT)
