# import imageio.v3 as iio
from PIL import Image
import numpy as np
import cv2
import sys

# COLOR_PALETTE = (
#         np.array(
#             [
#                 (0, 0, 0),          # unlabeled     =   0u
#                 (128, 64, 128),     # road          =   1u
#                 (244, 35, 232),     # sidewalk      =   2u
#                 (70, 70, 70),       # building      =   3u
#                 (102, 102, 156),    # wall          =   4u
#                 (190, 153, 153),    # fence         =   5u
#                 (153, 153, 153),    # pole          =   6u
#                 (250, 170, 30),     # traffic light =   7u
#                 (220, 220, 0),      # traffic sign  =   8u
#                 (107, 142, 35),     # vegetation    =   9u
#                 (152, 251, 152),    # terrain       =  10u
#                 (70, 130, 180),     # sky           =  11u
#                 (220, 20, 60),      # pedestrian    =  12u
#                 (255, 0, 0),        # rider         =  13u
#                 (0, 0, 142),        # Car           =  14u
#                 (0, 0, 70),         # truck         =  15u
#                 (0, 60, 100),       # bus           =  16u
#                 (0, 80, 100),       # train         =  17u
#                 (0, 0, 230),        # motorcycle    =  18u
#                 (119, 11, 32),      # bicycle       =  19u
#                 (110, 190, 160),    # static        =  20u
#                 (170, 120, 50),     # dynamic       =  21u
#                 (55, 90, 80),       # other         =  22u
#                 (45, 60, 150),      # water         =  23u
#                 (157, 234, 50),     # road line     =  24u
#                 (81, 0, 81),        # ground         = 25u
#                 (150, 100, 100),    # bridge        =  26u
#                 (230, 150, 140),    # rail track    =  27u
#                 (180, 165, 180),    # guard rail    =  28u
#                 (250, 128, 114),    # home          =  29u
#                 (255, 36, 0),       # animal        =  30u
#                 (224, 17, 95),      # nature        =  31u
#                 (184, 15, 10),      # special       =  32u
#                 (245, 0, 0),        # airplane      =  33u
#                 (245, 0, 0),        # falling       =  34u
#             ]
#         )
# )

LABEL = np.array([
    (255, 255, 255, 'Ego'),  # None 0
    (70, 70, 70, 'Building'),  # Building 1
    (100, 40, 40, 'Fences'),  # Fences 2
    (55, 90, 80, 'Other'),  # Other 3
    (220, 20, 60, 'Pedestrian'),  # Pedestrian 4
    (153, 153, 153, 'Pole'),  # Pole 5
    (157, 234, 50, 'RoadLines'),  # RoadLines 6
    (128, 64, 128, 'Road'),  # Road 7
    (244, 35, 232, 'Sidewalk'),  # Sidewalk 8
    (107, 142, 35, 'Vegetation'),  # Vegetation 9
    (0, 0, 142, 'Vehicle'),  # Vehicle 10
    (102, 102, 156, 'Wall'),  # Wall 11
    (220, 220, 0, 'TrafficSign'),  # TrafficSign 12
    (70, 130, 180, 'Sky'),  # Sky 13
    (81, 0, 81, 'Ground'),  # Ground 14
    (150, 100, 100, 'Bridge'),  # Bridge 15
    (230, 150, 140, 'RailTrack'),  # RailTrack 16
    (180, 165, 180, 'GuardRail'),  # GuardRail 17
    (250, 170, 30, 'TrafficLight'),  # TrafficLight 18
    (110, 190, 160, 'Static'),  # Static 19
    (170, 120, 50, 'Dynamic'),  # Dynamic 20
    (45, 60, 150, 'Water'),  # Water 21
    (145, 170, 100, 'Terrain'),  # Terrain 22
])
LABEL_COLORS = LABEL[:, :-1].astype(np.uint8) # / 255.0
LABEL_CLASS = np.char.lower(LABEL[:, -1])


def image_properties(inputs):
    for input in inputs:
        image = Image.open(input)
        image = np.asarray(image)
        # image = image[:,:,-1:]
        print("shape", image.shape)
        print("max", np.amax(image))
        print("min", np.amin(image))
        # np.squeeze(image, axis=2)
        image = Image.fromarray(image)
        # image.show()


def read_clearml_img(img):
    # img = cv2.imread(image,-1)
    depth_color = img[..., :-1].astype(float)
    semantic = img[..., -1]
    depth = 1000 * ((256 ** 2 * depth_color[..., 2] + 256 * depth_color[..., 1] + depth_color[..., 0]) / (256 ** 3 - 1))
    return depth, semantic, depth_color


def cut(image):
    # image = Image.open(input_path)
    image_arr = np.asarray(image)
    image_arr = np.copy(image_arr)
    # image_arr = image_arr[]
    print(image_arr.shape)

    # image = Image.fromarray(image_arr)
    # ("/home/tes_unreal/Desktop/BA/RbA/cutimage.png", image_arr)
    # image.show()
    return image_arr

def mask(input_path):
    # input = iio.imread(input_path)
    input_image = Image.open(input_path)
    input_img_arr = np.array(input_image).astype(np.uint16)

    copy = np.copy(input_img_arr).astype(np.uint16)
    # sliced_input = cut(copy)
    # mask = np.where(sliced_input == 255)
    mask = (copy==2)
    print("mask shape", mask.shape)
    copy[mask] = 255
    print("copy shape after", copy.shape)
    # iio.imwrite('/home/tes_unreal/Desktop/BA_gitlab/anomaly_benchmark/cityscapes.png', copy)
    # iio.imwrite('/home/lukasnroessler/Projects/anomaly_benchmark/mask.png', copy)
    copy_ = Image.fromarray(copy)
    copy_ = copy_.convert("L")
    copy_.save('/home/tes_unreal/Desktop/BA_gitlab/anomaly_benchmark/mask.png')


def color_semantics(image):
    # img = cv2.imread(image,-1)
    img = Image.open(image)
    img = np.asarray(img)
    height, width, _ = img.shape
    depth, semantic, _ = read_clearml_img(img)
    semantic_img = LABEL_COLORS[semantic]
    semantic_img = semantic_img.reshape((height,width,3)).astype(np.uint8)
    # semantic_img = cv2.cvtColor(semantic_img, cv2.COLOR_BGR2RGB)

def count_non_zero(image):
    image = Image.open(image)
    image = np.array(image)
    image = image.reshape(-1,1)
    return np.count_nonzero(image)


if __name__ == "__main__":
    inputs = sys.argv[1:]
    image_properties(inputs)
    print("count non zero:", count_non_zero(inputs[0]))
    # labelimg = cut(Image.open(inputs[0]))
    # img = Image.fromarray(labelimg)
    # img.show()
    # color_semantics(inputs[0])
    # img = cv2.imread(inputs[0],-1)


    mask(inputs[0])





