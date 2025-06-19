from django.db.models import Case, When, Value, IntegerField

def apply_booking_filters(bookings, request):
    search = request.query_params.get('search')
    if search:
        from django.db.models import Q
        bookings = bookings.filter(
            Q(client__first_name__icontains=search) |
            Q(client__last_name__icontains=search) |
            Q(property__name__icontains=search) |
            Q(unit__name__icontains=search) |
            Q(property__address__city__icontains=search) |
            Q(property__address__country__icontains=search) |
            Q(property__address__street__icontains=search)
        )

    if not request.user.is_staff:
        bookings = bookings.filter(unit__property__owner=request.user)

    filter_param = request.query_params.get('filter')

    filter_map = {
        'client_name': 'client__first_name',
        'descending_client_name': '-client__first_name',
        'status': 'status',
        'ascending_total_price': 'total_price',
        'descending_total_price': '-total_price',
        'least_guests': 'guests_count',
        'most_guests': '-guests_count',
        'arrival_date': 'check_in',
        'departure_date': 'check_out',
        None: 'check_in'
    }

    if filter_param == 'status':
        bookings = bookings.annotate(
            status_order=Case(
                When(status='confirmed', then=Value(0)),
                When(status='pending', then=Value(1)),
                default=Value(2),
                output_field=IntegerField()
            )
        ).order_by('status_order', 'check_in')

    elif filter_param in ['arrival_date', 'departure_date']:
        bookings = bookings.filter(status='confirmed')
        order_field = filter_map.get(filter_param, 'check_in')
        bookings = bookings.order_by(order_field)

    else:
        order_field = filter_map.get(filter_param, 'check_in')
        bookings = bookings.order_by(order_field)

    return bookings