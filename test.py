import json

INPUT = "./data/raw/dataset.json"
OUTPUT = "projects.c.json"
LIMIT = 1_000_000


def test_c_project(limit: int = 10):
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


def test_rust_project(filename: str):
    with open(filename, "rb") as f:
        data = json.load(f)
        print(len(data))


if __name__ == "__main__":
    test_rust_project("dataset.join.json")
