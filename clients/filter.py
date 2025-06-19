from django.db.models import Q

def apply_client_filters(clients, request):
    search = request.query_params.get('search')
    if search:
        clients = clients.filter(
            Q(first_name__icontains=search) |
            Q(email__icontains=search) |
            Q(address__city__icontains=search) |
            Q(address__country__icontains=search) |
            Q(address__street__icontains=search)
        )

    filter_param = request.query_params.get('filter')

    filter_map = {
        'ascending_name': 'first_name',
        'descending_name': '-first_name',
        'ascending_email': 'email',
        'descending_email': '-email',
        'country': 'address__country',
        'city': 'address__city',
        None: 'first_name',
    }

    order_field = filter_map.get(filter_param, 'first_name')
    clients = clients.order_by(order_field)

    return clients