from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from accounts.models import User
from listings.models import Listing
from .serializers import UserSerializer, ListingSerializer

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

class ListingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Listing.objects.filter(status='active')
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
