import os

ml_folders = ["train", "validation", "test"]
clinical_folders = ["Non_Demented", "Demented"]

os.chdir(input("Enter 'dataset' (e.g. /Users/Sandor/dataset) folder path: ").strip())

for i in ml_folders:
    # Check if directory exists before creating it
    if not os.path.exists(i):
        os.mkdir(i)
    
    # Create subdirectories inside each ai_folder
    for j in clinical_folders:
        # Create path for subdirectory
        subdir_path = os.path.join(i, j)
        # Check if subdirectory exists before creating it
        if not os.path.exists(subdir_path):
            os.mkdir(subdir_path)