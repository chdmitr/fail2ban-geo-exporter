import geoip2.database


class MaxmindDB:
    def __init__(self, config: dict):
        self.db_path = config['geo']['maxmind']['db_path']
        self.on_error = config['geo']['maxmind'].get('on_error', {})

    def annotate(self, ip: str) -> dict:
        reader = geoip2.database.Reader(self.db_path)
        try:
            lookup = reader.city(ip)
            entry = dict(
                city=str(lookup.city.name),
                latitude=str(lookup.location.latitude),
                longitude=str(lookup.location.longitude)
            )
        except Exception as e:
            if self.on_error is dict and len(self.on_error) > 0:
                entry = self.on_error
            else:
                entry = dict(
                    city=self.on_error.get('city', 'not set'),
                    latitude=self.on_error.get('latitude', '0'),
                    longitude=self.on_error.get('longitude', '0')
                )
        finally:
            reader.close()

        return entry

    def get_labels(self) -> list:
        return ['city', 'latitude', 'longitude']
