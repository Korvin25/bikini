# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.utils import OperationalError, DataError, IntegrityError

from apps.catalog.models import Product
from apps.lk.models import Profile, WishListItem


def update_wishlist(request, profile):
    s_wishlist = request.session.get('wishlist', [])
    if len(s_wishlist) and not profile.wishlist_items.count():
        for item in s_wishlist:
            try:
                WishListItem.objects.create(profile=profile,
                                            product_id=item.get('product_id', 0),
                                            price=item.get('price', 0.0),
                                            attrs=item.get('attrs', {}))
            except IntegrityError as e:
                pass
