from django.db.models import Q

def apply_promocode_filters(promocodes, request):
    search = request.query_params.get('search')
    if search:
        promocodes = promocodes.filter(
            Q(code__icontains=search) |
            Q(description__icontains=search)
        )

    filter_param = request.query_params.get('filter')

    filter_map = {
        'ascending_name': 'description',
        'descending_name': '-description',
        'ascending_code': 'code',
        'descending_code': '-code',
        'ascending_discount': 'discount_percent',
        'descending_discount': '-discount_percent',
        'earliest': '-valid_until',
        'latest': 'valid_until',
        None: 'code'
    }

    order_field = filter_map.get(filter_param, 'code')
    promocodes = promocodes.order_by(order_field)

    return promocodes