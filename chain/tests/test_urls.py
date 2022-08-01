from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.contrib import auth
from django.urls import resolve,reverse
from accounts.views import signin
from accounts.models import Subscription
from courses.views import businessdirect

"""class TestUrl(TestCase):
    def test_if_url_is_resolved(self):
        url = reverse('signin')
        self.assertEquals(resolve(url).func,signin)
"""

class TestViews(TestCase):
    def test_if_coursesview_is_resolved(self):
        myclient = Client()
        response = myclient.post(reverse('businessdirect'),{'business':'business'})
        self.assertEquals(response.status_code,200)
        self.assertTemplateUsed(response,'courses/courses-list.html')

    def test_if_signupview_is_resolved(self):
        myclient = Client()
        user = User.objects.create_user(username= 'opeoluwa@gmail.com',password='akerele')
        user.save()
        sub = Subscription(user=user,role='customer')
        sub.save()
        response = myclient.post(reverse('Signin'), {'email': 'opeoluwa@gmail.com', 'password':'akerele'})
        self.assertEquals(response.status_code, 302)
