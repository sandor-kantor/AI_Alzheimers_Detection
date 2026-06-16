import os
import re
from itertools import combinations

PATTERN = re.compile(r"OAS1_(\d{4})")

CLASSES = [
    "Mild Dementia",
    "Moderate Dementia",
    "Non Demented",
    "Very mild Dementia"
]


def get_patient_ids_and_file_count(folder_path):
    """
    Returns:
        patient_ids : set of unique OAS1 IDs
        file_count  : number of files matching the OAS1 pattern
    """
    patient_ids = set()
    file_count = 0

    if not os.path.exists(folder_path):
        print(f"WARNING: Folder not found: {folder_path}")
        return patient_ids, file_count

    for root, _, files in os.walk(folder_path):
        for filename in files:
            match = PATTERN.search(filename)

            if match:
                patient_ids.add(match.group(1))
                file_count += 1

    return patient_ids, file_count


if __name__ == "__main__":

    dataset_root = input(
        "Enter the path to the main dataset folder: "
    ).strip()

    class_data = {}

    print("\nCounts by clinical group")
    print("-" * 70)
    print(f"{'Folder':<25}{'Patients':>12}{'Images':>12}")
    print("-" * 70)

    total_images = 0
    all_patients = set()

    # --------------------------------------------------
    # Count patients and images
    # --------------------------------------------------

    for class_name in CLASSES:

        folder = os.path.join(dataset_root, class_name)

        patient_ids, file_count = (
            get_patient_ids_and_file_count(folder)
        )

        class_data[class_name] = patient_ids

        total_images += file_count
        all_patients |= patient_ids

        print(
            f"{class_name:<25}"
            f"{len(patient_ids):>12}"
            f"{file_count:>12}"
        )

    print("-" * 70)
    print(
        f"{'TOTAL':<25}"
        f"{len(all_patients):>12}"
        f"{total_images:>12}"
    )

    # --------------------------------------------------
    # Leakage check
    # --------------------------------------------------

    print("\nPatient overlap check")
    print("-" * 70)

    leakage_found = False

    for class1, class2 in combinations(CLASSES, 2):

        overlap = (
            class_data[class1]
            & class_data[class2]
        )

        if overlap:
            leakage_found = True

            print(
                f"WARNING: "
                f"{len(overlap)} patient(s) appear in both\n"
                f"  '{class1}' and '{class2}'"
            )

            print(
                f"IDs: {sorted(overlap)}\n"
            )

        else:
            print(
                f"OK: No overlap between "
                f"'{class1}' and '{class2}'"
            )

    print("-" * 70)

    if leakage_found:
        print(
            "\nDataset integrity check FAILED"
        )
    else:
        print(
            "\nDataset integrity check PASSED"
        )