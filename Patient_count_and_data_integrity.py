import os
import re
from collections import defaultdict

PATTERN = re.compile(r"OAS1_(\d{4})")

def get_patient_ids_and_file_count(folder_path):
    patient_ids = set()
    file_count = 0

    if not os.path.exists(folder_path):
        return patient_ids, file_count

    for root, _, files in os.walk(folder_path):
        for filename in files:
            match = PATTERN.search(filename)

            if match:
                patient_ids.add(match.group(1))
                file_count += 1

    return patient_ids, file_count


if __name__ == "__main__":

    dataset_folder = input("Enter DATASET folder path: ").strip()

    data = {}
    split_ids = defaultdict(set)

    print("\nCounts by split and class")
    print("-" * 75)
    print(f"{'Split':<12}{'Class':<15}{'Patients':>12}{'Files':>12}")
    print("-" * 75)

    for split in ["train", "validation", "test"]:
        for cls in ["Demented", "Non_Demented"]:

            folder = os.path.join(dataset_folder, split, cls)

            patient_ids, file_count = get_patient_ids_and_file_count(folder)

            data[(split, cls)] = patient_ids
            split_ids[split] |= patient_ids

            print(
                f"{split:<12}"
                f"{cls:<15}"
                f"{len(patient_ids):>12}"
                f"{file_count:>12}"
            )

    print("-" * 75)

    # ------------------------------------------------------------------
    # Leakage check between splits
    # ------------------------------------------------------------------

    print("\nLeakage check between dataset splits")
    print("-" * 75)

    leakage_found = False

    overlaps = {
        ("train", "validation"):
            split_ids["train"] & split_ids["validation"],

        ("train", "test"):
            split_ids["train"] & split_ids["test"],

        ("validation", "test"):
            split_ids["validation"] & split_ids["test"]
    }

    for (a, b), overlap in overlaps.items():

        if overlap:
            leakage_found = True

            print(
                f"WARNING: {len(overlap)} patient(s) appear "
                f"in both {a} and {b}"
            )

            print(f"IDs: {sorted(overlap)}\n")

        else:
            print(f"OK: No overlap between {a} and {b}")

    # ------------------------------------------------------------------
    # Leakage check between classes
    # ------------------------------------------------------------------

    print("\nLeakage check between classes")
    print("-" * 75)

    demented_ids = set()
    non_demented_ids = set()

    for split in ["train", "validation", "test"]:
        demented_ids |= data[(split, "Demented")]
        non_demented_ids |= data[(split, "Non_Demented")]

    class_overlap = demented_ids & non_demented_ids

    if class_overlap:

        print(
            f"WARNING: {len(class_overlap)} patient(s) appear "
            f"in both Demented and Non_Demented folders"
        )

        print(f"IDs: {sorted(class_overlap)}")

    else:
        print("OK: No overlap between Demented and Non_Demented")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    print("\nSummary")
    print("-" * 75)

    total_unique_patients = len(demented_ids | non_demented_ids)

    total_files = 0

    for split in ["train", "validation", "test"]:
        for cls in ["Demented", "Non_Demented"]:

            folder = os.path.join(dataset_folder, split, cls)

            _, file_count = get_patient_ids_and_file_count(folder)

            total_files += file_count

    print(f"Total unique patients: {total_unique_patients}")
    print(f"Total files:           {total_files}")

    if not leakage_found and not class_overlap:
        print("\nDataset integrity check PASSED")
    else:
        print("\nDataset integrity check FAILED")