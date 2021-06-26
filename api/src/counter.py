#!/root/.pyenv/versions/ipython/bin/python
import sys
from time import sleep
from typing import Dict, Iterable
import pymongo

from src.lib import DB


def count_col(database, col) -> int:
    return database[col].estimated_document_count()


def format_sum(sums: Dict[str, int]) -> str:
    return " | ".join([f"{col}={count:,}" for col, count in sums.items()])


def populate_counts(database, cols: Iterable) -> Dict:
    return {col: count_col(database, col) for col in cols}


def populate_diffs(prev_values: Dict, curr_values: Dict) -> Dict:
    return {col: curr_values[col] - prev_values[col] for col in prev_values.keys()}


def printer(initial_values: Dict, prev_values: Dict, curr_values: Dict):
    for col in prev_values.keys():
        print(
            f"{col}: {curr_values[col]:,} +{curr_values[col] - prev_values[col]:,} {' ' * 45}"
        )
    print("~" * 30)
    print(f"+++ {format_sum(populate_diffs(initial_values, curr_values))} +++", end="\r")


def main():
    initial_values = populate_counts(DB, DB.list_collection_names())
    previous_values = initial_values.copy()
    curr_values = initial_values  # Shallow copy

    try:
        while True:
            curr_values = populate_counts(DB, previous_values.keys())
            printer(initial_values, previous_values, curr_values)
            previous_values = curr_values
            sleep(2)
    except KeyboardInterrupt:
        print("\nTotal added:")
        for col in initial_values.keys():
            print(
                f"{col}: {curr_values[col]:,} +{curr_values[col] - initial_values[col]:,} {' ' * 45}"
            )
        sys.exit(0)


if __name__ == "__main__":
    main()
