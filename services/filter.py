from django.db.models import Q

def apply_service_filters(services, request):
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