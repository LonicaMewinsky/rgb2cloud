from PIL import Image
import numpy as np

def process_image(image):
    pixels = image.getdata()
    points = []
    for i, pixel in enumerate(pixels):
        # Unpack the RGB values
        red, green, blue = pixel
        x = i % image.width
        y = i // image.width

        for color in pixel:
            if color > 10:
                points.append([x, y, color])

    return points

inp_image = Image.open("C:/Users/Timothy/Downloads/pm0006.png")
cloud = process_image(inp_image)
data_array = np.array(cloud)
data_array[:, 2] = data_array[:, 2] * (inp_image.size[0]/255)
with open("C:/A1111/Sheeter/Res/res.xyz", 'w') as file:
    for array in data_array:
        file.write(f"{array[0]} {array[1]} {array[2]}\n")