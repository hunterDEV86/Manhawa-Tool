import zipfile
import os
from PIL import Image
import uuid

def merge_images(image_list, output_path):
    images = [Image.open(image) for image in image_list]
    widths, heights = zip(*(i.size for i in images))
    total_height = sum(heights)
    max_width = max(widths)
    
    new_image = Image.new('RGB', (max_width, total_height))
    
    y_offset = 0
    for img in images:
        new_image.paste(img, (0, y_offset))
        y_offset += img.height
    
    new_image.save(output_path)

def process_manhwa(zip_path, images_per_merge):
    # Create unique folder for this process
    process_id = str(uuid.uuid4())
    temp_dir = f'temp_files_{process_id}/'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Extract zip files to unique folder
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # List image files
    image_files = [os.path.join(temp_dir, f) for f in os.listdir(temp_dir) 
                  if f.lower().endswith(('jpg', 'jpeg', 'png', 'gif'))]
    image_files.sort()  # Sort files to maintain order
    
    # Group and merge images
    grouped_images = [image_files[i:i+images_per_merge] 
                     for i in range(0, len(image_files), images_per_merge)]
    
    output_images = []
    for idx, group in enumerate(grouped_images):
        output_path = os.path.join(temp_dir, f"merged_{idx+1}.jpg")
        merge_images(group, output_path)
        output_images.append(output_path)

    # Create output zip with unique name
    output_zip = f"merged_output_{process_id}.zip"
    with zipfile.ZipFile(output_zip, 'w') as zipf:
        for img in output_images:
            zipf.write(img, os.path.basename(img))
    
    # Cleanup temp files and folder
    for file in image_files + output_images:
        os.remove(file)
    os.rmdir(temp_dir)
    
    return output_zip

# Example usage:
# result = process_manhwa("input.zip", 3)
