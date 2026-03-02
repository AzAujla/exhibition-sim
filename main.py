from collections import defaultdict
import random
import pandas as pd

import config
import distributions
from visitor import Visitor
import map_data
import analytics
import heatmap


def get_stall(halls: dict, hall_id: str, stall_id: str) -> map_data.Stall | None:
    hall = halls.get(hall_id)
    if hall is None:
        return None

    for stall in hall.stalls:
        if stall.id == stall_id:
            return stall

    return None


def weighted_route(routes: list[map_data.Route]) -> map_data.Route:
    weights = [r.weight for r in routes]
    return random.choices(routes, weights=weights, k=1)[0]


def run(num_visiters: int) -> pd.DataFrame:
    records = []
    stall_inquirer_counts = defaultdict(int)

    for _ in range(num_visiters):
        visitor = Visitor(
            distributions.draw_company_size(), random.choice(config.ALL_THEMES)
        )

        halls_to_visit = distributions.draw_halls_to_visit()
        halls = random.sample(config.ALL_HALLS, halls_to_visit)

        for hall in halls:
            route = weighted_route(map_data.ROUTES[hall])
            for stall_id in route.sequence:
                stall = get_stall(map_data.HALLS, hall, stall_id)
                if stall is None:
                    continue

                if visitor.try_inquire(stall.theme, stall.misc, halls_to_visit):
                    stall_inquirer_counts[stall_id] += 1
                    records.append(
                        {
                            "stall_id": stall_id,
                            "hall_id": hall,
                            "stall_theme": stall.theme,
                            "visitor_theme": visitor.theme,
                            "company_size": visitor.ecount,
                        }
                    )

    return pd.DataFrame(records)


df = run(1000)
analytics.export(df)
heatmap.save(df, "heatmap.png")
print(analytics.summarize(df).head(10))
