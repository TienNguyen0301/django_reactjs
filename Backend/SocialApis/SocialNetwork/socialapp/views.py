from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, generics
from django.conf import settings
from .models import User, Post, Action, Rating, Comment, PostView, Tag
from .paginators import SocialPaginator
from .perms import CommentOwnerPermisson
from .serializers import (
    UserSerializer,
    PostSerializer,
    ActionSerializer,
    RatingSerializer,
    CommentSerializer,
    AddCommentSerializer,
    PostViewSerializer,
    PostDetailSerializer,

)
from django.db.models import F
from django.http import Http404




class PostViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Post.objects.all().order_by('-created_date')
    serializer_class = PostSerializer
    pagination_class = SocialPaginator

    def retrieve(self, request, pk):
        p = Post.objects.get_or_create(post=self.get_object())
        p.views += 1
        p.save()

        return Response(p,
                        status=status.HTTP_200_OK)

    # def inc_view(self, request, pk):
    #     v, created = Post.objects.get_or_create(id=pk)
    #     v.views = F('views') + 1
    #     v.save()
    #
    #     v.refresh_from_db()
    #
    #     return Response(PostSerializer(v).data,
    #                     status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action in ['add_comment', 'take_action', 'rate']:
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]


    # @action(methods=['post'], detail=True, url_path='add-post')
    # def add_post(self, request, pk):
    #     content = request.data.get('content')
    #     title = request.data.get('title')
    #     # image = request.data.get('image')
    #     if content:
    #         c = Post.objects.create(content=content,
    #                                 title=title,
    #                                 post=self.get_object(),
    #                                 creator=request.user)
    #
    #         return Response(AddPostSerializer(c).data, status=status.HTTP_201_CREATED)
    #
    #     return Response(status=status.HTTP_400_BAD_REQUEST)



    @action(methods=['post'], detail=True, url_path='add-comment')
    def add_comment(self, request, pk):
        content = request.data.get('content')
        if content:
            c = Comment.objects.create(content=content,
                                       post=self.get_object(),
                                       creator=request.user)

            return Response(AddCommentSerializer(c).data, status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description='Get the comments of a lesson',
        responses={
            status.HTTP_200_OK: CommentSerializer()
        }
    )
    @action(methods=['get'], url_path='comments', detail=True)
    def get_comments(self, request, pk):
        post = self.get_object()
        comments = post.comments.select_related('creator').filter(active=True)

        return Response(CommentSerializer(comments, many=True).data,
                        status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='like')
    def take_action(self, request, pk):
        try:
            action_type = int(request.data['type'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            action = Action.objects.update_or_create(creator=request.user,
                                                     post=self.get_object(),
                                                     defaults={'type': action_type})

            return Response(ActionSerializer(action).data,
                            status=status.HTTP_200_OK)


    @action(methods=['post'], detail=True, url_path='rating')
    def rate(self, request, pk):
        try:
            rating = int(request.data['rating'])
        except IndexError | ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            r = Rating.objects.update_or_create(creator=request.user,
                                                post=self.get_object(),
                                                defaults={'rate': rating}
                                                )

            return Response(RatingSerializer(r).data,
                            status=status.HTTP_200_OK)


    @action(methods=['get'], detail=True, url_path='views')
    def inc_view(self, request, pk):
        v, created = PostView.objects.get_or_create(post=self.get_object())
        v.views = F('views') + 1
        v.save()

        v.refresh_from_db()

        return Response(PostViewSerializer(v).data,
                        status=status.HTTP_200_OK)



class PostDetailViewSet(viewsets.ViewSet, generics.RetrieveAPIView):
    queryset = Post.objects.filter(active=True)
    serializer_class = PostDetailSerializer


    @action(methods=['post'], detail=True, url_path='tags')
    def add_tag(self, request, pk):
        try:
            post = self.get_object()
        except Http404:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            tags = request.data.get('tags')
            if tags is not None:
                for tag in tags:
                    t, _ = Tag.objects.get_or_create(name=tag)
                    post.tags.add(t)

                post.save()

                return Response(self.serializer_class(post).data,
                                status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_404_NOT_FOUND)

    # def get_queryset(self):
    #     posts = Post.objects.filter(active=True)
    #
    #     q = self.request.query_params.get('q')
    #     if q is not None:
    #         posts = posts.filter(subject__icontains=q)
    #
    #     post_id = self.request.query_params.get('post_id')
    #     if post_id is not None:
    #         posts = posts.filter(post_id=post_id)
    #
    #     return posts

    # @action(methods=['get'], detail=True, url_path='posts')
    # def get_post(self, request, pk):
    #     # post = Post.objects.get(pk=pk)
    #     posts = self.get_object().posts.filter(active=True)
    #
    #     return Response(PostSerializer(posts, many=True).data,
    #                     status=status.HTTP_200_OK)






class CommentViewSet(viewsets.ViewSet, generics.DestroyAPIView,
                     generics.UpdateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().destroy(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)


    def partial_update(self, request, *args, **kwargs):
        if request.user == self.get_object().creator:
            return super().partial_update(request, *args, **kwargs)

        return Response(status=status.HTTP_403_FORBIDDEN)



class UserViewSet(viewsets.ViewSet, generics.CreateAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser, ]


    def get_permissions(self):
        if self.action == 'get_current_user':
            return [permissions.IsAuthenticated()]

        return [permissions.AllowAny()]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(self, request):
        return Response(self.serializer_class(request.user).data,
                        status=status.HTTP_200_OK)


class AuthInfo(APIView):
    def get(self, request):
        return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)

