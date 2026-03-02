import config
import numpy as np
from scipy.stats import truncnorm


def draw_halls_to_visit() -> int:
    """Left-tailed: most people visit many halls, few visit only 1-2."""
    # truncnorm(a, b) in terms of standard deviations from mean
    a = (1 - config.HALLS_MEAN) / config.HALLS_STD
    b = (7 - config.HALLS_MEAN) / config.HALLS_STD
    val = truncnorm.rvs(a, b, loc=config.HALLS_MEAN, scale=config.HALLS_STD)
    return int(round(val))


def draw_company_size() -> int:
    a = (1 - config.COMPANY_SIZE_MEAN) / config.COMPANY_SIZE_STD
    b = np.inf
    return max(
        1,
        int(
            truncnorm.rvs(
                a, b, loc=config.COMPANY_SIZE_MEAN, scale=config.COMPANY_SIZE_STD
            )
        ),
    )
