import requests


class IPApi:
    def __init__(self, config: dict):
        self.config = config
        self.collected_ip = {}
        self.access_key = config['geo']['ipapi']['access_key']
        self.url = 'http://api.ipapi.com'

    def _parse_field(self, rs_dict: dict, field: str, none_case='Not found'):
        value = rs_dict.get(field)
        return str(value if value is not None else none_case)

    def annotate(self, ip: str = '') -> dict:
        if ip in self.collected_ip.keys():
            return self.collected_ip.get(ip)
        try:
            print(f"Get information about {ip} from {self.url}")
            response = requests.get(
                        f'{self.url}/{ip}/?access_key={self.access_key}'
                    ).json()
            entry = dict(
                city=self._parse_field(response, "city"),
                country=self._parse_field(response, "country_name"),
                latitude=self._parse_field(response, "latitude", 0),
                longitude=self._parse_field(response, "longitude", 0),
            )
            self.collected_ip.update({ip: entry})
        except Exception as e:
            print(f"Error when determining information about {ip}", e)
            entry = {
                "city": "Error",
                "country": "",
                "latitude": "0",
                "longitude": "0"
            }
        return entry

    def get_labels(self):
        return ["city", "country", "latitude", "longitude"]
