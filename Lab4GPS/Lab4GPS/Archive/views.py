from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions
from .models import Category, Tag, File, Comment, Like
from .serializers import CategorySerializer, TagSerializer, FileSerializer, CommentSerializer, LikeSerializer
from django.db.models import Q


class CategoryListView(generics.ListAPIView):
    """
    View to list all categories.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class TagListView(generics.ListAPIView):
    """
    View to list all tags.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]


class FileListView(APIView):
    """
    View to handle file listing, filtering, searching, and pagination.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        files = File.objects.all()
        category = request.query_params.get("category", "All")
        tags = request.query_params.getlist("tags", [])
        search = request.query_params.get("search", "")
        page = int(request.query_params.get("page", 1))
        files_per_page = 5

        # Filtering by category
        if category and category != "All":
            files = files.filter(category__name=category)

        # Filtering by tags
        if tags:
            files = files.filter(tags__name__in=tags).distinct()

        # Searching by title or description
        if search:
            files = files.filter(Q(title__icontains=search) | Q(description__icontains=search))

        # Pagination
        total_files = files.count()
        start = (page - 1) * files_per_page
        end = start + files_per_page
        files_paginated = files[start:end]

        serializer = FileSerializer(files_paginated, many=True, context={"request": request})
        return Response({
            "files": serializer.data,
            "total_pages": (total_files // files_per_page) + (1 if total_files % files_per_page > 0 else 0)
        })


class FileDetailView(APIView):
    """
    View to retrieve, update, or delete a single file.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            file.increment_views()
            serializer = FileSerializer(file, context={"request": request})
            return Response(serializer.data)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            serializer = FileSerializer(file, data=request.data, partial=True, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            file.delete()
            return Response({"message": "File deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


class FileUploadView(APIView):
    """
    View to handle file uploads.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = FileSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LikeView(APIView):
    """
    View to handle liking and unliking files.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            like, created = Like.objects.get_or_create(file=file, user=request.user)
            if not created:
                like.delete()
                return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
            return Response({"message": "File liked"}, status=status.HTTP_201_CREATED)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


class CommentView(APIView):
    """
    View to handle comments on files.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            data = request.data.copy()
            data["file"] = pk
            serializer = CommentSerializer(data=data, context={"request": request})
            if serializer.is_valid():
                serializer.save(user=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)


class FileDownloadView(APIView):
    """
    View to handle file downloads and increment the download count.
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, pk):
        try:
            file = File.objects.get(pk=pk)
            file.increment_downloads()
            serializer = FileSerializer(file, context={"request": request})
            return Response(serializer.data)
        except File.DoesNotExist:
            return Response({"error": "File not found"}, status=status.HTTP_404_NOT_FOUND)
