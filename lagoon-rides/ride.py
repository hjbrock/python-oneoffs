from pyquery import PyQuery


class Ride:
    def __init__(self, name, min_height, thrill_level, splash_level, ride_type, url):
        self.name = name
        self.min_height = Ride.__or_zero(min_height)
        self.thrill_level = Ride.__or_zero(thrill_level)
        self.splash_level = Ride.__or_zero(splash_level)
        self.ride_type = ride_type
        self.url = url
        self.max_height = 0
        self.location = ''
        self.note = ''

    def fetch_details(self):
        ride_page_pq = PyQuery(url=self.url)
        self.note = ride_page_pq('div.footnote').text()

        ride_infos_pq = ride_page_pq('div.about-box div.information')
        for ride_info in ride_infos_pq:
            ride_info_pq = PyQuery(ride_info)
            label = ride_info_pq('.label').text().lower()
            if label == 'maxium height' or label == 'maximum height':
                self.max_height = int(ride_info_pq('.data').text().strip('″'))
            elif label == 'location':
                self.location = ride_info_pq('.data').text()

    def pretty_print(self):
        print(self.name, '(' + self.ride_type + ')' + ':')
        print('\t', 'Min Height:', self.min_height)
        print('\t', 'Max Height:', self.max_height)
        print('\t', 'Thrill Level:', self.thrill_level)
        print('\t', 'Splash Level:', self.splash_level)
        print('\t', 'Location:', self.location)
        print('\t', 'Note:', self.note)
        print('\t', 'Details:', self.url)

    def thrill_level_str(self):
        match self.thrill_level:
            case 0:
                return 'None'
            case 1:
                return 'Very Low'
            case 2:
                return 'Low'
            case 3:
                return 'Medium'
            case 4:
                return 'High'
            case 5:
                return 'Very High'
            case 6:
                return 'Extreme'
        return 'Unknown'

    def splash_level_str(self):
        match self.splash_level:
            case 0:
                return 'None'
            case 1:
                return 'Sprinkle'
            case 2:
                return 'Damp'
            case 3:
                return 'Wet'
            case 4:
                return 'Very Wet'
            case 5:
                return 'Soaked'
        return 'Unknown'

    def is_toddler_suitable(self):
        return self.thrill_level < 4 and self.min_height < 33 and self.max_height == 0

    @staticmethod
    def __or_zero(val):
        if val == '':
            return 0
        return int(val)
