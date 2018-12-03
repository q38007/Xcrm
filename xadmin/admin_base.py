from django.shortcuts import render
import json


class BaseXAdmin(object):

    def __init__(self):  # 子类未实现将调用父类
        # self.actions = []   # 问题： actions会被未注册的model class共用, 导致重复添加
        self.actions.extend(self.default_actions)
        # print('self.actions-----', self, self.actions)

    list_display = []
    list_filter = []
    search_fields = []
    readonly_fields = []
    filter_horizontal = []
    list_per_page = 10

    default_actions = ['delete_selected_objs']
    actions = []

    def delete_selected_objs(self, request, querysets):
        querysets_ids = json.dumps([i.id for i in querysets])

        return render(request, 'xadmin/action_delete.html', {'admin_class': self,
                                                             'objs': querysets,
                                                             'querysets_ids': querysets_ids})

