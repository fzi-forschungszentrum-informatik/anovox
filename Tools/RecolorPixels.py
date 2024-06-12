import logging

import numpy as np
from PIL import Image
from numba import jit

from DataAnalysis.Utils import get_label_attributes


@jit(nopython=True)  # Compile the function with Numba
def recolor_pixels(image, target_color, new_color):
    # Get the dimensions of the image
    image = image[:, :, :3]
    rows, cols, channels = image.shape

    logging.info(f"pil shape: {image.shape}")
    logging.info(f"image: {image}")

    # Loop through each pixel in the image
    for row in range(rows):
        for col in range(cols):
            pixel = image[row, col]

            # Check if the pixel matches the target color
            if np.array_equal(pixel, target_color):
                # print("found")
                # Recolor the pixel
                image[row, col] = new_color

    return image


def semantic_image_colorizer(image):
    image = Image.open(image)
    image_data = np.array(image)
    color_image = np.zeros((image.height, image.width, 3), dtype=np.uint8)
    unique_pixels = set()
    for row in range(image.height):
        for col in range(image.width):
            pixel = image_data[row, col]
            unique_pixels.add(pixel)
            color = get_label_attributes("id", pixel, "color")
            color_image[row, col] = np.array(color, dtype=np.uint8)
    print(unique_pixels)
    return color_image


if __name__ == "__main__":
    image_path = "xxx.png"

    recolored_image = semantic_image_colorizer(image_path)

    recolored_image_path = "recolored_image.png"
    Image.fromarray(recolored_image).save(recolored_image_path)

    recolored = Image.open(recolored_image_path)
    recolored.show()
