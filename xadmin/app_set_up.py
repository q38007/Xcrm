from django import conf


# 自动导入每个app下的xadmin.py
def auto_discover():
    apps = conf.settings.INSTALLED_APPS  # conf.settings, 动态获取项目settings配置
    for app in apps:
        try:
            # __import__(module)相当于import module
            # __import__(package.module)相当于from package import name, 如果fromlist不传入值, 则返回package

            __import__('%s.xadmin' % app)

        except ImportError:
            pass
