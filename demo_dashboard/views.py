from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from datetime import timedelta, date
import random

from properties.models import Property, PropertyImage
from lease_auth.models import Profile
from units.models import Unit, UnitImage
from services.models import Service
from promocodes.models import Promocodes
from clients.models import Client
from addresses.models import Address
from bookings.models import Booking
from invoices.models import Invoice
import os
from django.core.files import File
User = get_user_model()

from django.core.files.base import ContentFile

from bookings.serializers import BookingWriteSerializer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPERTY_IMAGE_DIR = os.path.join(BASE_DIR, 'media', 'demo', 'property_images')
UNIT_IMAGE_DIR = os.path.join(BASE_DIR, 'media', 'demo', 'unit_images')

def generate_valid_booking_dates(unit, max_retries=100):
    for _ in range(max_retries):
        # Randomly choose past or future
        if random.choice([True, False]):
            check_out = date.today() - timedelta(days=random.randint(1, 365))
            check_in = check_out - timedelta(days=random.randint(2, 7))
        else:
            check_in = date.today() + timedelta(days=random.randint(0, 365))
            check_out = check_in + timedelta(days=random.randint(2, 7))

        # Check for conflict
        if not Booking.objects.filter(
            unit=unit,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists():
            return check_in, check_out

    return None, None  # fallback if unable to find free slot


def get_random_image(path: str) -> File | None:
    images = [f for f in os.listdir(path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not images:
        return None

    selected_filename = random.choice(images)
    full_path = os.path.join(path, selected_filename)

    with open(full_path, 'rb') as f:
        content = f.read()
        django_file = ContentFile(content)
        django_file.name = selected_filename
        return django_file



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
    Invoice.objects.filter(booking__unit__property__owner=guest_user).delete()
    Client.objects.filter(user=guest_user).delete()
    Unit.objects.filter(property__owner=guest_user).delete()
    Property.objects.filter(owner=guest_user).delete()
    Promocodes.objects.filter(owner_id=guest_user).delete()

    property_names = [
        "Seaside Escape", "Mountain View Retreat", "City Central Flat",
        "Lakeside Lodge", "Forest Haven", "Desert Oasis",
        "Countryside Cottage", "Urban Loft", "Beachfront Bungalow",
        "Mountain View Villa", "City Central Studio", "Lakeside Cottage",
    ]

    unit_types = ['apartment', 'villa', 'house', 'studio', 'suite', 'cabin', 'condo', 'townhouse']
    unit_names = ["Deluxe", "Cozy", "Modern", "Rustic", "Elegant", "Sunny", "Quiet", "Spacious"]
    
    street_names = ["Maple Street", "Oak Avenue", "Pine Road", "Cedar Lane", "Birch Way", "Willow Lane", "Elm Street", "Spruce Drive", "Hickory Boulevard", "Chestnut Street"]
    cities = ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig", "Bremen", "Dresden", "Hannover", "Nuremberg", "Mannheim", "Karlsruhe", "Augsburg", "Wiesbaden", "Mönchengladbach", "Gelsenkirchen"]
    countries = ["Germany", "Austria", "Switzerland", "Netherlands", "Belgium", "France", "Italy", "Spain", "Portugal", "Czech Republic"]
    phone_numbers = [
        "+49 30 123456", "+49 40 654321", "+49 89 987654", "+49 69 123456", "+49 30 987654", "+49 40 654321",
        "+49 89 123456", "+49 69 654321", "+49 30 987654", "+49 40 123456", "+49 89 654321", "+49 69 987654",
        "+49 30 123456", "+49 40 654321", "+49 89 987654", "+49 69 123456", "+49 30 987654", "+49 40 654321",]
    properties = []
    units_by_property = {}

    for prop_name in property_names:
        address = Address.objects.create(
            street=random.choice(street_names),
            house_number=str(random.randint(1, 99)),
            postal_code=f"{random.randint(10000, 99999)}",
            city=random.choice(cities),
            country=random.choice(countries),
            phone=random.choice(phone_numbers)
        )

        property = Property.objects.create(
            owner=guest_user,
            name=prop_name,
            address=address,
            description=f"{prop_name} - A perfect place for your stay."
        )
        
        property_image = get_random_image(PROPERTY_IMAGE_DIR)
        if property_image:
            PropertyImage.objects.create(
                property=property,
                image=property_image,
                alt_text=f"Image for {property.name}"
            )

        properties.append(property)
        units_by_property[property.id] = []

        for _ in range(random.randint(1, 3)):
            unit = Unit.objects.create(
                property=property,
                name=f"{random.choice(unit_names)} {random.choice(unit_types).capitalize()}",
                description="A wonderful unit with all modern amenities.",
                capacity=random.randint(2, 4),
                max_capacity=random.randint(4, 6),
                price_per_night = round(random.uniform(60, 180), 2),
                price_per_extra_person = round(random.uniform(10, 25), 2),
                status=random.choice(['available', 'booked', 'maintenance', 'cleaning']),
                type=random.choice(unit_types)
            )
            
            
            unit_image_file = get_random_image(UNIT_IMAGE_DIR)
            if unit_image_file:
                UnitImage.objects.create(
                    unit=unit,
                    image=unit_image_file,
                    alt_text=f"Image for {unit.name}"
                )
            units_by_property[property.id].append(unit)

        for _ in range(random.randint(1, 3)):
            Service.objects.create(
                name=random.choice(["Breakfast", "Airport Shuttle", "Spa Access", "Cleaning", "Gym Access", "Parking", "Laundry", "Wi-Fi"]),
                type=random.choice(['one_time', 'per_day']),
                price = round(random.uniform(15, 50), 2),
                property=property
            )
    client_first_names = [
    "John", "Jane", "Alice", "Bob", "Charlie", "Emily", "Liam", "Emma", "Noah", "Olivia",
    "Ava", "Elijah", "Mia", "Sophia", "Lucas", "Amelia", "Mason", "Isabella", "Ethan", "Charlotte"
]

    client_last_names = [
    "Smith", "Doe", "Brown", "Johnson", "Williams", "Taylor", "Anderson", "Thomas", "Moore", "Jackson",
    "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis"
]
    email_domains = ["example.com", "demo.org", "mail.dev", "sample.net"]
    client_street_names = ["Client Street", "Client Avenue", "Client Road", "Client Lane", "Client Way"]
    client_postal_codes = ["10115", "10117", "10119", "10178", "10179", "10180", "10182", "10184", "10186", "10187"]
    client_cities = ["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt", "Stuttgart", "Düsseldorf", "Dortmund", "Essen", "Leipzig"]
    client_countries = ["Germany", "Austria", "Switzerland", "Netherlands", "Belgium", "France", "Italy", "Spain", "Portugal", "Czech Republic"]
    client_phone_numbers = [
        "+49 30 123456", "+49 40 654321", "+49 89 987654", "+49 69 123456", "+49 30 987654", "+49 40 123456",
        "+49 89 987654", "+49 69 123456", "+49 30 987654", "+49 40 123456", "+49 89 987654", "+49 69 123456",
        "+49 30 987654", "+49 40 123456", "+49 89 987654", "+49 69 123456", "+49 30 987654", "+49 40 123456",]
    clients = []
    for i in range(200):
        first = random.choice(client_first_names)
        last = random.choice(client_last_names)
        domain = random.choice(email_domains)

        email = f"{first.lower()}.{last.lower()}{random.randint(1, 99)}@{domain}"

        street_base = random.choice(["Client Street", "Client Avenue", "Client Road", "Client Lane", "Client Way", "Client Boulevard", "Client Drive", "Client Place", "Client Terrace", "Client Square"])
        street = f"{street_base} {random.randint(1, 150)}"
        phone = f"+49 30 {random.randint(100000, 999999)}"

        addr = Address.objects.create(
            street=street,
            house_number=str(random.randint(1, 99)),
            postal_code=random.choice(["10115", "10117", "10119", "10178", "10179"]),
            city=random.choice(["Berlin", "Hamburg", "Munich", "Cologne", "Frankfurt"]),
            country=random.choice(["Germany", "Austria", "Switzerland", "Netherlands", "Belgium"]),
            phone=phone
        )

        client = Client.objects.create(
            first_name=first,
            last_name=last,
            email=email,
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

    for _ in range(200):
        client = random.choice(clients)
        unit = random.choice(all_units)

        check_in, check_out = generate_valid_booking_dates(unit)
        if not check_in or not check_out:
                print(f"Could not find free dates for unit {unit.id}")
                continue

        guests = random.randint(1, unit.max_capacity)
        services = random.sample(all_services, k=random.randint(0, 2))
        promo = random.choice(promocodes + [None])


        serializer = BookingWriteSerializer(data={
            'unit': unit.id,
            'client': client.id,
            'check_in': check_in,
            'check_out': check_out,
            'guests_count': guests,
            'deposit_paid': random.choice([True, False]),
            'promo_code': promo.id if promo else None,
            'status': random.choice(['pending', 'confirmed', 'cancelled']),
            'services': [s.id for s in services]
        })
        if serializer.is_valid():
            serializer.save()
        else:
            print("Booking error:", serializer.errors)

    guest_profile = Profile.objects.get(user=guest_user)
    guest_profile.first_name = "Guest"
    guest_profile.last_name = "User"
    guest_profile.data_filled = True
    guest_profile.save()

    return Response({
        "message": "Demo-Data successfully initialized.",
        "properties": len(properties),
        "units": len(all_units),
        "clients": len(clients),
        "bookings": 200,
        "services": len(all_services),
        "promocodes": len(promocodes),
    }, status=status.HTTP_201_CREATED)