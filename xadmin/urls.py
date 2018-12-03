

from django.conf.urls import url, include
from xadmin import views

urlpatterns = [
    url(r'^$', views.app_index),
    url(r'^(\w+)/$', views.app_table_list, name='app_table_list'),
    url(r'^(\w+)/(\w+)/$', views.table_obj_list, name='table_obj_list'),
    url(r'^(\w+)/(\w+)/(\d+)/change/$', views.table_obj_change, name='table_obj_change'),
    url(r'^(\w+)/(\w+)/(\d+)/delete/$', views.table_obj_delete, name='object_delete'),
    url(r'^(\w+)/(\w+)/add/$', views.table_obj_add, name='table_obj_add'),
    url(r'^login/', views.acc_login),
    url(r'^logout/', views.acc_logout, name='xadmin_logout'),
]
