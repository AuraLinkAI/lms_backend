from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Stamp, Document
from .serializers import StampSerializer, DocumentSerializer

class StampViewSet(viewsets.ModelViewSet):
    serializer_class = StampSerializer
    queryset = Stamp.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    queryset = Document.objects.all()

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        metadata = {
            "uploaded_by": self.request.user.username,
            "timestamp": str(serializer.validated_data["created_at"]),
        }
        serializer.save(user=self.request.user, metadata=metadata)

    @action(detail=True, methods=["post"])
    def apply_stamp(self, request, pk=None):
        document = self.get_object()
        stamp_id = request.data.get("stamp_id")
        try:
            stamp = Stamp.objects.get(id=stamp_id, user=request.user)
        except Stamp.DoesNotExist:
            return Response({"error": "Stamp not found"}, status=status.HTTP_404_NOT_FOUND)

        # Example of applying stamp (logic to be implemented as needed)
        document.stamped = True
        document.save()

        return Response({"message": "Stamp applied successfully"})
