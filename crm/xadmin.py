from xadmin.sites import site
from crm import models
from xadmin.admin_base import BaseXAdmin


class CustomerInfoAdmin(BaseXAdmin):
    # def __init__(self):
    #     super().__init__()

    list_display = ['id', 'name', 'source', 'contact_type', 'contact', 'consultant', 'consult_content', 'status',
                    'date']
    list_filter = ['source', 'consultant', 'status', 'date']
    search_fields = ['contact', 'consultant__name']  # 外键字段用双下划线
    readonly_fields = ['status', 'contact']
    filter_horizontal = ['consult_courses']

    actions = ['change_status', ]  # 函数名

    def change_status(self, request, querysets):
        # 自定制

        # self 实例本身 CustomerAdmin
        # request request请求
        # querysets 所有选中的对象
        querysets.update(status=0)


class CourseRecordAdmin(BaseXAdmin):
    list_display = ['class_grade', 'day_num', 'has_homework']


# 注意site只在被导入的时候初始化一次！！！
# 将app_name, table_name, admin_class想关联
site.register(models.CustomerInfo, CustomerInfoAdmin)
site.register(models.UserProfile)
site.register(models.Role)
site.register(models.Student)
site.register(models.Course)
site.register(models.CustomerFollowUp)
site.register(models.ClassList)
site.register(models.CourseRecord, CourseRecordAdmin)
site.register(models.StudyRecord)
site.register(models.Menus)
site.register(models.Branch)
site.register(models.PaymentRecord)
site.register(models.StudentEnrollment)
site.register(models.ContractTemplate)
