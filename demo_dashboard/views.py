from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from django.contrib.auth import get_user_model
from datetime import timedelta, date
import random

from properties.models import Property, PropertyImage
from lease_auth.models import Profile, UserLogo
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

from django.utils.timezone import make_aware
import datetime

from .demodata.unit_data import unit_descriptions, unit_full_names, unit_image_descriptions
from .demodata.property_data import property_descriptions, property_names, property_image_descriptions
from .demodata.client_data import client_first_names, client_last_names, client_postal_codes, street_bases, phone_prefixes_by_country, email_domains, client_phones
from .demodata.address_data import country_to_cities, street_names, phone_numbers, emails

from django.core.files.base import ContentFile

from bookings.serializers import BookingWriteSerializer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROPERTY_IMAGE_DIR = os.path.join(BASE_DIR, 'media', 'demo', 'property_images')
UNIT_IMAGE_DIR = os.path.join(BASE_DIR, 'media', 'demo', 'unit_images')

def generate_valid_booking_dates(unit, max_retries=100):
    for _ in range(max_retries):
        if random.choice([True, False]):
            check_out = date.today() - timedelta(days=random.randint(1, 365))
            check_in = check_out - timedelta(days=random.randint(2, 7))
        else:
            check_in = date.today() + timedelta(days=random.randint(0, 365))
            check_out = check_in + timedelta(days=random.randint(2, 7))

        if not Booking.objects.filter(
            unit=unit,
            check_in__lt=check_out,
            check_out__gt=check_in
        ).exists():
            return check_in, check_out

    return None, None


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
            password="guest1234BB!!",
            first_name="Guest",
            last_name="User",
        )

    Invoice.objects.filter(booking__client__user=guest_user).delete()
    Booking.objects.filter(client__user=guest_user).delete()
    Address.objects.filter(
            id__in=Client.objects.filter(user=guest_user).values_list('address_id', flat=True)
        ).delete()
    Address.objects.filter(
            id__in=Property.objects.filter(owner=guest_user).values_list('address_id', flat=True)
        ).delete()

    Client.objects.filter(user=guest_user).delete()
    Unit.objects.filter(property__owner=guest_user).delete()
    Service.objects.filter(property__owner=guest_user).delete()
    Property.objects.filter(owner=guest_user).delete()
    Promocodes.objects.filter(owner_id=guest_user).delete()
    Profile.objects.filter(user=guest_user).delete()
    UserLogo.objects.filter(user=guest_user).delete()


    unit_types = ['apartment', 'villa', 'house', 'studio', 'suite', 'cabin', 'condo', 'townhouse']
    properties = []
    units_by_property = {}

    guest_logo, _ = UserLogo.objects.get_or_create(user=guest_user)
    random_logo_image = get_random_image(UNIT_IMAGE_DIR)
    if random_logo_image:
        guest_logo.logo.save(random_logo_image.name, random_logo_image, save=True)

    guest_address = Address.objects.create(
        street="Demo Street",
        house_number="1",
        postal_code="12345",
        city="Demo City",
        country="DemoLand",
        phone="+49 30 000000"
    )

    guest_profile, _ = Profile.objects.get_or_create(user=guest_user)
    guest_profile.data_filled = True
    guest_profile.address = guest_address
    guest_profile.logo = guest_logo
    guest_profile.save()

    for _ in range(random.randint(4, 12)):
        prop_name = random.choice(property_names)
        country = random.choice(list(country_to_cities.keys()))
        city = random.choice(country_to_cities[country])
        address = Address.objects.create(
            street=random.choice(street_names),
            house_number=str(random.randint(1, 99)),
            postal_code=f"{random.randint(10000, 99999)}",
            country = country,
            city = city,
            phone=random.choice(phone_numbers)
        )

        property = Property.objects.create(
            owner=guest_user,
            name=prop_name,
            address=address,
            email = random.choice(emails),
            description=random.choice(property_descriptions),
            active = random.choice([True, False])
        )
        
        property_image = get_random_image(PROPERTY_IMAGE_DIR)
        for _ in range(random.randint(3, 7)):
            property_image = get_random_image(PROPERTY_IMAGE_DIR)
            if property_image:
                PropertyImage.objects.create(
                    property=property,
                    image=property_image,
                    alt_text=random.choice(property_image_descriptions)
                )

        properties.append(property)
        units_by_property[property.id] = []

        for _ in range(random.randint(1, 3)):
            unit = Unit.objects.create(
                property=property,
                name=random.choice(unit_full_names),
                description=random.choice(unit_descriptions),
                capacity=random.randint(2, 4),
                max_capacity=random.randint(4, 6),
                price_per_night = round(random.uniform(60, 180), 2),
                price_per_extra_person = round(random.uniform(10, 25), 2),
                status=random.choice(['available', 'booked', 'maintenance', 'cleaning']),
                type=random.choice(unit_types),
                active = random.choice([True, False])
            )

            random_ids = random.sample(range(1, 21), random.randint(1, 10))
            unit.amenities.set(random_ids)
            
            
            for _ in range(random.randint(3, 7)):
                unit_image_file = get_random_image(UNIT_IMAGE_DIR)
                if unit_image_file:
                    UnitImage.objects.create(
                        unit=unit,
                        image=unit_image_file,
                        alt_text=random.choice(unit_image_descriptions)
                    )
            units_by_property[property.id].append(unit)
        used_services = set()
        for _ in range(random.randint(1, 3)):
            for _ in range(10): 
                name = random.choice(["Breakfast", "Airport Shuttle", "Spa Access", "Cleaning", "Gym Access", "Parking", "Laundry", "Wi-Fi"])
                s_type = random.choice(['one_time', 'per_day'])
                key = (name, s_type)
                if key not in used_services:
                    used_services.add(key)
                    Service.objects.create(
                        name=name,
                        type=s_type,
                        price=round(random.uniform(15, 50), 2),
                        property=property
                    )
                    break

    
    clients = []
    for _ in range(50):
        country = random.choice(list(country_to_cities.keys()))
        city = random.choice(country_to_cities[country])
        first = random.choice(client_first_names)
        last = random.choice(client_last_names)
        domain = random.choice(email_domains)

        local_part = f"{first.lower()}.{last.lower()}{random.randint(1, 999)}"
        email = f"{local_part}@{domain}"
        street = f"{random.choice(street_bases)} {random.randint(1, 150)}"
        addr = Address.objects.create(
            street=street,
            house_number=str(random.randint(1, 99)),
            postal_code=random.choice(client_postal_codes),
            city=city,
            country=country,
            phone = random.choice(client_phones)
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
    active_count = 0
    for code in ["WELCOME10", "SUMMER15", "AUTUMN20", "WINTER25", "SPRING5"]:
        is_active = random.choice([True, False])
        if len(promocodes) - active_count >= 3:
            is_active = True
        promo = Promocodes.objects.create(
            code=code,
            description=f"{code} for special discount",
            valid_until=date.today() + timedelta(days=random.randint(40, 365)),
            discount_percent=random.choice([5, 10, 15, 20, 25]),
            owner_id=guest_user,
            active = is_active
        )
        if is_active:
            active_count += 1
        promocodes.append(promo)

    all_services = list(Service.objects.filter(property__owner=guest_user))
    all_units = [unit for units in units_by_property.values() for unit in units]

    for _ in range(100):
        client = random.choice(clients)
        unit = random.choice(all_units)

        check_in, check_out = generate_valid_booking_dates(unit)
        if not check_in or not check_out:
                print(f"Could not find free dates for unit {unit.id}")
                continue

        guests = random.randint(1, unit.max_capacity)
        property_services = list(Service.objects.filter(property=unit.property.id))
        services = random.sample(property_services, k=min(len(property_services), random.randint(0, 2)))
        promo = random.choice(promocodes + [None])
        promo_id = promo.id if promo and Promocodes.objects.filter(id=promo.id, active=True).exists() else None


        serializer = BookingWriteSerializer(data={
            'unit': unit.id,
            'client': client.id,
            'check_in': check_in,
            'check_out': check_out,
            'guests_count': guests,
            'deposit_paid': random.choice([True, False]),
            'promo_code': promo_id,
            'status': random.choice(['pending', 'confirmed', 'cancelled']),
            'services': [s.id for s in services]
        })
        if serializer.is_valid():
            booking = serializer.save()
            booking.refresh_from_db()

            update_fields = []

            if booking.total_price and booking.total_price > 0 and booking.deposit_paid is True:
                deposit = round(booking.total_price * random.uniform(0.2, 0.4), 2)
                booking.deposit_amount = deposit
                booking.total_price -= deposit
                update_fields += ['deposit_amount', 'total_price']

            random_days_before = random.randint(3, 20)
            random_created_at = booking.check_in - timedelta(days=random_days_before)
            if isinstance(random_created_at, datetime.date) and not isinstance(random_created_at, datetime.datetime):
                random_created_at = make_aware(datetime.datetime.combine(random_created_at, datetime.datetime.min.time()))
            booking.created_at = random_created_at
            update_fields.append('created_at')

            booking.save(update_fields=update_fields)

    return Response({
        "message": "Demo-Data successfully initialized.",
        "properties": len(properties),
        "units": len(all_units),
        "clients": len(clients),
        "bookings": 200,
        "services": len(all_services),
        "promocodes": len(promocodes),
    }, status=status.HTTP_201_CREATED)