from django.forms import ModelForm
from django import forms
from crm import models


class CustomerForm(ModelForm):
    class Meta:
        model = models.CustomerInfo
        fields = '__all__'
        exclude = ['consult_content', 'status', 'consult_courses']
        readonly_fields = ['contact_type', 'contact', 'consultant', 'referral_from', 'source']

    def __new__(cls, *args, **kwargs):  # 定制样式
        print("__new__", cls, args, kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class': 'form-control'})

            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})  # form表单不会提交disabled字段, 解决: js 在提交前去掉disabled
                # print("--new meta:",cls.Meta)

        # print(cls.Meta.exclude)
        return ModelForm.__new__(cls)

    def clean(self):  # is_valid()触发表单级别验证
        '''form defautl clean method'''

        print("cleaned_dtat:", self.cleaned_data)

        if self.errors:  # 全局错误
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None:  # means this is a change form ,should check the readonly fields
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, field)  # 数据库里的数据
                form_val = self.cleaned_data.get(field)  # 前端提交通过的
                print("filed differ compare:", old_field_val, form_val)
                if old_field_val != form_val:
                    # 字段级别的错误
                    self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ". \
                                   format(**{'value': old_field_val, 'new_value': form_val}))


class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        print("__new__", cls, args, kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class': 'form-control'})
            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
        return ModelForm.__new__(cls)

    class Meta:
        model = models.StudentEnrollment
        # fields = ['name','consultant','status']
        fields = "__all__"
        exclude = ['contract_approved_date']
        readonly_fields = ['contract_agreed', ]

    def clean(self):
        '''form defautl clean method'''
        # print("\033[41;1mrun form defautl clean method...\033[0m",dir(self))
        # print(self.Meta.admin.readonly_fields)
        print("cleaned_dtat:", self.cleaned_data)

        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None:  # means this is a change form ,should check the readonly fields
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance, field)  # 数据库里的数据
                form_val = self.cleaned_data.get(field)
                print("filed differ compare:", old_field_val, form_val)
                if old_field_val != form_val:
                    self.add_error(field, "Readonly Field: field should be '{value}' ,not '{new_value}' ". \
                                   format(**{'value': old_field_val, 'new_value': form_val}))
