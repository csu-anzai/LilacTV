# -*- coding: UTF-8 -*-
# -Created from the one by JewBMX in Scrubs.
# -Update by Tempest (Pulls links for RD users)

import re, urllib, urlparse
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils
from resources.lib.modules import debrid
from resources.lib.modules import cfscrape


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['ganool.ws', 'ganol.si', 'ganool123.com']
        self.base_link = 'https://ganool.ws'
        self.search_link = '/search/?q=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except BaseException:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if url is None:
                return sources
            if debrid.status() is False:
                raise Exception()
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            q = '%s' % cleantitle.get_gan_url(data['title'])
            url = self.base_link + self.search_link % q
            r = self.scraper.get(url).content
            v = re.compile('<a href="(.+?)" class="ml-mask jt" title="(.+?)">\n<span class=".+?">(.+?)</span>').findall(r)
            for url, check, quality in v:
                t = '%s (%s)' % (data['title'], data['year'])
                if t not in check:
                    raise Exception()
                key = url.split('-hd')[1]
                r = self.scraper.get('https://ganool.ws/moviedownload.php?q=' + key).content
                r = re.compile('<a rel=".+?" href="(.+?)" target=".+?">').findall(r)
                for url in r:
                    if any(x in url for x in ['.rar']):
                        continue
                    quality = source_utils.check_url(quality)
                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid:
                        continue
                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'direct': False, 'debridonly': True})
            return sources
        except:
            return sources

    def resolve(self, url):
        return url
