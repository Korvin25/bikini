# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..content.models import Video


def fill_video_covers():
    print 'filling...'
    for v in Video.objects.all():
        v.update_video_cover()
        print '  ', v.id, v.video_cover.url
    print '  done!'
