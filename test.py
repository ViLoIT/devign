import json

INPUT = "./data/raw/dataset.json"
OUTPUT = "projects.c.json"
LIMIT = 1_000_000


def process2(limit: int = 10):
    inputs = json.load(open(INPUT))[:limit]

    data = list(
        filter(
            lambda x: x is not None,
            map(
                lambda x: (
                    {
                        "project": x["project"],
                        "target": x["target"],
                        "commit_id": x["commit_id"],
                        "func": x["func"][:100],
                    }
                    if x["target"] == 1
                    else None
                ),
                inputs,
            ),
        )
    )

    json.dump(data, open(OUTPUT, "w"), indent=2)


if __name__ == "__main__":
    process2(10)
