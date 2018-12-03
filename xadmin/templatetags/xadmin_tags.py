from django.template import Library
from django.utils.safestring import mark_safe
import datetime

register = Library()


@register.simple_tag
def build_table_row(obj, admin_class):
    """生成一条记录的html element"""
    ele = ''
    if admin_class.list_display:
        for index, column in enumerate(admin_class.list_display):
            field_obj = admin_class.model._meta.get_field(column)   # 拿到字段对象
            if field_obj.choices:   # 判断字段是否是choices类型
                column_data = getattr(obj, 'get_%s_display' % column)()  # 获取choices别名 , get_field_display
            else:
                column_data = getattr(obj, column)
            td_ele = '<td>%s</td>' % column_data
            if index == 0:
                td_ele = '<td><a href="%s/change/">%s</a></td>' % (obj.id, column_data)
            ele += td_ele
    else:   # 未注册admin
        td_ele = '<td><a href=%s/change/>%s</a></td>' % (obj.id, obj)   # 默认返回obj的__str__
        ele += td_ele
    return mark_safe(ele)


@register.simple_tag
def build_filter_ele(filter_column, admin_class):
    column_obj = admin_class.model._meta.get_field(filter_column)
    try:
        filter_ele = '<select class="form-control" name=%s>' % filter_column
        # fileds_obj.get_choices() 生成下拉菜单, date类型会报错
        # [('', '---------'), (0, '未报名'), (1, '已报名'), (2, '已退学')]
        for choice in column_obj.get_choices():
            selected = ''
            # 显示选中的过滤条件, select的name与option的value组成过滤条件
            if filter_column in admin_class.filter_conditions:  # 当前字段被过滤了
                # filter_condtions = {'date__gte': '2018-11-1', 'consultant': '4', 'status': '0'}

                if str(choice[0]) == admin_class.filter_conditions.get(filter_column):  # 当前值被选中了
                    selected = 'selected'

            option = '<option value=%s %s>%s</option>' % (choice[0], selected, choice[1])
            filter_ele += option
    except AttributeError:
        # models.CustomerInfo.objects.filter(date__gte='2016-11-17')
        filter_ele = '<select class="form-control" name=%s__gte>' % filter_column
        if column_obj.get_internal_type() in ('DateField', 'DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [
                ['', '------'],
                [time_obj, 'Today'],
                [time_obj - datetime.timedelta(7), '七天内'],
                [time_obj.replace(day=1), '本月'],    # 替换
                [time_obj - datetime.timedelta(90), '三个月内'],
                [time_obj.replace(month=1, day=1), 'YearToDay(YTD)'],
                ['', 'ALL'],
            ]

            for i in time_list:
                selected = ''
                time_to_str = '' if not i[0] else '%s-%s-%s' % (i[0].year, i[0].month, i[0].day)  # 三元运算
                if '%s__gte' % filter_column in admin_class.filter_conditions:  # 当前字段被过滤了
                    if time_to_str == admin_class.filter_conditions.get('%s__gte' % filter_column):  # 当前值被选中了
                        selected = 'selected'
                option = '<option value=%s %s>%s</option>' % (time_to_str, selected, i[1])
                filter_ele += option

    filter_ele += "</select>"
    return mark_safe(filter_ele)


@register.simple_tag
def get_app_tables(site, app_name):
    return site.enabled_admins[app_name]


@register.simple_tag
def get_model_name(admin_class):
    # return admin_class.model._meta.model_name.upper()
    return admin_class.model._meta.model_name


@register.simple_tag
def get_app_name(admin_class):
    # return admin_class.model._meta.model_name.upper()
    return admin_class.model._meta.app_label


@register.simple_tag
def render_paginator(querysets, admin_class, sorted_column):
    ele = '<ul class="pagination">'

    # if querysets.has_previous:
    #     print('querysets.previous_page_number-----', querysets.previous_page_number)
    #     ele += '<li><a href="?_page=%s">上一页</a></li>' % querysets.previous_page_number

    for i in querysets.paginator.page_range:  # 轮循每一页
        if abs(querysets.number - i) < 3:  # 显示前后2页（当前页和每页比较）
            active = ''
            if querysets.number == i:  # current page
                active = 'active'
            filter_ele = render_filter_args(admin_class)

            sorted_ele = ''
            if sorted_column:
                sorted_ele += '&_o=%s' % list(sorted_column.values())[0]
            p_ele = '<li class="%s"><a href="?_page=%s%s%s">%s</a></li>' % (active, i, filter_ele, sorted_ele, i)
            ele += p_ele

    # if querysets.has_next:
    #     ele += '<li><a href="?_page=%s">下一页</a></li>' % querysets.next_page_number

    ele += '</ul>'
    return mark_safe(ele)


@register.simple_tag
def get_sorted_column(column, sorted_column, forloop):
    # sorted_column = {'status': '0'}
    if column in sorted_column:  # 这一列被排序了
        # 判断上一次排序的顺序, 本次取反
        last_sort_index = sorted_column[column]
        if last_sort_index.startswith('-'):
            this_time_sort_index = last_sort_index.strip('-')
        else:
            this_time_sort_index = '-%s' % last_sort_index
        return this_time_sort_index
    else:
        return forloop


@register.simple_tag
def render_sorted_arrow(column, sorted_column):
    if column in sorted_column:  # 这一列被排序了
        last_sort_index = sorted_column[column]
        if last_sort_index.startswith('-'):
            arrow_diretion = 'bottom'
        else:
            arrow_diretion = 'top'
        ele = '<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>' % arrow_diretion
        return mark_safe(ele)
    return ''


@register.simple_tag
def render_filter_args(admin_class, render_html=True):
    """拼接筛选的字段"""
    if admin_class.filter_conditions:
        ele = ''
        for k, v in admin_class.filter_conditions.items():
            ele += '&%s=%s' % (k, v)
        if render_html:
            return mark_safe(ele)
        else:
            return ele
    else:
        return ''


@register.simple_tag
def get_current_sorted_column_index(sorted_column):
    """只有排了序才取"""
    return list(sorted_column.values())[0] if sorted_column else ''


@register.simple_tag
def get_obj_field_value(form_obj, field, admin_class):
    """返回model obj 具体字段的值"""
    field_obj = admin_class.model._meta.get_field(field)
    if field_obj.choices:  # 获取choice字段的值的别名
        return getattr(form_obj.instance, 'get_%s_display' % field)()
    else:
        return getattr(form_obj.instance, field)


@register.simple_tag
def get_available_m2m_data(field_name, form_obj, admin_class):
    """返回m2m字段没有关联的所有数据"""
    field_obj = admin_class.model._meta.get_field(field_name)
    obj_list = set(field_obj.related_model.objects.all())  # 获取相关联的m2m表的所有数据
    if form_obj.instance.id:  # 如果是添加 form_obj为空
        selected_list = set(getattr(form_obj.instance, field_name).all())  # 获取相关联的m2m表的数据
        return obj_list - selected_list  # 差集
    else:
        return obj_list


@register.simple_tag
def get_selected_m2m_data(field_name, form_obj):
    """返回已选的m2m数据"""
    if form_obj.instance.id:  # 如果是添加 form_obj为空
        return getattr(form_obj.instance, field_name).all()
    else:
        return ''


@register.simple_tag
def display_all_related_objs(obj):
    """
    显示要被删除对象的所有关联对象
    :param obj:
    :return:
    """
    ele = "<ul><b style='color:red'>%s</b>" % obj

    for reversed_fk_obj in obj._meta.related_objects:

        related_table_name = reversed_fk_obj.name
        # if reversed_fk_obj.get_internal_type() == 'OneToOneField':
        #     related_lookup_key = "%s" % related_table_name
        #     related_objs = getattr(obj, related_lookup_key)  # 反向查所有关联的数据(one2one)
        # else:
        related_lookup_key = "%s_set" % related_table_name
        related_objs = getattr(obj, related_lookup_key).all()  # 反向查所有关联的数据(fk, m2m)
        ele += "<li>%s3333<ul> " % related_table_name

        if reversed_fk_obj.get_internal_type() == "ManyToManyField":  # 不需要深入查找
            for i in related_objs:
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a> 记录里与[%s]相关的的数据将被删除</li>" \
                       % (i._meta.app_label, i._meta.model_name, i.id, i, obj)
        else:
            for i in related_objs:
                # ele += "<li>%s--</li>" %i
                ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a></li>" % (i._meta.app_label,
                                                                                  i._meta.model_name,
                                                                                  i.id, i)
                ele += display_all_related_objs(i)

        ele += "</ul></li>"

    ele += "</ul>"

    return ele
