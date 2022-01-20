from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import *
from rest_framework import generics, permissions
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import *
from django.core import serializers



#POST /api/follow/{id} authenticated user would follow user with {id}
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def follow(request,id):
    if request.method == 'POST':
        curr = request.user
        try:
            fid = User.objects.get(id=id)
            soc = socialprofile.objects.get(user=curr)
            target = socialprofile.objects.get(user=fid)
        except ObjectDoesNotExist:
            return Response({'Error':'User not found'},status=406)
        data = {}
        try:
            check = soc.following.get(user=fid)
            data['response'] = 'Already Following this user'
        except:
            target.followers.add(soc)
            soc.following.add(target)
            data['response'] = 'Started following this user'
        return Response(data,status=200)

#- POST /api/unfollow/{id} authenticated user would unfollow a user with {id}
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def unfollow(request,id):
    if request.method == 'POST':
        curr = request.user
        try:
            fid = User.objects.get(id=id)
            soc = socialprofile.objects.get(user=curr)
            target = socialprofile.objects.get(user=fid)
        except ObjectDoesNotExist:
            return Response({'Error':'User not found'},status=406)
        data = {}
        try:
            check = soc.following.get(user=fid)
            soc.following.remove(target)
            target.followers.remove(soc)
            data['response'] = 'Unfollowed this user'
        except:
            data['response'] = 'Already Unfollowed this user'
        return Response(data,status=200)

#- GET /api/user should authenticate the request and return the respective user profile.
   # - RETURN: User Name, number of followers & followings.
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def userprofile(request):
    if request.method == 'GET':
        user = request.user
        try:
            soc = socialprofile.objects.get(user=user)
        except ObjectDoesNotExist:
            return Response({'Error':'User Social Profile not found'},status=406)
        data = {}
        data['username'] = user.username
        data['following'] = soc.following.all().count()
        data['followers'] = soc.followers.all().count()
        return Response(data,status=200)


# - POST api/posts/ would add a new post created by the authenticated user.
#     - Input: Title, Description
#     - RETURN: Post-ID, Title, Description, Created Time(UTC).

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def addpost(request):
    if request.method == 'POST':
        user = request.user
        serializer = AddPostSerializer(data=request.data)
        if serializer.is_valid():
            obj = Posts.objects.create(title=serializer.validated_data['title'],desc=serializer.validated_data['desc'],user=user)
            data = {}
            data['post-id'] = obj.id
            data['title'] = obj.title
            data['created_at'] = obj.created_at
            data['desc'] = obj.desc
            return Response(data, status=200)
        else:
            return Response(serializer.errors,status=406)


# - DELETE api/posts/{id} would delete post with {id} created by the authenticated user.

@api_view(['DELETE','GET'])
@permission_classes((IsAuthenticated, ))
def deletepost(request, id):
    if request.method == 'DELETE':
        user = request.user
        try:
            dpost = Posts.objects.get(id=id)
            if dpost.user == user:
                dpost.delete()
                return Response({'Response':'Post Deleted'},status=200)
            else:
                return Response({'Response':'Not Your Post'},status=500)
        except ObjectDoesNotExist:
            return Response({'Error':'Post ID not found'},status=406)
    elif request.method == 'GET':
        # - GET api/posts/{id} would return a single post with {id} populated with its number of likes and comments
        try:
            post = Posts.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Error':'Post ID not found'},status=406)
        data = {}
        data['number-likes'] = Like.objects.filter(post=post,like=True).count()
        data['number-comments'] = Comment.objects.filter(post=post).count()
        data['title'] = post.title
        data['desc'] = post.desc
        return Response(data,status=200)


# - POST /api/like/{id} would like the post with {id} by the authenticated user.
        
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def likepost(request, id):
    if request.method == 'POST':
        user = request.user
        try:
            lpost = Posts.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Error':'Post ID not found'},status=406)
        try:
            check = Like.objects.get(user=user,post=lpost)
            if check.like == True:
                return Response({'Response':'Already Liked'},status=200)
            else:
                check.like = True
                check.save()
                return Response({'Response':'Post Liked'},status=200)
        except:
            Like.objects.create(user=user,post=lpost,like=True)
            return Response({'Response':'Post Liked'},status=200)


# - POST /api/unlike/{id} would unlike the post with {id} by the authenticated user.  

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def unlikepost(request, id):
    if request.method == 'POST':
        user = request.user
        try:
            ulpost = Posts.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Error':'Post ID not found'},status=406)
        try:
            check = Like.objects.get(user=user,post=ulpost)
            check.delete()
            return Response({'Response':'unliked'},status=200)
        except:
            return Response({'Response':'Post Already Unliked'},status=200)

# - POST /api/comment/{id} add comment for post with {id} by the authenticated user.
#     - Input: Comment
#     - Return: Comment-ID

@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
def addcomment(request, id):
    if request.method == 'POST':
        user = request.user
        serializer = AddCommentSerializer(data=request.data)
        try:
            post = Posts.objects.get(id=id)
        except ObjectDoesNotExist:
            return Response({'Error':'Post ID not found'},status=406)
        if serializer.is_valid():
            obj = Comment.objects.create(comm=serializer.validated_data['comment'],user=user,post=post)
            data = {}
            data['Comment-ID'] = obj.id
            return Response(data, status=200)
        else:
            return Response(serializer.errors,status=406)

# - GET /api/all_posts would return all posts created by authenticated user sorted by post time.
#     - RETURN: For each post return the following values
#         - id: ID of the post
#         - title: Title of the post
#         - desc: Description of the post
#         - created_at: Date and time when the post was created
#         - comments: Array of comments, for the particular post
#         - likes: Number of likes for the particular post

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def all_posts(request):
    if request.method == 'GET':
        user = request.user
        objs = Posts.objects.filter(user=user).order_by('-created_at')
        data = []
        for obj in objs:
            dat = {}
            dat['id'] = obj.id
            dat['title'] = obj.title
            dat['desc'] = obj.desc
            dat['created_at'] = obj.created_at
            com = Comment.objects.filter(post=obj)
            dat['comments'] = []
            for comu in com:
                du = {}
                du['comment'] = comu.comm
                du['user'] = comu.user.username
                du['time'] = comu.time
                dat['comments'].append(du)
            dat['number-likes'] = Like.objects.filter(post=obj,like=True).count()
            data.append(dat)
        return Response(data,status=200)
