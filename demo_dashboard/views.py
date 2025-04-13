from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from datetime import timedelta, date
import random

from properties.models import Property
from units.models import Unit, UnitImage
from services.models import Service
from promocodes.models import Promocodes
from clients.models import Client
from addresses.models import Address
from bookings.models import Booking

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
def reset_guest_demo_data(request):
    try:
        guest_user = User.objects.get(username="guest@exampless.com")
    except User.DoesNotExist:
        guest_user = User.objects.create_user(
            username="guest@exampless.com",
            email="guest@exampless.com",
            password="guest1234BB!!"
        )

    Booking.objects.filter(client__user=guest_user).delete()
    Client.objects.filter(user=guest_user).delete()
    Unit.objects.filter(property__owner=guest_user).delete()
    Property.objects.filter(owner=guest_user).delete()
    Promocodes.objects.filter(owner_id=guest_user).delete()

    property_names = [
        "Seaside Escape", "Mountain View Retreat", "City Central Flat",
        "Lakeside Lodge", "Forest Haven"
    ]

    unit_types = ['apartment', 'villa', 'house', 'studio', 'suite', 'cabin', 'condo', 'townhouse']
    unit_names = ["Deluxe", "Cozy", "Modern", "Rustic", "Elegant", "Sunny", "Quiet", "Spacious"]

    properties = []
    units_by_property = {}

    for prop_name in property_names:
        address = Address.objects.create(
            street=f"{random.randint(1, 99)} Example Street",
            house_number=str(random.randint(1, 99)),
            postal_code=f"{random.randint(10000, 99999)}",
            city="Demo City",
            country="Demo Country",
            phone=f"+49 123 456789"
        )

        property = Property.objects.create(
            owner=guest_user,
            name=prop_name,
            address=address,
            description=f"{prop_name} - A perfect place for your stay."
        )
        properties.append(property)
        units_by_property[property.id] = []

        for _ in range(random.randint(1, 4)):
            unit = Unit.objects.create(
                property=property,
                name=f"{random.choice(unit_names)} {random.choice(unit_types).capitalize()}",
                description="A wonderful unit with all modern amenities.",
                capacity=random.randint(2, 4),
                max_capacity=random.randint(4, 6),
                price_per_night=random.uniform(60, 180),
                price_per_extra_person=random.uniform(10, 25),
                status=random.choice(['available', 'booked', 'maintenance', 'cleaning']),
                type=random.choice(unit_types)
            )
            units_by_property[property.id].append(unit)
            UnitImage.objects.create(unit=unit, alt_text="Sample image")

        for _ in range(random.randint(1, 3)):
            Service.objects.create(
                name=random.choice(["Breakfast", "Airport Shuttle", "Spa Access", "Cleaning"]),
                type=random.choice(['one_time', 'per_day']),
                price=random.uniform(15, 50),
                property=property
            )

    clients = []
    for i in range(100):
        addr = Address.objects.create(
            street=f"Client Street {i+1}",
            house_number=str(random.randint(1, 99)),
            postal_code="10115",
            city="Berlin",
            country="Germany",
            phone=f"+49 30 123456{i}"
        )
        client = Client.objects.create(
            first_name=f"Client{i+1}",
            last_name="Demo",
            email=f"client{i+1}@example.com",
            user=guest_user,
            address=addr
        )
        clients.append(client)

    promocodes = []
    for code in ["WELCOME10", "SUMMER15", "AUTUMN20", "WINTER25", "SPRING5"]:
        promo = Promocodes.objects.create(
            code=code,
            description=f"{code} for special discount",
            valid_until=date.today() + timedelta(days=90),
            discount_percent=random.choice([5, 10, 15, 20, 25]),
            owner_id=guest_user
        )
        promocodes.append(promo)

    all_services = list(Service.objects.filter(property__owner=guest_user))
    all_units = [unit for units in units_by_property.values() for unit in units]

    for _ in range(80):
        client = random.choice(clients)
        unit = random.choice(all_units)

        if random.choice([True, False]):
            check_out = date.today() - timedelta(days=random.randint(1, 365))
            check_in = check_out - timedelta(days=random.randint(2, 7))
        else:
            check_in = date.today() + timedelta(days=random.randint(0, 365))
            check_out = check_in + timedelta(days=random.randint(2, 7))

        guests = random.randint(1, unit.max_capacity)
        services = random.sample(all_services, k=random.randint(0, 2))
        promo = random.choice(promocodes + [None])

        booking = Booking.objects.create(
            unit=unit,
            client=client,
            check_in=check_in,
            check_out=check_out,
            guests_count=guests,
            deposit_paid=random.choice([True, False]),
            promo_code=promo
        )
        booking.services.set(services)

    return Response({
        "message": "Demo-Data successfully initialized.",
        "properties": len(properties),
        "units": len(all_units),
        "clients": len(clients),
        "bookings": 80,
        "services": len(all_services),
        "promocodes": len(promocodes),
    }, status=status.HTTP_201_CREATED)