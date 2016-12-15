# -*- coding: utf-8 -*-

# Use either location_ids or locations (or neither)
# If location_ids (one or more) are provided, locations will be ignored.
# If neither is provided, all areas will be retured in search result.

search = {
    'location_ids': [],     # Array[string]: ['17744', '17755'] look at webpage source for codes
    'locations': 	[],     # Array[string]: ['Stockholm', 'Malmö kommun'] locations by string will be looked up and the first search result will be returned (if any)
    'type': 		[],     # Array[string]: options: 'all', 'fritidshus', 'villa', 'tomt', 'radhus', 'gard', 'other'
    'min_size': 	'',     # String (m2)  : '60'
    'min_price': 	'',     # string (SEK) : '1000000'
    'max_price': 	'',     # string (SEK) : '3000000'
    'min_rooms': 	'',     # string       : '3'
    'max_fee': 		'',     # string (SEK) : '4000'
    'keywords': 	''      # string       : 'balkong, kakelugn'
}
