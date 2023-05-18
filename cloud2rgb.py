import numpy as np
import math
import os
from PIL import Image

xyz_dir = "C:/path/to/cloud/dir"
img_resolution = 768

#Center foreground pixels to image
def center_foreground(image):
    grayscale_image = image.convert("L")
    foreground_box = grayscale_image.getbbox()
    foreground_center_x = (foreground_box[2] + foreground_box[0]) // 2
    foreground_center_y = (foreground_box[3] + foreground_box[1]) // 2

    shift_x = image.width // 2 - foreground_center_x
    shift_y = image.height // 2 - foreground_center_y

    centered_image = Image.new("RGB", (image.width, image.height), (0, 0, 0))
    centered_image.paste(image, (shift_x, shift_y))

    return centered_image

#Rotate cloud as needed
def rotate_point_cloud(point_cloud, angle_degrees, axis):
    angle_radians = math.radians(angle_degrees)
    if axis == 'x':
        rotation_matrix = np.array([[1, 0, 0],
                                    [0, math.cos(angle_radians), -math.sin(angle_radians)],
                                    [0, math.sin(angle_radians), math.cos(angle_radians)]])
    elif axis == 'y':
        rotation_matrix = np.array([[math.cos(angle_radians), 0, math.sin(angle_radians)],
                                    [0, 1, 0],
                                    [-math.sin(angle_radians), 0, math.cos(angle_radians)]])
    elif axis == 'z':
        rotation_matrix = np.array([[math.cos(angle_radians), -math.sin(angle_radians), 0],
                                    [math.sin(angle_radians), math.cos(angle_radians), 0],
                                    [0, 0, 1]])
    else:
        raise ValueError("Invalid rotation axis. Valid options are 'x', 'y', or 'z'.")
    
    rotated_point_cloud = np.dot(point_cloud, rotation_matrix)
    return rotated_point_cloud

def normalize_cloud(data_list, canvas_resolution = 768):
    data_array = np.array(data_list)

    #Un-comment to rotate the cloud as needed
    #data_array = rotate_point_cloud(data_array, 15, "y")
    #data_array = rotate_point_cloud(data_array, -5, "x")
    #data_array = rotate_point_cloud(data_array, -90, "z")

    range_x = (max(data_array[:, 0]) - min(data_array[:, 0]))
    range_y = (max(data_array[:, 1]) - min(data_array[:, 1]))
    min_xyz = np.min(data_array, axis=0)
    max_xyz = np.max(data_array, axis=0)

    scaled_data = np.copy(data_array)

    #Normalize X and Y
    scaled_data[:, :2] = (scaled_data[:, :2] - min_xyz[:2]) / (max_xyz[:2] - min_xyz[:2]) * (canvas_resolution-2) +1 #floor is 1
    if range_x > range_y:
        scaled_data[:, 1] = scaled_data[:, 1] * (range_y/range_x)
    else:
        scaled_data[:, 0] = scaled_data[:, 0] * (range_x/range_y)
    
    #Normalize Z (strictly to 255)
    scaled_data[:, 2] = (scaled_data[:, 2] - min_xyz[2]) / (max_xyz[2] - min_xyz[2]) * 254 + 1

    #Process cloud for effecient conversion to image
    scaled_data = np.round(scaled_data).astype(int)
    unique_data = np.unique(scaled_data, axis=0)
    
    #Reorder Z data smallest to largest
    #The stack ends up with bottom and top of range
    z_data = unique_data[:, 2]
    sorted_indices = np.argsort(z_data)
    sorted_data = [unique_data[i] for i in sorted_indices]

    return sorted_data

#Plot cloud points to RGB
def cloud2RGB(cloud, canvas_resolution):
    image_array = np.zeros((canvas_resolution, canvas_resolution, 3), dtype=np.uint8)
    for x, y, z in cloud:
        if 0 in image_array[x, y]:
            idx = np.where(image_array[x, y] == 0)[0][0]
            image_array[x, y, idx] = z
        else:
            image_array[x, y, 2] = z

    return image_array

#Iterate directory of XYZs, output PNGs to same directory
for filename in os.listdir(xyz_dir):
    if filename.endswith(".xyz"):
        file_path = os.path.join(xyz_dir, filename)
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(xyz_dir, output_filename)
        
        data_list = []
        with open(file_path, 'r') as f:
            for line in f:
                #ASSUMES xyz file contains ONLY FLOATS for ONLY points
                #TODO: Conditions for types, error handling
                data = [float(x) for x in line.strip().split()]
                data_list.append(data)
        ranged = normalize_cloud(data_list, img_resolution)
        colored = cloud2RGB(ranged, img_resolution)
        img = Image.fromarray(colored, "RGB")
        #Process image.. uncomment as needed
        #img = img.transpose(Image.ROTATE_90)
        #img = center_foreground(img)
        img.save(output_path)