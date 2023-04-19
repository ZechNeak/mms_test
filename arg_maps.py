from mbientlab.metawear.cbindings import *

acc_rates = {
    0.78125: AccBmi270Odr._0_78125Hz,
    1.5625: AccBmi270Odr._1_5625Hz,
    3.125: AccBmi270Odr._3_125Hz,
    6.25: AccBmi270Odr._6_25Hz,
    12.5: AccBmi270Odr._12_5Hz,
    25.0: AccBmi270Odr._25Hz,
    50.0: AccBmi270Odr._50Hz,
    100.0: AccBmi270Odr._100Hz,
    200.0: AccBmi270Odr._200Hz,
    400.0: AccBmi270Odr._400Hz,
    800.0: AccBmi270Odr._800Hz,
    1600.0: AccBmi270Odr._1600Hz
}

acc_ranges = {
    2: AccBoschRange._2G,
    4: AccBoschRange._4G,
    8: AccBoschRange._8G,
    16: AccBoschRange._16G
}

gyro_rates = {
    25: GyroBoschOdr._25Hz,
    50: GyroBoschOdr._50Hz,
    100: GyroBoschOdr._100Hz,
    200: GyroBoschOdr._200Hz,
    400: GyroBoschOdr._400Hz,
    800: GyroBoschOdr._800Hz,
    1600: GyroBoschOdr._1600Hz,
    3200: GyroBoschOdr._3200Hz
}

gyro_ranges = {
    125: GyroBoschRange._125dps,
    250: GyroBoschRange._250dps,
    500: GyroBoschRange._500dps,
    1000: GyroBoschRange._1000dps,
    2000: GyroBoschRange._2000dps
}

mag_presets = {
    "low": MagBmm150Preset.LOW_POWER,
    "regular": MagBmm150Preset.REGULAR,
    "enhanced": MagBmm150Preset.ENHANCED_REGULAR,
    "high": MagBmm150Preset.HIGH_ACCURACY
}