from django.forms import ModelForm


def create_dynamic_model_form(admin_class, form_add=False):
    """动态的生成modelform
    form_add: False 默认是修改表单, True为添加
    """

    class Meta:
        model = admin_class.model
        fields = '__all__'
        if not form_add:  # change
            exclude = admin_class.readonly_fields
            admin_class.form_add = False  # 这是因为自始至终admin_class实例都是同一个,
            # 这里修改属性为True是为了避免上一次添加调用将其改为了True
        else:
            # add
            admin_class.form_add = True

    def __new__(cls, *args, **kwargs):

        # cls == dynamic_form
        # cls.base_fields = {'字段名': <字段对象>, ...}
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class': 'form-control'})  # 自定义mdoelform样式

        return ModelForm.__new__(cls)

    # 使用type生成类
    # type第一个参数：类名
    # type第二个参数：当前类的基类
    # type第三个参数：类的成员

    # 先执行meta生成class DynamicModelForm, 再执行__new__！！！
    dynamic_form = type('DynamicModelForm', (ModelForm,), {'Meta': Meta, '__new__': __new__})

    return dynamic_form
