from django.db.models import Q

def apply_promocode_filters(promocodes, request):
    """
    Filter promocodes based on query parameters.

    The query parameters that this function considers are:

    - search: a string to search for in the code or description.
    - filter: how to order the results. The values are 'ascending_name', 'descending_name',
      'ascending_code', 'descending_code', 'ascending_discount', 'descending_discount',
      'earliest', 'latest', or None. If None, the default ordering is by code.

    :param promocodes: The QuerySet of promocodes to filter.
    :param request: The request object with the query parameters.
    :return: The filtered QuerySet of promocodes.
    """

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