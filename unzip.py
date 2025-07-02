import zipfile
import os
import glob

# Path to the folder with zip files
zip_folder = r'C:\Users\andre\projects\cda\base'  # <- change this
output_folder = zip_folder  # or use another folder

# Find all .zip files
zip_files = glob.glob(os.path.join(zip_folder, "*.zip"))

for zip_path in zip_files:
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            # Extract all files directly into the output folder (flatten)
            if not member.endswith('/'):
                with zip_ref.open(member) as source_file:
                    file_name = os.path.basename(member)
                    target_path = os.path.join(output_folder, file_name)
                    
                    # Optional: skip if file already exists
                    if not os.path.exists(target_path):
                        with open(target_path, 'wb') as target_file:
                            target_file.write(source_file.read())
print("✅ Done!")
