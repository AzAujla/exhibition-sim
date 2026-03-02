import random
import config


class Visitor:
    def __init__(self, ecount: int, theme: str) -> None:
        self.ecount = ecount
        self.theme = theme
        pass

    def try_inquire(self, theme: str, unrelated: bool, n_visitors: int) -> bool:
        if theme == self.theme or unrelated:
            p = min(
                1.00,
                config.P_BASE_INQUIRY
                + min(config.P_DP_MAX, n_visitors) * config.P_DP_INQUIRY,
            )

            if random.random() < p:
                return True

        return False

    pass
