import os

folder_path = './static/VENGEWAV'
keywords = ['Cutted']

def delete_files_with_keywords(folder_path, keywords):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if any(keyword in file_name for keyword in keywords):
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_name}")
            except Exception as e:
                print(f"Error deleting file {file_name}: {e}")

delete_files_with_keywords(folder_path, keywords)
