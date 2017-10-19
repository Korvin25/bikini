# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from urlparse import urlparse, parse_qs


def get_youtube_video_id(link):
    """
    Получаем ID ютуб-видео из ссылки
    (http://stackoverflow.com/a/7936523)

    Примеры ссылок:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(link)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None


def get_youtube_embed_video(link=None, video_id=None):
    """
    Получаем ссылку для вставки видео на сайт
    """
    video_id = video_id or get_youtube_video_id(link)
    return 'https://www.youtube.com/embed/{}'.format(video_id)
