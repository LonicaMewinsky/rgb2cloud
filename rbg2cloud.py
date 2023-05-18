from PIL import Image
import numpy as np

inp_image = Image.open("C:/path/to/image.png")
out_xyz = "C:/path/to/pointcloud.xyz"
black_threshold = 5 #cull near-black pixels

#Iterate all pixels, write points if color > black_threshold
def rgb2cloud(image):
    pixels = image.getdata()
    points = []
    for i, pixel in enumerate(pixels):
        x = i % image.width
        y = i // image.width
        for color in pixel:
            if color > black_threshold:
                points.append([x, y, color])
    return points

#Make cloud
cloud = rgb2cloud(inp_image)
data_array = np.array(cloud)

#Z axis was squished to 255; try to scale it back to normal
data_array[:, 2] = data_array[:, 2] * (inp_image.width/255)

#Write to xyz file
with open(out_xyz, 'w') as file:
    for array in data_array:
        file.write(f"{array[0]} {array[1]} {array[2]}\n")