from .ebtc import eBTC
from .uni_v3 import UniV3
from .cow import Cow


class ApeApis:
    def init_ebtc(self):
        self.ebtc = eBTC(self)

    def init_uni_v3(self):
        self.uni_v3 = UniV3(self)

    def init_cow(self, prod=False):
        self.cow = Cow(self, prod=prod)
