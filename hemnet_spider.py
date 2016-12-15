# -*- coding: utf-8 -*-
import json
import urllib
import scrapy
from scrapy.http import Request, FormRequest
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import logging
import settings

# TODO: Use pipeline to encode values in parse_posting?
# NOTE: This will give duplicates as there are multiple links matched by LinkExtractor. (http://www.hemnet.se/resultat?page=N)
# use Rule process_links attribute?
# NOTE: New productions can usually not be parsed (will be listed will all values NA)

class HemnetSpider(CrawlSpider):
    name        = 'hemnetspider'
    start_urls  = ['http://www.hemnet.se']
    rules       = (
        Rule(LinkExtractor(allow=('/resultat(\?page=\d+)',)), callback='parse_page', follow=True),
        Rule(LinkExtractor(allow='/bostad', restrict_xpaths='//ul[@id="search-results"]'), callback='parse_posting', follow=False)
    )

    def parse_start_url(self, response):
        """Submit FormRequest with search option (from seattings.search object).
        """
        logging.info('parsing start_url')
        yield FormRequest.from_response(response, formdata = createFormData(settings.search))


    def parse_page(self, response):
        """Submit Request for each property listing on this search result page.
        """
        logging.info('parsing page')
        for prop in response.css('div.result > ul > li > div > a::attr(href)').extract():
            url = prop if prop[0:4] == 'http' else self.start_urls[0]+prop         # Handle different href formats
            yield Request(url, callback=self.parse_posting, dont_filter=True)


    def parse_posting(self, response):
        # unicode(response.body.decode(response.encoding)).encode('utf-8')
        def getAttr(name):
            return (attr[names.index(name)] if name in names else 'NA').encode('utf-8')

        names = response.css('div.property__attributes-container > dl > dt::text').extract()
        attr  = response.css('div.property__attributes-container > dl > dd::text').extract()
        loc1  = response.css('p.property-location::text').extract()
        loc2  = response.css('p.property-location > span::text').extract()
        price = [s.encode('utf-8').strip() for s in response.css('span.property__price::text').extract()]
        yield {
            'location_1': loc1[0].encode('utf-8').strip() if len(loc1) > 0 else 'NA',
            'location_2': loc2[0].encode('utf-8').strip() if len(loc2) > 0 else 'NA',
            'price'     : price[0] if len(price) > 0 else 'NA',
            'type'      : getAttr(u'Bostadstyp').strip(),
            'size'      : getAttr(u'Boarea'),
            'rooms'     : getAttr(u'Antal rum'),
            'fee'       : getAttr(u'Avgift/månad'),
            'price_m2'  : getAttr(u'Pris/m²')
        }


# --------------- HELP FUNCTIONS ----------------------------------------


def lookupLocation(str):
    '''Look up location id's from search strings with hemnet calls.
    The first search hit (if any) will be used
    '''
    search_url = 'http://www.hemnet.se/locations/show?q=' + str
    search = json.loads(urllib.urlopen(search_url).read())
    if len(search) == 0:
        logging.info(' No location found for search string: ' + str)
        return []
    logging.info( ' Searching in location: ' + search[0]['name'])
    return search[0]['id']


def createFormData(settings):
    '''Create a form data object from settings.search object.
    Look up location id's if location search strings are provided.
    '''
    locations = settings['location_ids']
    if len(settings['location_ids']) == 0:
        locations = [str(lookupLocation(s)) for s in settings['locations']]
    return {
        'search[location_ids][]': locations,
        'search[item_types][]': settings['type'],
        'search[living_area_min]': settings['min_size'],
        'search[price_min]': settings['min_price'],
        'search[price_max]': settings['max_price'],
        'search[rooms_min]': settings['min_rooms'],
        'search[fee_max]': settings['max_fee'],
        'search[keywords]': settings['keywords'],
    }
