from xadmin.admin_base import BaseXAdmin


class AdminSite(object):
    def __init__(self):
        self.enabled_admins = {}

    def register(self, model_class, admin_class=None):
        """注册admin表"""
        # note:
        #   model_class = Customer
        #   model_name = customer
        #   admin_class = CustomerAdmin

        app_name = model_class._meta.app_label
        model_name = model_class._meta.model_name  # 小写表名

        # 实例化 避免多个model共享同一个BaseKingAdmin内存对象
        # 问题???： 不同的内存地址还是共用一个actions
        if not admin_class:
            admin_class = BaseXAdmin()
            print('BaseXAdmin------', id(admin_class), id(admin_class.actions))
        else:
            admin_class = admin_class()
            print('admin------', admin_class.actions, id(admin_class), id(admin_class.actions))

        admin_class.model = model_class  # 把model_class赋值给了admin_class
        if app_name not in self.enabled_admins:
            self.enabled_admins[app_name] = {}
        # 将app_name, table_name, admin_class想关联
        self.enabled_admins[app_name][model_name] = admin_class

        # enabled_admins = {
        #     < app_name >: { < table_name >: < admin_class >[model_class], ...}
        #     ...
        # }


site = AdminSite()  # 注意在django中 site只被初始化一次！！！
