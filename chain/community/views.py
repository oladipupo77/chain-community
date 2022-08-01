from django.shortcuts import render,redirect
import datetime
from .models import *
from django.core.files.storage import FileSystemStorage
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)
def blogpage(request):
    blogposts = Blogpost.objects.filter(type='public')
    return render(request,'blog.html',{'blogposts':blogposts})

@cache_page(60 * 2)
def blogpost(request,id):
    blogpost = Blogpost.objects.get(id=id)
    comments = Comment.objects.filter(blogpost=blogpost)
    return render(request, 'blog-single.html', {'blogpost': blogpost,'comments':comments})

def postcomment(request):
    user = User.objects.get(id=request.user.id)
    post = Blogpost.objects.get(id=request.POST['postid'])
    comment = request.POST['comment']
    newcomment = Comment(user=user,comment=comment,uploaded=datetime.datetime.now(),blogpost=post)
    newcomment.save()
    return blogpost(request,str(request.POST['postid']))

def postquestion(request):
    if request.method == 'POST':
        if request.POST['type'] == 'anon':
            question = request.POST['question']
            title = request.POST['title']
            category = request.POST['category']
            image = request.FILES['image']
            fs = FileSystemStorage()
            doc = fs.save(image.name, image)
            newquestion = Blogpost(title=title,post=question,image=doc,type=request.POST['type'],category=category)
            newquestion.save()
            return redirect('blog')
        else:
            question = request.POST['question']
            title = request.POST['title']
            image = request.POST['image']
            fs = FileSystemStorage()
            doc = fs.save(image.name, image)
            newquestion = Blogpost(title=title, post=question, image=doc, poster=request.user,uploaded = datetime.datetime.now(),type=request.POST['type'])
            newquestion.save()
            return redirect('blog')
    else:
        return render(request,'askquestion.html')

def agree(request,id):
    comment = Comment.objects.get(id=id)
    comment.vote +=1
    comment.save()

@cache_page(60 * 5)
def anon(request):
    blogposts = Blogpost.objects.filter(type='anon')
    return render(request,'blog2.html',{'blogposts':blogposts})

@cache_page(60 * 2)
def anonpost(request,id):
    blogpost = Blogpost.objects.get(id=id)
    comments = Comment.objects.filter(blogpost=blogpost)
    return render(request, 'blog-single2.html', {'blogpost': blogpost, 'comments': comments})

@cache_page(60 * 5)
def filter(request,category):
    posts = Blogpost.objects.filter(category=category)
    return render(request, 'community.html', {'posts': posts})