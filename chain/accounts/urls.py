from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.signup,name='signup'),
    path('clientsignup/', views.clientsignup, name='clientsignup'),
    path('userdashboard/',views.dashboard,name='dashboard'),
    path('clientdashboard/', views.clientdashboard, name='clientdashboard'),
    path('signin/',views.signin,name='signin'),
    path('signout/', views.signout, name='logout'),
    path('portfolio/',views.portfoliodashboard,name='portfolio'),
    path('editporfolioitem/', views.editporfolioitem, name='editportfolioitem'),
    path('jobs/', views.jobdashboard, name='jobdashboard'),
    path('viewuploadedjobs/', views.viewjobs, name='viewjobs'),
    path('viewbids/', views.viewbids, name='viewbids'),
    path('submitbid/<str:id>', views.submitbid, name='submitbid'),
    path('acceptbid/<str:id>', views.acceptbid, name='acceptbid'),
    path('rejectbid/<str:id>', views.rejectbid, name='rejectbid'),
    path('deletejob/<str:id>', views.deletejob, name='deletejob'),
    path('editprofile/', views.editprofile, name='editprofile'),
    #path('projects/', views.ProjectApiView),
    path('projects/<str:pk>', views.Projectupdate.as_view()),
    path('bio/<str:pk>', views.Bioupdate.as_view()),
    path('Bios/', views.BioApiView),
    path('bids/', views.BidApiView),
    path('updatebid/<str:id>', views.UpdateBidApiView),
    path('deleteprofile/', views.deleteprofile, name='deleteprofile'),
    path('deleteitemfromportfolio/<str:id>', views.deleteprofile, name='deletefromportfolio'),
]