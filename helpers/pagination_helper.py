def get_paginated_items(query, page, per_page):
    offset = (page - 1) * per_page
    limited_query = query.offset(offset).limit(per_page)
    paginated_items = limited_query.all()

    return paginated_items
