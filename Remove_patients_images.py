import os
import re
import shutil
import csv
from collections import defaultdict

def group_files_by_id(folder_path):
    pattern = re.compile(r"OAS1_(\d{4})")
    groups = defaultdict(list)

    for filename in os.listdir(folder_path):
        match = pattern.search(filename)
        if match:
            groups[match.group(1)].append(filename)

    return groups


def total_file_count(groups):
    return sum(len(files) for files in groups.values())


# --- EXACT KNAPSACK ---
def select_ids_knapsack_exact(groups, target_remove):
    """
    Finds the combination of IDs whose total file count is
    as close as possible to target_remove (without exceeding it).
    """
    items = [(gid, len(files)) for gid, files in groups.items()]

    dp = {0: []}  # sum -> list of IDs

    for gid, size in items:
        new_dp = dict(dp)

        for current_sum, id_list in dp.items():
            new_sum = current_sum + size

            if new_sum > target_remove:
                continue

            if new_sum not in new_dp:
                new_dp[new_sum] = id_list + [gid]

        dp = new_dp

    best_sum = max(dp.keys())
    return set(dp[best_sum]), best_sum


def move_group(folder_path, destination_root, group_id, files, log_rows, dry_run=False):
    dest_folder = os.path.join(destination_root, "knapsack_removed", group_id)

    if not dry_run:
        os.makedirs(dest_folder, exist_ok=True)

    for f in files:
        src = os.path.join(folder_path, f)
        dst = os.path.join(dest_folder, f)

        if dry_run:
            print(f"[DRY RUN] Would move: {src} -> {dst}")
        else:
            shutil.move(src, dst)

    log_rows.append([group_id, len(files)])


def save_csv_log(csv_path, log_rows, dry_run=False):
    if dry_run:
        print(f"\n[DRY RUN] CSV log would be saved to: {csv_path}")
        return

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "file_count"])
        writer.writerows(log_rows)


if __name__ == "__main__":
    # --- User input ---
    source_folder = input("Enter SOURCE folder path: ").strip()
    destination_folder = input("Enter DESTINATION folder for removed files: ").strip()
    target_total = int(input("Enter target total file count: "))
    dry_run = input("Dry run? (y/n): ").strip().lower() == "y"

    # --- Group files ---
    groups = group_files_by_id(source_folder)

    current_total = total_file_count(groups)
    target_remove = current_total - target_total

    print(f"\nInitial total files: {current_total}")
    print(f"Target total: {target_total}")
    print(f"Need to remove: {target_remove}")

    if target_remove <= 0:
        print("No removal needed.")
        exit()

    # --- Exact knapsack ---
    selected_ids, removed_sum = select_ids_knapsack_exact(groups, target_remove)

    final_total = current_total - removed_sum

    print(f"\nSelected {len(selected_ids)} ID groups")
    print(f"Files removed: {removed_sum}")
    print(f"Final total: {final_total}")
    print(f"Difference from target: {abs(final_total - target_total)}")

    # --- Move files ---
    log_rows = []

    for gid in selected_ids:
        move_group(source_folder, destination_folder, gid, groups[gid], log_rows, dry_run)

    # --- Save CSV ---
    csv_path = os.path.join(destination_folder, "knapsack_log.csv")
    save_csv_log(csv_path, log_rows, dry_run)

    print("\nDone.")