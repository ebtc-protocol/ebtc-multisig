AddressZero = "0x0000000000000000000000000000000000000000"
MaxUint256 = str(int(2 ** 256 - 1))
EmptyBytes32 = "0x0000000000000000000000000000000000000000000000000000000000000000"

## eBTC Constants
DECIMAL_PRECISION = 1000000000000000000
MAX_REWARD_SPLIT = 10000
MIN_REDEMPTION_FEE_FLOOR = (DECIMAL_PRECISION * 5) / 1000  # 0.5%
MIN_MINUTE_DECAY_FACTOR = 1  # Non-zero
MAX_MINUTE_DECAY_FACTOR = (
    999999999999999999  # Corresponds to a very fast decay rate, but not too extreme
)
MINIMUM_GRACE_PERIOD = 15 * 60  # 15 minutes
MAX_FEE_BPS = 1000
