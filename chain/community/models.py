from django.db import models
from django.contrib.auth.models import User
import datetime

class Testimonial(models.Model):
    developer = models.OneToOneField(User, on_delete=models.CASCADE, null=True,related_name='programmer')
    client = models.OneToOneField(User, on_delete=models.CASCADE, null=True, related_name='customer')
    review = models.CharField(max_length=100)

class Blogpost(models.Model):
    poster = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=35,default='title')
    post = models.CharField(max_length=500)
    category = models.CharField(max_length=35,default='hardware')
    uploaded = models.DateTimeField(default='2022-05-08 17:55:54.349667', blank=True)
    image = models.ImageField(upload_to='images/', default='static/accounts/images/chain.png', null=True)
    type = models.CharField(max_length=10,default='public')


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    blogpost = models.ForeignKey(Blogpost, on_delete=models.CASCADE, null=False, related_name='blogpost')
    uploaded = models.DateTimeField(default='2022-05-08 17:55:54.349667', blank=True)
    comment = models.CharField(max_length=100)
    vote = models.IntegerField(default=0)

class Question(models.Model):
    image = models.ImageField(upload_to='images/', default='images/home-profile.jpg', null=True)
    question = models.CharField(max_length=200)
    title = models.CharField(max_length=50)
