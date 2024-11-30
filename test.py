import json

INPUT = "./data/raw/dataset.json"
OUTPUT = "projects.json"
LIMIT = 1_000_000

inputs = json.load(open(INPUT))[:LIMIT]
data = list(
    filter(
        lambda x: x is not None,
        map(
            lambda x: (
                {
                    "project": x["project"],
                    "target": x["target"],
                    "commit_id": x["commit_id"],
                }
                if x["target"] == 1
                else None
            ),
            inputs,
        ),
    )
)

# project_set = set()

# for item in obj:
#     for key, value in item.items():
#         project_set.add(key)

print(len(data))
json.dump(data, open(OUTPUT, "w"), indent=2)
# json.dump(list(project_set), open(OUTPUT, "w"), indent=2)

MAX_WORDS_IN_BATCH = 10000


def __init__(
    self,
    sentences=None,
    corpus_file=None,
    vector_size=100,
    alpha=0.025,
    window=5,
    min_count=5,
    max_vocab_size=None,
    sample=1e-3,
    seed=1,
    workers=3,
    min_alpha=0.0001,
    sg=0,
    hs=0,
    negative=5,
    ns_exponent=0.75,
    cbow_mean=1,
    hashfxn=hash,
    epochs=5,
    null_word=0,
    trim_rule=None,
    sorted_vocab=1,
    batch_words=MAX_WORDS_IN_BATCH,
    compute_loss=False,
    callbacks=(),
    comment=None,
    max_final_vocab=None,
    shrink_windows=True,
):
    pass


# AttributeError: The vocab attribute was removed from KeyedVector in Gensim 4.0.0.
# Use KeyedVector's .key_to_index dict, .index_to_key list, and methods .get_vecattr(key, attr) and .set_vecattr(key, attr, new_val) instead.
# See https://github.com/RaRe-Technologies/gensim/wiki/Migrating-from-Gensim-3.x-to-4
