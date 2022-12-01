import geoip2.database


class MaxmindDB:
    def __init__(self, config: str):
        self.db_path = config['geo']['maxmind']['db_path']
        self.on_error = config['geo']['maxmind'].get('on_error', '')

    def annotate(self, ip: str) -> dict:
        reader = geoip2.database.Reader(self.db_path)
        try:
            lookup = reader.city(ip)
            entry = dict(
                city=str(lookup.city.name),
                latitude=str(lookup.location.latitude),
                longitude=str(lookup.location.longitude)
            )
        except Exception:
            if not self.on_error:
                entry = {}
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
