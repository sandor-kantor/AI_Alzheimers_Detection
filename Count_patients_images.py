import os
import re
from collections import defaultdict

def count_oas1_numbers(folder_path):
    pattern = re.compile(r"OAS1_(\d{4})")
    counts = defaultdict(int)

    for filename in os.listdir(folder_path):
        match = pattern.search(filename)
        if match:
            number = match.group(1)
            counts[number] += 1

    unique_count = len(counts)
    return unique_count, counts


if __name__ == "__main__":
    folder = input("Enter folder path: ").strip()
    unique_count, counts = count_oas1_numbers(folder)

    print(f"Unique 4-digit numbers count: {unique_count}\n")

    print("Counts per number:")
    for number in sorted(counts):
        print(f"{number}: {counts[number]}")