# -*- coding: utf-8 -*-
from __future__ import unicode_literals


def get_wishlist_from_request(request):
    profile = request.user
    wishlist = request.session.get('wishlist', []) if profile.is_anonymous() else profile.wishlist
    return wishlist
