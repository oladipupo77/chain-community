from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.blogpage,name='blog'),
    path('anon/', views.anon,name='anon'),
    path('blogpost/<str:id>', views.blogpost,name='blogpost'),
    path('anonymouspost/<str:id>', views.anonpost, name='anonpost'),
    path('postcomment/', views.postcomment,name='postcomment'),
    path('postquestion/', views.postquestion, name='postquestion'),
    path('filter/<str:category>', views.filter, name='filter'),
    path('agree/<str:id>', views.agree, name='agree'),
]