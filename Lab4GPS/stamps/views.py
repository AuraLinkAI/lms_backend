from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Stamp, Document
from .serializers import StampSerializer, DocumentSerializer

class StampViewSet(viewsets.ModelViewSet):
    serializer_class = StampSerializer
    queryset = Stamp.objects.all()

    def get_queryset(self):
        # Filter the stamps by the authenticated user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Associate the authenticated user with the stamp being created
        serializer.save(user=self.request.user)

class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()
    permission_classes = [IsAuthenticated]  # Ensure that the user is authenticated

    def get_queryset(self):
        # Filter documents by the authenticated user
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        metadata = {
            "uploaded_by": self.request.user.username,
        }
        # Associate the authenticated user with the document being created
        serializer.save(user=self.request.user, metadata=metadata)

    @action(detail=True, methods=["post"])
    def apply_stamp(self, request, pk=None):
        # Ensure the user is authenticated before processing the request
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the document object
        document = self.get_object()

        # Get the stamp ID from the request data
        stamp_id = request.data.get("stamp_id")

        try:
            # Fetch the stamp object, ensuring it belongs to the authenticated user
            stamp = Stamp.objects.get(id=stamp_id, user=request.user)
        except Stamp.DoesNotExist:
            return Response({"error": "Stamp not found"}, status=status.HTTP_404_NOT_FOUND)

        # Apply the stamp to the document (You can expand this logic based on your actual requirements)
        document.stamped = True
        document.save()

        return Response({"message": "Stamp applied successfully"})