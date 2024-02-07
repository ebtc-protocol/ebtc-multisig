from .ebtc import eBTC
from .cow import Cow


class ApeApis:
    def init_ebtc(self):
        self.ebtc = eBTC(self)

    def init_cow(self, prod=False):
        self.cow = Cow(self, prod=prod)