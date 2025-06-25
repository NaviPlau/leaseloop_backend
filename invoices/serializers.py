from rest_framework import serializers
from .models import Invoice
from bookings.serializers import BookingReadSerializer
from lease_auth.models import UserLogo

class InvoiceSerializer(serializers.ModelSerializer):
    booking = BookingReadSerializer(read_only=True)
    logo_path = serializers.SerializerMethodField()
    class Meta:
        model = Invoice
        fields = '__all__'

    def get_logo_path(self, obj):
        """
        Returns the path to the logo of the user who owns the property where the
        invoice was generated. If the user does not have a logo, returns None.
        """
        
        try:
            user = obj.booking.property.owner
            logo = UserLogo.objects.get(user=user)
            if logo.logo:
                return logo.logo.url
        except (UserLogo.DoesNotExist, AttributeError):
            return None
