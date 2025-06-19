from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import CharField

def apply_unit_filters(units, request):
    search = request.query_params.get('search')
    if search:
        units = units.annotate(
            max_capacity_str=Cast('max_capacity', CharField())
        ).filter(
            Q(name__icontains=search) |
            Q(property__name__icontains=search) |
            Q(max_capacity_str__icontains=search) |
            Q(status__icontains=search) | 
            Q(description__icontains=search)
        )

    filter_param = request.query_params.get('filter')

    filter_map = {
        'active': 'active',
        'inactive': 'active',
        'capacity': '-max_capacity',
        'ascending_name': 'name',
        'descending_name': '-name',
        'status': 'status',
        'price_per_night': 'price_per_night',
        'descending_price_per_night': '-price_per_night',
        None: 'name',
    }

  
    if filter_param == 'active':
        units = units.filter(active=True)
    elif filter_param == 'inactive':
        units = units.filter(active=False)

    if filter_param not in ['active', 'inactive']:
        order_field = filter_map.get(filter_param, 'name')
        units = units.order_by(order_field)

    return units