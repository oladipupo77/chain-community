from django.db import models
from django.contrib.auth.models import User

class Bio(models.Model):
    name = models.CharField(max_length=35)
    bio = models.CharField(max_length=90, default='null', null=True)
    image = models.ImageField(upload_to='images/', default='images/home-profile.jpg', null=True)
    phone = models.IntegerField()
    profile_views = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    github = models.CharField(max_length=75, default='null')
    linkedin = models.CharField(max_length=75, default='null')
    stack = models.CharField(max_length=15,default='web developer')
    role = models.CharField(max_length=15,default='developer')

    def __str__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100,default='no description')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='client')
    developer = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True, related_name='developer')
    uploaded = models.DateTimeField(null=True)
    price = models.IntegerField(null=False,default=1000)
    category = models.CharField(max_length=50,default='Web Design')
    stack = models.CharField(max_length=50, default='Django')

    def __str__(self):
        return self.name

class Portfolio(models.Model):
    name = models.CharField(max_length=100,blank=True,null=True)
    description = models.CharField(max_length=100, default='no description')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='user')
    github = models.CharField(max_length=75, default='null')
    uploaded = models.DateTimeField()
    stacks_used = models.CharField(max_length=75, default='null', null=True )

    def __str__(self):
        return self.name

class Bid(models.Model):
    job = models.ForeignKey(Project, on_delete=models.CASCADE, null=False)
    BidSentBy = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=15, default='pending')
    def __str__(self):
        return self.job.name


class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action = models.CharField(max_length=35)