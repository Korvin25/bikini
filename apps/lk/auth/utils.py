# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.utils import IntegrityError

from apps.lk.models import WishListItem


def update_wishlist(request, profile):
    s_wishlist = request.session.get('wishlist', [])
    if len(s_wishlist) and not profile.wishlist_items.count():
        for item in s_wishlist:
            try:
                import ipdb; ipdb.set_trace()
                WishListItem.objects.create(profile=profile,
                                            product_id=item.get('product_id', 0),
                                            option_id=item.get('option_id', 0),
                                            price_rub=item.get('price_rub', 0.0),
                                            price_eur=item.get('price_eur', 0.0),
                                            price_usd=item.get('price_usd', 0.0),
                                            attrs=item.get('attrs', {}),
                                            extra_products=item.get('extra_products', {}),
                                            hash=item.get('hash', 0))
            except IntegrityError:
                pass
            except TypeError:
                pass
            # except Exception as exc:
            #     import ipdb; ipdb.set_trace()
