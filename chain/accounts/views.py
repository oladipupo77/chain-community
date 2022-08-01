from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib.auth import authenticate
import datetime
from django.core.files.storage import FileSystemStorage
from .models import *
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from rest_framework import status,viewsets,generics
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import  IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django.views.decorators.cache import cache_page
from .serializers import *
from .tasks import *

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        bio = request.POST['bio']
        stack = request.POST['stack']
        phone = request.POST['phone']
        image = request.FILES['image']
        github =  request.POST['github']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            u = User.objects.get(username=email)
            developer = Bio(user=u, name =name,phone=phone,image=doc,github=github,bio=bio,stack=stack)
            developer.save()
            activity = Activity(user=u, action="created profile at " + str(datetime.datetime.now()))
            activity.save()
            auth.login(request, user)
            return redirect('dashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'signup.html', {'mg': mg})
    else:
        return render(request, 'signup.html')

def clientsignup(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        bio = request.POST['bio']
        phone = request.POST['phone']
        image = request.FILES['image']
        fs = FileSystemStorage()
        doc = fs.save(image.name, image)
        if request.POST['password'] == request.POST['password2']:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.save()
            u = User.objects.get(username=email)
            client = Bio(user=u, name =name,phone=phone,image=doc,role='client',bio=bio)
            client.save()
            activity = Activity(user=u, action="created profile at " + str(datetime.datetime.now()))
            activity.save()
            auth.login(request, user)
            return redirect('clientdashboard')
        else:
            mg = 'passwords must match'
            return render(request, 'signup.html', {'mg': mg})
    else:
        return render(request, 'csignup.html')

def signin(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['email'], password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            activity = Activity(user=user,action= "login at"+ str(datetime.datetime.now()))
            activity.save()
            userbio = Bio.objects.get(user=user)
            if userbio.role == 'developer':
                return redirect('dashboard')
            else:
                return redirect('clientdashboard')
        else:
            return render(request, 'signin.html', {'error': 'username or password is incorrect'})
    else:
        return render(request, 'signin.html')

def signout(request):
    user = User.objects.get(username=request.user.get_username())
    auth.logout(request)
    activity = Activity(user=user, action="logout at " + str(datetime.datetime.now()))
    activity.save()
    return redirect('home')

# @cache_page(60 * 5)
def dashboard(request):
    u = User.objects.get(username=request.user.get_username())
    bio = Bio.objects.get(user=u)
    #bio.profile_views += 1
    #bio.save()
    acceptedbids = Bid.objects.filter(BidSentBy=u, status='accepted')
    pendingbids = Bid.objects.filter(BidSentBy=u, status='pending')
    project = Project.objects.filter(uploaded_by=u)
    activities = Activity.objects.filter(user=u)
    portfolio = Portfolio.objects.filter(uploaded_by=u)
    return render(request, 'dev-home.html', {'bio': bio, 'project': project, 'portfolio': portfolio ,
                                             'acceptedbids':acceptedbids, 'pendingbids':pendingbids, 'activities':activities})


def clientdashboard(request):
    u = User.objects.get(username=request.user.get_username())
    activities = Activity.objects.filter(user=u)
    bio = Bio.objects.get(user=u)
    projects = Project.objects.filter(uploaded_by=u)
    totalbids = []
    pendingbids = []
    acceptedbids = []
    for project in projects:
        if Bid.objects.filter(job=project,status='pending'):
            pendingbids += Bid.objects.filter(job=project)
        elif Bid.objects.filter(job=project,status='accepted'):
            acceptedbids += Bid.objects.filter(job=project)
    return render(request, 'client-home.html', {'bio': bio, 'projects': projects, 'totalbids': totalbids, 'pendingbids': len(pendingbids), 'acceptedbids': len(acceptedbids), 'activities':activities})


def viewbids(request):
    u = User.objects.get(username=request.user.get_username())
    projects = Project.objects.filter(uploaded_by=u)
    pendingbids = []
    acceptedbids = []
    for project in projects:
        if Bid.objects.filter(job=project, status='pending'):
            pendingbids += Bid.objects.filter(job=project)
        elif Bid.objects.filter(job=project, status='accepted'):
            acceptedbids += Bid.objects.filter(job=project)

    acceptedbidscount = len(acceptedbids)
    pendingbidscount = len(pendingbids)
    totalbidscount = len(acceptedbids) + len(pendingbids)
    return render(request, 'client-bids-dashboard.html',{'projects': projects, 'pendingbids': pendingbids, 'acceptedbids': acceptedbids,'totalbidscount':totalbidscount,'pendingbidscount':pendingbidscount,'acceptedbidscount':acceptedbidscount})

@cache_page(60 * 5)
def viewjobs(request):
    if request.method == 'POST':
        title = request.POST['title']
        category = request.POST['jobcategory']
        description = request.POST['description']
        uploaded = request.POST['uploaded']
        id = request.POST['id']
        Project.objects.get(id=id).update(name=title,category=category,description=description,uploaded=uploaded)
        return redirect('viewjobs')
    else:
        u = User.objects.get(username=request.user.get_username())
        jobs = Project.objects.filter(uploaded_by=u)
        return render(request, 'uploadjob.html', {'jobs': jobs})

def uploadjob(request):
    u = User.objects.get(username=request.user.get_username())
    title = request.POST['title']
    category = request.POST['category']
    stack = request.POST['stack']
    price = request.POST['price']
    description = request.POST['description']
    uploaded = datetime.datetime.now()
    project = Project(uploaded_by=u,name=title,description=description,uploaded=uploaded,category=category,price=price,stack=stack)
    project.save()
    return redirect('viewjobs')

def deletejob(request,id):
    job = Project.objects.get(id=id)
    job.delete()
    return redirect('clientdashboard')

def deletefromportfolio(request,id):
    item = Portfolio.objects.get(id=id)
    item.delete()
    return redirect('dashboard')

def editprofile(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        phone = request.POST['phone']
        image = request.FILES['image']
        github = request.POST['github']
        u = User.objects.get(username=request.user.get_username())
        u.set_password(password)
        u.email = email
        u.save()
        Bio.objects.get(user=u).update(name =name,phone=phone,image=image,github=github)
        activity = Activity(user=u, action="edited profile at" + str(datetime.datetime.now()))
        activity.save()
        return redirect('dashboard')
    else:
        return render(request, 'user-profile.html')

@cache_page(60 * 5)
def portfoliodashboard(request):
    if request.method == 'POST':
        name = request.POST['name']
        github = request.POST['github']
        stacks = request.POST['stack']
        date = datetime.datetime.now()
        u = User.objects.get(username=request.user.get_username())
        project = Portfolio(name=name,uploaded_by=u,github=github,uploaded=date,stacks_used=stacks)
        project.save()
        return redirect('dashboard')
    else:
        u = User.objects.get(username=request.user.get_username())
        portfolio = Portfolio.objects.filter(uploaded_by=u)
        return render(request, 'portfoliodashboard.html',{'portfolio':portfolio})

def editporfolioitem(request):
    name = request.POST['name']
    github = request.POST['github']
    stacks = request.POST['stack']
    description = request.POST['description']
    uploaded = request.POST['uploaded']
    id = request.POST['id']
    Portfolio.objects.get(id=id).update(name=name,github=github,stacks_used=stacks,description=description,uploaded=uploaded)
    return redirect('portfolio')

@cache_page(60 * 5)
def jobdashboard(request):
    u = User.objects.get(username=request.user.get_username())
    userbio = Bio.objects.get(user=u)
    totalbids = Bid.objects.filter(BidSentBy=u).count()
    acceptedbids = Bid.objects.filter(BidSentBy=u, status='accepted')
    projects = Project.objects.filter(stack=userbio.stack)
    return render(request, 'project.html', {'projects':projects, 'totalbids':totalbids,  'acceptedbids':acceptedbids})

def submitbid(request,id):
    bidder = request.user.get_username()
    user = User.objects.get(username=bidder)
    project = Project.objects.get(id=id)
    bid = Bid(job=project,BidSentBy=user)
    bid.save()
    return redirect('viewbids')

def acceptbid(request,id):
    bid = Bid.objects.get(id=id)
    job = bid.job
    job.developer = bid.BidSentBy
    job.save()
    bid.status = 'accepted'
    bid.save()
    send_email.delay(job.developer.email,bid)
    for b in Bid.objects.filter(job=job):
        b.delete()
    return redirect('viewbids')

def rejectbid(request,id):
    bid = Bid.objects.get(id=id)
    bid.delete()
    return redirect('viewbids')

def project_details(request,id):
    project = Project.objects.get(id=id)
    return render(request, 'project-details.html', {'project':project})

def delete_from_portolio(request,id):
    item = Portfolio.objects.get(id=id)
    item.delete()
    return redirect('portfolio')

def deleteprofile(request):
    u = request.user.get_username()
    user = User.objects.get(username = u)
    user.delete()
    return redirect('home')


# basic function API for viewing existing users' Bio's or adding a new user Bio
@api_view(['GET','POST'])
def BioApiView(request):
    if request.method =='GET':
        allbios = Bio.objects.all()
        serializer = BioSerializer(allbios,many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            user = User.objects.get(username=request.data['uploaded_by'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# basic function API for viewing existing uploaded jobs or adding a new job
@api_view(['GET','POST'])
def ProjectApiView(request):
    if request.method == 'GET':
        allprojects = Project.objects.all()
        serializer = ProjectSerializer(allprojects,many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            client = User.objects.get(username=request.data['uploaded_by'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=client)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

#APIVIEW Project API to create,update and delete projects/jobs
class ProjectAPI(APIView):
    def get(self, request):
        allprojects = Project.objects.all()
        serializer = ProjectSerializer(allprojects, many=True)
        return Response(serializer.data)

    def post(self,request):
        try:
            client = User.objects.get(username=request.data['uploaded_by'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=client)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

#Create New Project/Job API
class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        if self.request.data['developer'] == '':
            user = User.objects.get(username=self.request.data['uploaded_by'])
            serializer.save(uploaded_by=user,developer=None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

#Update Project/Job API
class Projectupdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    def perform_create(self, serializer):
        if self.request.data['developer'] == '':
            user = User.objects.get(username=self.request.data['uploaded_by'])
            serializer.save(uploaded_by=user,developer=None)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

#Create new bio API
class BioList(generics.ListCreateAPIView):
    queryset = Bio.objects.all()
    serializer_class = BioSerializer
    def perform_create(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['user'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#Update User Bio API
class Bioupdate(generics.RetrieveUpdateAPIView):
    queryset = Bio.objects.all()
    serializer_class = BioSerializer
    def perform_update(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['user'])
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer.save(user=user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#New Bid API
class BidList(generics.ListCreateAPIView):
    queryset = Bid.objects.all()
    serializer_class = BidSerializer
    def perform_create(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['BidSentBy'])
            job = Project.objects.get(name=self.request.data['job'])
        except User.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer.save(BidSentBy=user,job=job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#Update Bid API
class Bidupdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Bid.objects.all()
    serializer_class = BioSerializer
    def perform_create(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['BidSentBy'])
            job = Project.objects.get(name=self.request.data['job'])
        except User.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer.save(BidSentBy=user,job=job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    def perform_update(self, serializer):
        try:
            user = User.objects.get(username=self.request.data['BidSentBy'])
            job = Project.objects.get(name=self.request.data['job'])
        except User.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer.save(BidSentBy=user,job=job)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

#Bid decision API
class Biddecision(generics.RetrieveUpdateAPIView):
    queryset = Bid.objects.all()
    serializer_class = DecideBidSerializer

# basic function API for getting/deleting specific Bio objects or updating data for a specific Bio object
@api_view(['GET','PUT','DELETE'])
def UpdateBioApiView(request,id):
    try:
        user = User.objects.get(id=id)
        bio = Bio.objects.get(user=user)
    except User.DoesNotExist or Bio.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BioSerializer(bio)
        return Response(serializer.data,status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BioSerializer(bio,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        bio.delete()
        return Response(status=status.HTTP_410_GONE)

# basic function API for getting/deleting specific Project objects  uploaded by a particular user
@api_view(['GET','DELETE'])
def UpdateProjectsApiView(request,username):
    try:
        user = User.objects.get(username=username)
        projects = Project.objects.filter(uploaded_by=user)

    except User.DoesNotExist or Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(projects,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        for project in projects:
            project.delete()
        return Response(status=status.HTTP_410_GONE)

# basic function API for updating a specific Project object uploaded by a particular user
@api_view(['PUT','DELETE','GET'])
def ModifyProjectAPIView(request,id):
    try:
        project = Project.objects.get(id=id)

    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data,status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        uploaded_by=User.objects.get(username=request.data['uploaded_by'])
        serializer = ProjectSerializer(project,data=request.data)
        if serializer.is_valid():
            serializer.save(uploaded_by=uploaded_by)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        project.delete()
        return Response(status=status.HTTP_410_GONE)


# basic function API for viewing existing Bids or adding a new user Bid
@api_view(['GET','POST'])
def BidApiView(request):
    if request.method =='GET':
        allbids = Bid.objects.all()
        serializer = BidSerializer(allbids,many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        try:
            user = User.objects.get(username=request.data['BidSentBy'])
            job = Project.objects.get(name=request.data['job'])
        except User.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(BidSentBy=user,job=job)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)

# basic function API for getting/deleting specific Bid objects or updating data for a specific Bid object
@api_view(['GET','PUT','DELETE'])
def UpdateBidApiView(request,id):
    try:
        bid = Bid.objects.get(id=id)

    except Bid.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BidSerializer(bid)
        return Response(serializer.data,status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        try:
            user = User.objects.get(username=request.data['BidSentBy'])
            job = Project.objects.get(name=request.data['job'])
        except User.DoesNotExist or Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = BidSerializer(bid,data=request.data)
        if serializer.is_valid():
            serializer.save(BidSentBy=user,job=job)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        bid.delete()
        return Response(status=status.HTTP_410_GONE)

# basic function API for getting/deleting specific Bid objects uploaded by a particular user
@api_view(['GET','DELETE'])
def DeleteBidsApiView(request,username):
    try:
        user = User.objects.get(username=username)
        bids = Bid.objects.filter(uploaded_by=user)

    except User.DoesNotExist or Bid.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(bids,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        for bid in bids:
            bid.delete()
        return Response(status=status.HTTP_410_GONE)

# basic function API for accepting or rejecting bids
@api_view(['PUT'])
def bid_reject_or_accept_API(request,id):
    try:
        bid = Bid.objects.get(id=id)

    except Bid.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = DecideBidSerializer(bid,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# basic function API for creating new users
@api_view(['GET','POST'])
@permission_classes([AllowAny])
def registrationAPI(request):
    if request.method =='GET':
        allusers = User.objects.all()
        serializer = RegistrationSerializer(allusers,many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            User.objects.create_user(
                serializer.initial_data['email'],
                serializer.initial_data['username'],
                serializer.initial_data['password']
            )
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)



