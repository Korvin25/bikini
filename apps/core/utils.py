# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from urlparse import urlparse, parse_qs

from watermarker.templatetags.watermark import watermark


# def with_watermark(image, watermark_name='default', position='C', opacity=100):
def with_watermark(image, watermark_name='default', position='BR', opacity=66):
    return watermark(image, '{},position={},opacity={}'.format(watermark_name, position, opacity))


def get_youtube_video_id(link):
    query = urlparse(link)
    video_id = 0
    try:
        if query.hostname == 'youtu.be':
            video_id = query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = parse_qs(query.query)
                video_id = p['v'][0]
            if query.path[:7] == '/embed/':
                video_id = query.path.split('/')[2]
            if query.path[:3] == '/v/':
                video_id = query.path.split('/')[2]
    except Exception as e:
        pass
    return video_id


def get_youtube_embed_video(link=None, video_id=None):
    """
    Получаем ссылку для вставки видео на сайт
    """
    video_id = video_id or get_youtube_video_id(link)
    return 'https://www.youtube.com/embed/{}'.format(video_id)


def get_vimeo_id(link):
    url = VIMEO_OEMBED_URL.format(link)
    video_id = 0
    try:
        r = requests.get(url)
        if r.status_code == 200:
            json_response = r.json()
            video_id = json_response.get('video_id')
    except Exception as e:
        pass
    return video_id


def get_error_message(e):
    try:
        err_message = unicode(e.message).decode('utf-8') or unicode(e).decode('utf-8')
    except UnicodeDecodeError:
        err_message = e.message.decode('utf-8')
    except:
        err_message = repr(e)
        # err_message = e.__class__.__name__
    return err_message
