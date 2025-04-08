from rest_framework import serializers

class DashboardStatsSerializer(serializers.Serializer):
    next_arrival = serializers.DateField(allow_null=True)
    next_departure = serializers.DateField(allow_null=True)
    guests_today = serializers.IntegerField()
    today_occupancy = serializers.IntegerField()
    monthly_occupancy = serializers.IntegerField()
