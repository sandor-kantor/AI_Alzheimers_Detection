import os
import re
import shutil
import random
import csv
from collections import defaultdict

VALID_CLASSES = ["Demented", "Non_Demented"]


def group_files_by_id(folder_path):
    pattern = re.compile(r"OAS1_(\d{4})")
    groups = defaultdict(list)

    for filename in os.listdir(folder_path):
        match = pattern.search(filename)
        if match:
            number = match.group(1)
            groups[number].append(filename)

    return groups


def split_ids(groups, train_pct, val_pct, test_pct):
    ids = list(groups.keys())
    random.shuffle(ids)

    total = len(ids)

    train_end = int(total * train_pct / 100)
    val_end = train_end + int(total * val_pct / 100)

    train_ids = ids[:train_end]
    val_ids = ids[train_end:val_end]
    test_ids = ids[val_end:]

    return train_ids, val_ids, test_ids


def folder_has_files(path):
    return os.path.exists(path) and any(os.scandir(path))


def check_destination(dataset_folder, class_name, dry_run=False):
    subfolders = ["train", "validation", "test"]
    existing = []

    for sub in subfolders:
        path = os.path.join(dataset_folder, sub, class_name)
        if folder_has_files(path):
            existing.append(path)

    if existing:
        print(f"\n⚠️ Warning: The following destination folders for '{class_name}' already contain files:")
        for path in existing:
            print(f" - {path}")

        if dry_run:
            print("\n[DRY RUN] Would prompt for confirmation here.")
            return True

        response = input("\nProceed and potentially overwrite files? (y/n): ").strip().lower()
        return response == "y"

    return True


def copy_files(source_folder, destination_folder, ids, groups, dry_run=False):
    if not dry_run:
        os.makedirs(destination_folder, exist_ok=True)

    for number in ids:
        for filename in groups[number]:
            src = os.path.join(source_folder, filename)
            dst = os.path.join(destination_folder, filename)

            if dry_run:
                print(f"[DRY RUN] Would copy: {src} -> {dst}")
            else:
                shutil.copy2(src, dst)


def save_csv_log(output_path, rows):
    with open(output_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "class", "split"])
        for class_name, split, patient_id in rows:
            writer.writerow([patient_id, class_name, split])


if __name__ == "__main__":
    # --- User input ---
    # One source folder per clinical group. Each class is split independently
    # with the SAME percentages, which keeps the number of patients per
    # clinical group balanced within each of train / validation / test.
    source_folders = {}
    for class_name in VALID_CLASSES:
        source_folders[class_name] = input(f"Enter SOURCE folder path for {class_name}: ").strip()

    dataset_folder = input("Enter 'dataset' (destination) folder path: ").strip()

    train_pct = float(input("Enter TRAIN percentage (e.g. 70): "))
    val_pct = float(input("Enter VALIDATION percentage (e.g. 15): "))
    test_pct = float(input("Enter TEST percentage (e.g. 15): "))

    if train_pct + val_pct + test_pct != 100:
        raise ValueError("Percentages must sum to 100")

    seed_input = input("Enter random seed (or press Enter to skip): ").strip()
    seed = int(seed_input) if seed_input else None

    dry_run_input = input("Dry run only? (y/n): ").strip().lower()
    dry_run = dry_run_input == "y"

    # --- Safety check (both classes before doing anything) ---
    for class_name in VALID_CLASSES:
        if not check_destination(dataset_folder, class_name, dry_run):
            print("Aborted by user.")
            exit()

    # --- Process each class independently with the same percentages ---
    csv_rows = []
    summary = {}

    for class_name in VALID_CLASSES:
        # Re-seed before each class so the split is reproducible and the
        # proportions are applied consistently to every clinical group.
        if seed is not None:
            random.seed(seed)

        source_folder = source_folders[class_name]
        groups = group_files_by_id(source_folder)

        train_ids, val_ids, test_ids = split_ids(groups, train_pct, val_pct, test_pct)

        train_folder = os.path.join(dataset_folder, "train", class_name)
        val_folder = os.path.join(dataset_folder, "validation", class_name)
        test_folder = os.path.join(dataset_folder, "test", class_name)

        copy_files(source_folder, train_folder, train_ids, groups, dry_run)
        copy_files(source_folder, val_folder, val_ids, groups, dry_run)
        copy_files(source_folder, test_folder, test_ids, groups, dry_run)

        for i in train_ids:
            csv_rows.append((class_name, "train", i))
        for i in val_ids:
            csv_rows.append((class_name, "validation", i))
        for i in test_ids:
            csv_rows.append((class_name, "test", i))

        summary[class_name] = {
            "total": len(groups),
            "train": len(train_ids),
            "validation": len(val_ids),
            "test": len(test_ids),
        }

    # --- CSV log ---
    csv_path = os.path.join(dataset_folder, "split_log.csv")
    if dry_run:
        print(f"\n[DRY RUN] CSV log would be saved to: {csv_path}")
    else:
        os.makedirs(dataset_folder, exist_ok=True)
        save_csv_log(csv_path, csv_rows)

    # --- Summary ---
    print("\nDone.")
    print(f"{'Split':<12}" + "".join(f"{c:<16}" for c in VALID_CLASSES))
    for split in ["total", "train", "validation", "test"]:
        label = "Total IDs" if split == "total" else split.capitalize()
        print(f"{label:<12}" + "".join(f"{summary[c][split]:<16}" for c in VALID_CLASSES))
