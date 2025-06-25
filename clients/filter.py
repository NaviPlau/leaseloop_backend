from django.db.models import Q

def apply_client_filters(clients, request):
    """
    Filter clients based on query parameters.

    The query parameters that this function considers are:

    - search: a string to search for in the client's first name, email, address city, address country, or address street.
    - filter: how to order the results. The values are 'ascending_name', 'descending_name', 'ascending_email', 'descending_email', 'country', 'city', or None. If None, the default ordering is by first name.

    :param clients: The QuerySet of clients to filter.
    :param request: The request object with the query parameters.
    :return: The filtered QuerySet of clients.
    """
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