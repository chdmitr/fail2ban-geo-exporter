import requests


class IPApi:
    def __init__(self, conf):
        self.conf = conf # cap
        self.collected_ip = {}
        self.url = 'https://ipapi.co'
        pass

    def annotate(self, ip=''):
        if ip in self.collected_ip.keys():
            return self.collected_ip.get(ip)
        try:
            print(f"Get information about {ip}")
            response = requests.get(f'{self.url}/{ip}/json/').json()
            entry = {
                "city": response.get("city"),
                "country": response.get("country_name"),
                "latitude": str(response.get("latitude")),
                "longitude": str(response.get("longitude"))
            }
            self.collected_ip.update({ip: entry})
        except Exception as e:
            print(f"Error when determining information about {ip}", e)
            entry = {
                    "Error": {
                    "city": "",
                    "country": "",
                    "latitude": "0",
                    "longitude": "0"
                }
            }
        return entry

    def get_labels(self):
        return ["city", "country", "latitude", "longitude"]
