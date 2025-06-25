from django.db.models import Q

def apply_service_filters(services, request):
    """
    Filter services based on query parameters.

    The query parameters that this function considers are:

    - search: a string to search for in the service's name.
    - filter: how to order the results and filter by type. The values are 
      'ascending_name', 'descending_name', 'ascending_price', 'descending_price', 
      'ascending_property_name', 'descending_property_name', 'one_time', 'per_day', 
      or None. If None, the default ordering is by descending creation date.

    :param services: The QuerySet of services to filter.
    :param request: The request object with the query parameters.
    :return: The filtered QuerySet of services.
    """
    search = request.query_params.get('search')
    if search:
        services = services.filter(
            Q(name__icontains=search) 
        )

    filter_param = request.query_params.get('filter')

    filter_map = {
        'ascending_name': 'name',
        'descending_name': '-name',
        'ascending_price': 'price',
        'descending_price': '-price',
        'ascending_property_name': 'property__name',
        'descending_property_name': '-property__name',
        None: '-created_at'
    }

    if filter_param == 'one_time':
        services = services.filter(type='one_time')
    elif filter_param == 'per_day':
        services = services.filter(type='per_day')
    else:
        order_field = filter_map.get(filter_param, '-created_at')
        services = services.order_by(order_field)

    return services