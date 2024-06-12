from PIL import Image
import numpy as np

COLOR_PALETTE = (
        np.array(
            [
                (0, 0, 0),          # unlabeled     =   0u
                (128, 64, 128),     # road          =   1u
                (244, 35, 232),     # sidewalk      =   2u
                (70, 70, 70),       # building      =   3u
                (102, 102, 156),    # wall          =   4u
                (190, 153, 153),    # fence         =   5u
                (153, 153, 153),    # pole          =   6u
                (250, 170, 30),     # traffic light =   7u
                (220, 220, 0),      # traffic sign  =   8u
                (107, 142, 35),     # vegetation    =   9u
                (152, 251, 152),    # terrain       =  10u
                (70, 130, 180),     # sky           =  11u
                (220, 20, 60),      # pedestrian    =  12u
                (255, 0, 0),        # rider         =  13u
                (0, 0, 142),        # Car           =  14u
                (0, 0, 70),         # truck         =  15u
                (0, 60, 100),       # bus           =  16u
                (0, 80, 100),       # train         =  17u
                (0, 0, 230),        # motorcycle    =  18u
                (119, 11, 32),      # bicycle       =  19u
                (110, 190, 160),    # static        =  20u
                (170, 120, 50),     # dynamic       =  21u
                (55, 90, 80),       # other         =  22u
                (45, 60, 150),      # water         =  23u
                (157, 234, 50),     # road line     =  24u
                (81, 0, 81),        # ground         = 25u
                (150, 100, 100),    # bridge        =  26u
                (230, 150, 140),    # rail track    =  27u
                (180, 165, 180),    # guard rail    =  28u
                (250, 128, 114),    # home          =  29u
                (255, 36, 0),       # animal        =  30u
                (224, 17, 95),      # nature        =  31u
                (184, 15, 10),      # special       =  32u
                (245, 0, 0),        # airplane      =  33u
                (245, 0, 0),        # falling       =  34u
            ]
        )
)


def label_mask(image_path, label):
    input_image = Image.open(image_path)
    input_img_arr = np.array(input_image).astype(np.uint16)
    label_color = COLOR_PALETTE [label]

    image_copy = np.copy(input_img_arr).astype(np.uint16)
    height, width, _ = image_copy.shape
    mask = np.all(image_copy == label_color, axis=-1)

    roi_img = np.full((height, width,), True, bool)  # np.zeros(shape=(height, width,), dtype=bool)
    roi_img[mask] = False
    return roi_img

if __name__== "__main__":
    example_image = "/home/lukasnroessler/Downloads/Anovox_Sample/Anovox/Scenario_ef183332-f895-4456-82ed-370fae4a7e88/SEMANTIC_IMG/SEMANTIC_IMG_5720.png"
    label = 14 # car/ ego vehicle
    roi = label_mask(example_image, label)
    roi_img = Image.fromarray(roi)
    roi_img.save("roi.png")