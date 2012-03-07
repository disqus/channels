# -*- coding: utf-8 -*-
import re

urlre = re.compile("""(?i)\\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""")


class FakeClient(object):
    def oembed(self, url):
        return {"provider_url": "http://imgur.com", "version": "1.0", "url": "http://imgur.com/Bdl6A.jpg", "thumbnail_width": 90, "height": 467, "width": 500, "thumbnail_url": "http://imgur.com/Bdl6As.jpg", "provider_name": "Imgur", "type": "photo", "thumbnail_height": 90}


def format(res):
    tpl = '<a href="%s">%s</a><br /><a href="%s"><img src="%s" height="%s" width="%s" /></a><br />'
    return tpl % (res['url'], res['url'], res['url'],
                  res['thumbnail_url'], res['thumbnail_height'], res['thumbnail_width'])

def replace(html, client):
    matches = [s for s in urlre.split(html) if s]
    if len(matches) == 1:
        return html

    for i, part in enumerate(matches):
        if part and urlre.match(part):
            res = client.oembed(part)
            matches[i] = format(res)

    return ''.join(matches)

if __name__ == '__main__':
    d = " go to http://google.com and also http://www.example.com"
    print urlre.split(d)
    print urlre.split(" go to ")

    c = FakeClient()

    print replace(d, c)
