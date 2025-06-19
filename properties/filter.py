from django.db.models import Q, Count

def apply_property_filters(properties, request):
    search = request.query_params.get('search')
    if search:
        properties = properties.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(address__city__icontains=search)
        )

    filter_param = request.query_params.get('filter')
    filter_map = {
        'ascending_name': 'name',
        'descending_name': '-name',
        'city': 'address__city',
        'country': 'address__country',
        'most_units': '-units_count',
        'most_images': '-images_count',
        None: 'name',  
    }

    if filter_param == 'most_units':
        properties = properties.annotate(units_count=Count('units'))
    if filter_param == 'active':
        properties = properties.filter(active=True)
    if filter_param == 'inactive':
        properties = properties.filter(active=False)
    if filter_param == 'most_images':
        properties = properties.annotate(images_count=Count('images'))

    order_field = filter_map.get(filter_param, 'name')
    properties = properties.order_by(order_field)

    return properties