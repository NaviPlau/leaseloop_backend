from django.db.models import Q

def apply_invoice_filters(invoices, request):
    """
    Applies filters to a QuerySet of invoices based on the query parameters
    in the given request.

    The query parameters that this function considers are:

    - search: a string to search for in the client's first name, last name, 
      property name, unit name, invoice number, address city, address country, 
      or address street.
    - filter: how to order the results. The values are 'ascending_name', 
      'descending_name', 'ascending_date', 'descending_date', 'booking_id_lowest', 
      'booking_id_highest', 'amount_lowest', 'amount_highest', or None. If None, 
      the default ordering is by descending date.

    :param invoices: The QuerySet of invoices to filter.
    :param request: The request object with the query parameters.
    :return: The filtered QuerySet of invoices.
    """
    search = request.query_params.get('search')
    if search:
        invoices = invoices.filter(
            Q(booking__client__first_name__icontains=search) |
            Q(booking__client__last_name__icontains=search) |
            Q(booking__property__name__icontains=search) |
            Q(booking__unit__name__icontains=search) |
            Q(invoice_number__icontains=search) |
            Q(booking__property__address__city__icontains=search) |
            Q(booking__property__address__country__icontains=search) |
            Q(booking__property__address__street__icontains=search)
        )

    filter_param = request.query_params.get('filter')

    filter_map = {
        'ascending_name': 'booking__client__first_name',
        'descending_name': '-booking__client__first_name',
        'ascending_date': 'created_at', 
        'descending_date': '-created_at',  
        'booking_id_lowest': 'booking__id',
        'booking_id_highest': '-booking__id',
        'amount_lowest': 'booking__total_price',
        'amount_highest': '-booking__total_price',
        None: '-created_at'
    }

    order_field = filter_map.get(filter_param, '-created_at')
    invoices = invoices.order_by(order_field)

    return invoices