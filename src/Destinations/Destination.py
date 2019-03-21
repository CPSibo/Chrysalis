
import attr

DESTINATIONS = []

def RegisteredDestionation(cls):
    DESTINATIONS.append(cls)
    return cls

@attr.s
class Destination:
    destination = ''

    def run(self, postprocessor):
        return None