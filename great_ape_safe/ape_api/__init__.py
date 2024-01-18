from .ebtc import eBTC
from .uni_v3 import UniV3


class ApeApis:
    def init_ebtc(self):
        self.ebtc = eBTC(self)

    def init_uni_v3(self):
        self.uni_v3 = UniV3(self)
