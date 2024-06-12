from collections import namedtuple
import numpy as np
# import sys
import os
import argparse
from PIL import Image
from tqdm import tqdm
import shutil
# import imageio.v3 as iio
# taken from cityscapesscripts/helpers/labels.py

# python convert_dataset/convert_images.py --dataset_path /home/tes_unreal/Desktop/Dataset_BA/outputtest/Final_Output_19_40-17_09_2023/ --cityscapes_format
# a label and all meta information
Label = namedtuple( 'Label' , [

    'name'        , # The identifier of this label, e.g. 'car', 'person', ... .
                    # We use them to uniquely name a class

    'id'          , # An integer ID that is associated with this label.
                    # The IDs are used to represent the label in ground truth images
                    # An ID of -1 means that this label does not have an ID and thus
                    # is ignored when creating ground truth images (e.g. license plate).
                    # Do not modify these IDs, since exactly these IDs are expected by the
                    # evaluation server.

    'trainId'     , # Feel free to modify these IDs as suitable for your method. Then create
                    # ground truth images with train IDs, using the tools provided in the
                    # 'preparation' folder. However, make sure to validate or submit results
                    # to our evaluation server using the regular IDs above!
                    # For trainIds, multiple labels might have the same ID. Then, these labels
                    # are mapped to the same class in the ground truth images. For the inverse
                    # mapping, we use the label that is defined first in the list below.
                    # For example, mapping all void-type classes to the same ID in training,
                    # might make sense for some approaches.
                    # Max value is 255!

    'category'    , # The name of the category that this label belongs to

    'categoryId'  , # The ID of this category. Used to create ground truth images
                    # on category level.

    'hasInstances', # Whether this label distinguishes between single instances or not

    'ignoreInEval', # Whether pixels having this class as ground truth label are ignored
                    # during evaluations or not

    'color'       , # The color of this label
    ] )

labels_19 = [ # 19 but redone
    #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
    Label(  'unlabeled'            ,  0 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    Label(  'ego vehicle'          ,  1 ,       16 , 'void'            , 0       , False        , True         , (  1,  0,  0) ),
    # Label(  'rectification border' ,  2 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'out of roi'           ,  3 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'static'               ,  4 ,      255 , 'void'            , 0       , False        , True         , (110,190,160) ),
    Label(  'dynamic'              ,  5 ,      255 , 'void'            , 0       , False        , True         , (111, 74,  0) ),
    Label(  'ground'               ,  6 ,       17 , 'void'            , 0       , False        , True         , ( 81,  0, 81) ),
    Label(  'road'                 ,  7 ,        0 , 'flat'            , 1       , False        , False        , (128, 64,128) ),
    Label(  'sidewalk'             ,  8 ,        1 , 'flat'            , 1       , False        , False        , (244, 35,232) ),
    Label(  'parking'              ,  9 ,      255 , 'flat'            , 1       , False        , True         , (250,170,160) ),
    Label(  'rail track'           , 10 ,      255 , 'flat'            , 1       , False        , True         , (230,150,140) ),
    Label(  'building'             , 11 ,        2 , 'construction'    , 2       , False        , False        , ( 70, 70, 70) ),
    Label(  'wall'                 , 12 ,        3 , 'construction'    , 2       , False        , False        , (102,102,156) ),
    Label(  'fence'                , 13 ,        4 , 'construction'    , 2       , False        , False        , (190,153,153) ),
    Label(  'guard rail'           , 14 ,       18 , 'construction'    , 2       , False        , True         , (180,165,180) ),
    Label(  'bridge'               , 15 ,       19 , 'construction'    , 2       , False        , True         , (150,100,100) ),
    Label(  'tunnel'               , 16 ,      255 , 'construction'    , 2       , False        , True         , (150,120, 90) ),
    Label(  'pole'                 , 17 ,        5 , 'object'          , 3       , False        , False        , (153,153,153) ),
    # Label(  'polegroup'            , 18 ,      255 , 'object'          , 3       , False        , True         , (153,153,153) ),
    Label(  'traffic light'        , 19 ,        6 , 'object'          , 3       , False        , False        , (250,170, 30) ),
    Label(  'traffic sign'         , 20 ,        7 , 'object'          , 3       , False        , False        , (220,220,  0) ),
    Label(  'vegetation'           , 21 ,        8 , 'nature'          , 4       , False        , False        , (107,142, 35) ),
    Label(  'terrain'              , 22 ,        9 , 'nature'          , 4       , False        , False        , (152,251,152) ),
    Label(  'sky'                  , 23 ,       10 , 'sky'             , 5       , False        , False        , ( 70,130,180) ),
    Label(  'person'               , 24 ,       11 , 'human'           , 6       , True         , False        , (220, 20, 60) ),
    Label(  'rider'                , 25 ,       12 , 'human'           , 6       , True         , False        , (255,  0,  0) ),
    Label(  'car'                  , 26 ,       13 , 'vehicle'         , 7       , True         , False        , (  0,  0,142) ),
    Label(  'truck'                , 27 ,       14 , 'vehicle'         , 7       , True         , False        , (  0,  0, 70) ),
    Label(  'bus'                  , 28 ,       15 , 'vehicle'         , 7       , True         , False        , (  0, 60,100) ),
    Label(  'caravan'              , 29 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0, 90) ),
    Label(  'trailer'              , 30 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0,110) ),
    Label(  'train'                , 31 ,      255 , 'vehicle'         , 7       , True         , False        , (  0, 80,100) ),
    Label(  'motorcycle'           , 32 ,      255 , 'vehicle'         , 7       , True         , False        , (  0,  0,230) ),
    Label(  'bicycle'              , 33 ,      255 , 'vehicle'         , 7       , True         , False        , (119, 11, 32) ),
    # Label(  'license plate'        , -1 ,       -1 , 'vehicle'         , 7       , False        , True         , (  0,  0,142) ),
]


labels_new_order = [
    #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
    Label(  'unlabeled'            ,  0 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    Label(  'ego vehicle'          ,  1 ,        0 , 'void'            , 0       , False        , True         , (  1,  0,  0) ),
    # Label(  'rectification border' ,  2 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'out of roi'           ,  3 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'static'               ,  4 ,      255 , 'void'            , 0       , False        , True         , (110,190,160) ),
    Label(  'dynamic'              ,  5 ,      255 , 'void'            , 0       , False        , True         , (111, 74,  0) ),
    Label(  'ground'               ,  6 ,        1 , 'void'            , 0       , False        , True         , ( 81,  0, 81) ),
    Label(  'road'                 ,  7 ,        2 , 'flat'            , 1       , False        , False        , (128, 64,128) ),
    Label(  'sidewalk'             ,  8 ,        3 , 'flat'            , 1       , False        , False        , (244, 35,232) ),
    Label(  'parking'              ,  9 ,      255 , 'flat'            , 1       , False        , True         , (250,170,160) ),
    Label(  'rail track'           , 10 ,      255 , 'flat'            , 1       , False        , True         , (230,150,140) ),
    Label(  'building'             , 11 ,        4 , 'construction'    , 2       , False        , False        , ( 70, 70, 70) ),
    Label(  'wall'                 , 12 ,        5 , 'construction'    , 2       , False        , False        , (102,102,156) ),
    Label(  'fence'                , 13 ,        6 , 'construction'    , 2       , False        , False        , (190,153,153) ),
    Label(  'guard rail'           , 14 ,        7 , 'construction'    , 2       , False        , True         , (180,165,180) ),
    Label(  'bridge'               , 15 ,        8 , 'construction'    , 2       , False        , True         , (150,100,100) ),
    Label(  'tunnel'               , 16 ,      255 , 'construction'    , 2       , False        , True         , (150,120, 90) ),
    Label(  'pole'                 , 17 ,        9 , 'object'          , 3       , False        , False        , (153,153,153) ),
    # Label(  'polegroup'            , 18 ,      255 , 'object'          , 3       , False        , True         , (153,153,153) ),
    Label(  'traffic light'        , 19 ,       10 , 'object'          , 3       , False        , False        , (250,170, 30) ),
    Label(  'traffic sign'         , 20 ,       11 , 'object'          , 3       , False        , False        , (220,220,  0) ),
    Label(  'vegetation'           , 21 ,       12 , 'nature'          , 4       , False        , False        , (107,142, 35) ),
    Label(  'terrain'              , 22 ,       13 , 'nature'          , 4       , False        , False        , (152,251,152) ),
    Label(  'sky'                  , 23 ,       14 , 'sky'             , 5       , False        , False        , ( 70,130,180) ),
    Label(  'person'               , 24 ,       15 , 'human'           , 6       , True         , False        , (220, 20, 60) ),
    Label(  'rider'                , 25 ,       16 , 'human'           , 6       , True         , False        , (255,  0,  0) ),
    Label(  'car'                  , 26 ,       17 , 'vehicle'         , 7       , True         , False        , (  0,  0,142) ),
    Label(  'truck'                , 27 ,       18 , 'vehicle'         , 7       , True         , False        , (  0,  0, 70) ),
    Label(  'bus'                  , 28 ,       19 , 'vehicle'         , 7       , True         , False        , (  0, 60,100) ),
    Label(  'caravan'              , 29 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0, 90) ),
    Label(  'trailer'              , 30 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0,110) ),
    Label(  'train'                , 31 ,       20 , 'vehicle'         , 7       , True         , False        , (  0, 80,100) ),
    Label(  'motorcycle'           , 32 ,       21 , 'vehicle'         , 7       , True         , False        , (  0,  0,230) ),
    Label(  'bicycle'              , 33 ,       22 , 'vehicle'         , 7       , True         , False        , (119, 11, 32) ),
    # Label(  'license plate'        , -1 ,       -1 , 'vehicle'         , 7       , False        , True         , (  0,  0,142) ),
]

labels = [ # injective mapping
    #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color
    Label(  'unlabeled'            ,  0 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    Label(  'ego vehicle'          ,  1 ,      255 , 'void'            , 0       , False        , True         , (  1,  0,  0) ),
    # Label(  'rectification border' ,  2 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'out of roi'           ,  3 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    # Label(  'static'               ,  4 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0) ),
    Label(  'dynamic'              ,  5 ,      255 , 'void'            , 0       , False        , True         , (111, 74,  0) ),
    Label(  'ground'               ,  6 ,        1 , 'void'            , 0       , False        , True         , ( 81,  0, 81) ),
    Label(  'road'                 ,  7 ,        0 , 'flat'            , 1       , False        , False        , (128, 64,128) ),
    Label(  'sidewalk'             ,  8 ,        1 , 'flat'            , 1       , False        , False        , (244, 35,232) ),
    Label(  'parking'              ,  9 ,      255 , 'flat'            , 1       , False        , True         , (250,170,160) ),
    Label(  'rail track'           , 10 ,      255 , 'flat'            , 1       , False        , True         , (230,150,140) ),
    Label(  'building'             , 11 ,        2 , 'construction'    , 2       , False        , False        , ( 70, 70, 70) ),
    Label(  'wall'                 , 12 ,        3 , 'construction'    , 2       , False        , False        , (102,102,156) ),
    Label(  'fence'                , 13 ,        4 , 'construction'    , 2       , False        , False        , (190,153,153) ),
    Label(  'guard rail'           , 14 ,        4 , 'construction'    , 2       , False        , True         , (180,165,180) ),
    Label(  'bridge'               , 15 ,        3 , 'construction'    , 2       , False        , True         , (150,100,100) ),
    Label(  'tunnel'               , 16 ,      255 , 'construction'    , 2       , False        , True         , (150,120, 90) ),
    Label(  'pole'                 , 17 ,        5 , 'object'          , 3       , False        , False        , (153,153,153) ),
    # Label(  'polegroup'            , 18 ,      255 , 'object'          , 3       , False        , True         , (153,153,153) ),
    Label(  'traffic light'        , 19 ,        6 , 'object'          , 3       , False        , False        , (250,170, 30) ),
    Label(  'traffic sign'         , 20 ,        7 , 'object'          , 3       , False        , False        , (220,220,  0) ),
    Label(  'vegetation'           , 21 ,        8 , 'nature'          , 4       , False        , False        , (107,142, 35) ),
    Label(  'terrain'              , 22 ,        9 , 'nature'          , 4       , False        , False        , (152,251,152) ),
    Label(  'sky'                  , 23 ,       10 , 'sky'             , 5       , False        , False        , ( 70,130,180) ),
    Label(  'person'               , 24 ,       11 , 'human'           , 6       , True         , False        , (220, 20, 60) ),
    Label(  'rider'                , 25 ,       12 , 'human'           , 6       , True         , False        , (255,  0,  0) ),
    Label(  'car'                  , 26 ,       13 , 'vehicle'         , 7       , True         , False        , (  0,  0,142) ),
    Label(  'truck'                , 27 ,       14 , 'vehicle'         , 7       , True         , False        , (  0,  0, 70) ),
    Label(  'bus'                  , 28 ,       15 , 'vehicle'         , 7       , True         , False        , (  0, 60,100) ),
    Label(  'caravan'              , 29 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0, 90) ),
    Label(  'trailer'              , 30 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0,110) ),
    Label(  'train'                , 31 ,       16 , 'vehicle'         , 7       , True         , False        , (  0, 80,100) ),
    Label(  'motorcycle'           , 32 ,       17 , 'vehicle'         , 7       , True         , False        , (  0,  0,230) ),
    Label(  'bicycle'              , 33 ,       18 , 'vehicle'         , 7       , True         , False        , (119, 11, 32) ),
    # Label(  'license plate'        , -1 ,       -1 , 'vehicle'         , 7       , False        , True         , (  0,  0,142) ),
]



# Label = namedtuple( 'Label' , [

#     'name'        , # The identifier of this label, e.g. 'car', 'person', ... .
#                     # We use them to uniquely name a class

#     'id'          , # An integer ID that is associated with this label.
#                     # The IDs are used to represent the label in ground truth images
#                     # An ID of -1 means that this label does not have an ID and thus
#                     # is ignored when creating ground truth images (e.g. license plate).
#                     # Do not modify these IDs, since exactly these IDs are expected by the
#                     # evaluation server.

#     'trainId'     , # Feel free to modify these IDs as suitable for your method. Then create
#                     # ground truth images with train IDs, using the tools provided in the
#                     # 'preparation' folder. However, make sure to validate or submit results
#                     # to our evaluation server using the regular IDs above!
#                     # For trainIds, multiple labels might have the same ID. Then, these labels
#                     # are mapped to the same class in the ground truth images. For the inverse
#                     # mapping, we use the label that is defined first in the list below.
#                     # For example, mapping all void-type classes to the same ID in training,
#                     # might make sense for some approaches.
#                     # Max value is 255!

#     'category'    , # The name of the category that this label belongs to

#     'categoryId'  , # The ID of this category. Used to create ground truth images
#                     # on category level.

#     'hasInstances', # Whether this label distinguishes between single instances or not

#     'ignoreInEval', # Whether pixels having this class as ground truth label are ignored
#                     # during evaluations or not

#     'color'       , # The color of this label
#     'customId',
#     ] )

# labels = [
#     #       name                     id    trainId   category            catId     hasInstances   ignoreInEval   color            customId
#     Label(  'unlabeled'            ,  0 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0),   3),
#     Label(  'ego vehicle'          ,  1 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0),   0),
#     # Label(  'rectification border' ,  2 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0),   0),
#     # Label(  'out of roi'           ,  3 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0),   0),
#     Label(  'static'               ,  4 ,      255 , 'void'            , 0       , False        , True         , (  0,  0,  0),  19),
#     Label(  'dynamic'              ,  5 ,      255 , 'void'            , 0       , False        , True         , (111, 74,  0),  20),
#     Label(  'ground'               ,  6 ,      255 , 'void'            , 0       , False        , True         , ( 81,  0, 81),  14),
#     Label(  'road'                 ,  7 ,        0 , 'flat'            , 1       , False        , False        , (128, 64,128),   7),
#     Label(  'sidewalk'             ,  8 ,        1 , 'flat'            , 1       , False        , False        , (244, 35,232),   8),
#     # Label(  'parking'              ,  9 ,      255 , 'flat'            , 1       , False        , True         , (250,170,160),   0),
#     Label(  'rail track'           , 10 ,      255 , 'flat'            , 1       , False        , True         , (230,150,140),  16),
#     Label(  'building'             , 11 ,        2 , 'construction'    , 2       , False        , False        , ( 70, 70, 70),   1),
#     Label(  'wall'                 , 12 ,        3 , 'construction'    , 2       , False        , False        , (102,102,156),  11),
#     Label(  'fence'                , 13 ,        4 , 'construction'    , 2       , False        , False        , (190,153,153),   2),
#     Label(  'guard rail'           , 14 ,      255 , 'construction'    , 2       , False        , True         , (180,165,180),  17),
#     Label(  'bridge'               , 15 ,      255 , 'construction'    , 2       , False        , True         , (150,100,100),  15),
#     # Label(  'tunnel'               , 16 ,      255 , 'construction'    , 2       , False        , True         , (150,120, 90),   0),
#     Label(  'pole'                 , 17 ,        5 , 'object'          , 3       , False        , False        , (153,153,153),   5),
#     # Label(  'polegroup'            , 18 ,      255 , 'object'          , 3       , False        , True         , (153,153,153),   0),
#     Label(  'traffic light'        , 19 ,        6 , 'object'          , 3       , False        , False        , (250,170, 30),  18),
#     Label(  'traffic sign'         , 20 ,        7 , 'object'          , 3       , False        , False        , (220,220,  0),  12),
#     Label(  'vegetation'           , 21 ,        8 , 'nature'          , 4       , False        , False        , (107,142, 35),   9),
#     Label(  'terrain'              , 22 ,        9 , 'nature'          , 4       , False        , False        , (152,251,152),  22),
#     Label(  'sky'                  , 23 ,       10 , 'sky'             , 5       , False        , False        , ( 70,130,180),  13),
#     Label(  'person'               , 24 ,       11 , 'human'           , 6       , True         , False        , (220, 20, 60),   4),
#     # Label(  'rider'                , 25 ,       12 , 'human'           , 6       , True         , False        , (255,  0,  0),   0),
#     Label(  'car'                  , 26 ,       13 , 'vehicle'         , 7       , True         , False        , (  0,  0,142),  10),
#     # Label(  'truck'                , 27 ,       14 , 'vehicle'         , 7       , True         , False        , (  0,  0, 70),   0),
#     # Label(  'bus'                  , 28 ,       15 , 'vehicle'         , 7       , True         , False        , (  0, 60,100),   0),
#     # Label(  'caravan'              , 29 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0, 90),   0),
#     # Label(  'trailer'              , 30 ,      255 , 'vehicle'         , 7       , True         , True         , (  0,  0,110),   0),
#     # Label(  'train'                , 31 ,       16 , 'vehicle'         , 7       , True         , False        , (  0, 80,100),   0),
#     # Label(  'motorcycle'           , 32 ,       17 , 'vehicle'         , 7       , True         , False        , (  0,  0,230),   0),
#     # Label(  'bicycle'              , 33 ,       18 , 'vehicle'         , 7       , True         , False        , (119, 11, 32),   0),
#     # Label(  'license plate'        , -1 ,       -1 , 'vehicle'         , 7       , False        , True         , (  0,  0,142) ),
# ]

id_tuples = [(getattr(label, 'trainId'), getattr(label, 'id'), getattr(label, 'color')) for label in labels]


# custom color palette

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


format_tuple = namedtuple('format_tuple', [ # store for each dataset format the matching names
    'image_dir',
    'ground_truth_dir',
    'image_file', # name for raw data images
    'ground_truth_file', # name for ground truth images
    ])

format_dict = {
    'cityscapes': format_tuple('leftImg8bit', 'gtFine', '_leftImg8bit.png', '_gtFine_labelTrainIds.png'),
    'anovox': format_tuple('RGB_IMG', 'SEMANTIC_IMG', 'RGB_IMG.png', 'SEMANTIC_IMG.png'),
}


# create new image with train id labels, from our dataset


# def label_TrainIds(id_img_path, id_type):
#     if id_type not in ['trainId', 'id']:
#         return
#     semantic_img = Image.open(id_img_path)
#     # semantic_array = iio.imread(id_img_path)
#     semantic_array = np.asarray(semantic_img)
#     semantic_array = semantic_array[:,:,:3]
#     height, width, channels = semantic_array.shape
#     new_id_array = np.ones((height, width,)) # create new grayscale image
#     # new_trainId_array = np.ones((height, width,))

#     # trainId_color_tuples = [(getattr(label, id_type), getattr(label, 'color')) for label in labels]

#     for cityscapes_train_id, cityscapes_id, semantic_color in id_tuples:
#         cityscapes_id = np.array(cityscapes_id)
#         # trainId = np.array(trainId)
#         semantic_color = np.array(semantic_color)

#         mask = np.all(semantic_array == semantic_color, axis=-1)
#         new_id_array[mask] = cityscapes_id
#         # new_trainId_array[mask] = trainId


#     new_id_array = new_id_array.astype(np.uint16)
#     # iio.imwrite(id_img_path, new_id_array)
#     new_id_img = Image.fromarray(new_id_array)
#     new_id_img = new_id_img.convert("L") # convert to grayscale
#     new_id_img.save(id_img_path)

    # new_id_img = Image.fromarray(new_id_array)
    # new_id_img = new_id_img.convert("L") # convert to grayscale
    # new_id_img.save(trainId_img_path)


def label_TrainIds(id_img_path, id_type):
    if id_type not in ['trainId', 'id']:
        return
    semantic_img = Image.open(id_img_path)
    # semantic_array = iio.imread(id_img_path)
    semantic_array = np.asarray(semantic_img)
    semantic_array = semantic_array[:,:,:3]
    height, width, channels = semantic_array.shape
    new_id_array = np.zeros((height, width,)) # create new grayscale image
    # new_trainId_array = np.zeros((height, width,))

    trainId_color_tuples = [(getattr(label, id_type), getattr(label, 'color')) for label in labels]

    for cityscapes_id, semantic_color in trainId_color_tuples:
        cityscapes_id = np.array(cityscapes_id)
        # trainId = np.array(cityscapes_train_id)
        semantic_color = np.array(semantic_color)

        mask = np.all(semantic_array == semantic_color, axis=-1)
        new_id_array[mask] = cityscapes_id
        # new_trainId_array[mask] = trainId


    new_id_array = new_id_array.astype(np.uint16)
    # iio.imwrite(id_img_path, new_id_array)
    new_id_img = Image.fromarray(new_id_array)
    new_id_img = new_id_img.convert("L") # convert to grayscale
    new_id_img.save(id_img_path)

    # new_id_img = Image.fromarray(new_id_array)
    # new_id_img = new_id_img.convert("L") # convert to grayscale
    # new_id_img.save(trainId_img_path)



def create_file_name(type, file_path):
    """
    file path in format Final_Output/ScenarioId/ImageType/ImageType_FrameId.png
    """

    img_file_name = os.path.basename(file_path).replace('.png','')

    # if not args.cityscapes_format:
    #     return img_file_name
    # scenario_id = os.path.split(os.path.split(file_path)[0])[0]
    file_path = os.path.normpath(file_path)
    path_splits = file_path.split(os.sep)
    scenario_id = path_splits[-3] # ScenarioId
    scenario_id = scenarioId_refactoring(scenario_id)

    file_name_arr = img_file_name.split('_') # get number of frame id
    image_type = file_name_arr[0]
    frame_id = file_name_arr[2]

    if type == "raw":
        new_file_name = scenario_id + "_0000000_" + frame_id.rjust(6,'0') + "_leftImg8bit.png"
        return new_file_name

    elif type == "trainId":
        new_file_name = scenario_id + "_0000000_" + frame_id.rjust(6,'0') + "_gtFine_labelTrainIds.png"
        return new_file_name
    elif type == "id":
        new_file_name = scenario_id + "_0000000_" + frame_id.rjust(6,'0') + "_gtFine_labelIds.png"
        return new_file_name
    elif type == "instance":
        new_file_name = scenario_id + "_0000000_" + frame_id.rjust(6,'0') + "_gtFine_instanceIds.png"
        return new_file_name

    else:
        return None # some exception


def move_to_cityscapes(anovox_root, cityscapes_raw_dir, cityscapes_gt_dir):
    split = 'train'
    file_count = 0
    for scenario in tqdm(sorted(os.listdir(anovox_root))):
        file_count += 1
        scenario_dir = os.path.join(anovox_root, scenario)
        scenario_id = os.path.basename(scenario_dir)
        if scenario_dir == os.path.join(anovox_root, "Scenario_Configuration_Files") or scenario_dir == os.path.join(anovox_root, "cityscapes_2975") or scenario_dir == os.path.join(anovox_root, "cityscapes_19130"):
            continue
        RGB_dir = os.path.join(scenario_dir, "RGB_IMG")
        SEM_dir = os.path.join(scenario_dir, "SEMANTIC_IMG")

        if file_count > args.train_split_size + 100: # only so much needed for first evaluation (100 * 5)
            break
        # if file_count > 744: # for 4 images per scenario
        # if file_count > 3:
        if file_count > args.train_split_size: # 595 * 5 = 2975
        # if file_count > 3826: # 595 * 5 = 2975
            split = 'val'
        _cityscapes_raw_dir = os.path.join(cityscapes_raw_dir, split)
        _cityscapes_gt_dir = os.path.join(cityscapes_gt_dir, split)

        cityscapes_scenario_dir = scenarioId_refactoring(scenario_id)


        for rgb_img in os.listdir(RGB_dir):
            rgb_img_path = os.path.join(RGB_dir, rgb_img)
            _file_name = create_file_name("raw", rgb_img_path)
            _file_path = os.path.join(_cityscapes_raw_dir, cityscapes_scenario_dir,_file_name) # should be cityscapes/leftImg8Bit/ScenarioId/filename
            shutil.copyfile(rgb_img_path, _file_path) # move rgb img file from anovox to cityscapes

        split_dict = {'train': 'trainId', 'val': 'id'}
        for sem_img in os.listdir(SEM_dir):
            sem_img_path = os.path.join(SEM_dir, sem_img)
            id_file_name = create_file_name('id', sem_img_path)
            id_file_path = os.path.join(_cityscapes_gt_dir, cityscapes_scenario_dir, id_file_name)
            shutil.copyfile(sem_img_path, id_file_path) # move semantic img file from anovox to cityscapes
            # label_TrainIds(_file_path) # set new train Id labels
            trainId_file_name = create_file_name('trainId', sem_img_path)
            trainId_file_path = os.path.join(_cityscapes_gt_dir, cityscapes_scenario_dir, trainId_file_name)
            shutil.copyfile(sem_img_path, trainId_file_path) # move semantic img file from anovox to cityscapes

            instance_file_name = create_file_name('instance', sem_img_path)
            instance_file_path = os.path.join(_cityscapes_gt_dir, cityscapes_scenario_dir, instance_file_name)
            shutil.copyfile(sem_img_path, instance_file_path) # move semantic img file from anovox to cityscapes

        if args.cityscapes_format:
            # for path, subdirs, files in os.walk(_cityscapes_gt_dir): # relabel all labelTrainIds
            #     print(path)
            #     for gt_img in files:
            #         label_TrainIds(os.path.join(path, gt_img), split)
            _cityscapes_scenario_dir = os.path.join(_cityscapes_gt_dir, cityscapes_scenario_dir)
            for image in os.listdir(_cityscapes_scenario_dir):
                image_path = os.path.join(_cityscapes_scenario_dir, image)
                # print(image_path)
                name_split = image.split('_')
                if 'labelTrainIds.png' in name_split:
                    label_TrainIds(image_path, 'trainId')
                elif 'labelIds.png' in name_split:
                    label_TrainIds(image_path, 'id')
                # label_TrainIds(image_path)



def scenarioId_refactoring(scenario_id):
    scenario_id = scenario_id.replace('_', '')
    scenario_id = scenario_id.replace('-', '')  # some refactoring for the scenario id
    return scenario_id


def create_cityscapes_folders(root, train_scenarios_amount):
    print("root", root)
    root_prev, _ = os.path.split(root)
    print("root prev ", root_prev)

    # Scenario ID will replace city names.
    cityscapes_dir = os.path.join(root_prev, "cityscapes_2975_19injective")
    os.mkdir(cityscapes_dir)
    os.chdir(cityscapes_dir)

    raw_data_dir = os.path.join(cityscapes_dir, "leftImg8bit")
    gt_data_dir = os.path.join(cityscapes_dir, "gtFine")
    os.mkdir(raw_data_dir)
    os.mkdir(gt_data_dir)
    os.chdir(raw_data_dir)
    raw_data_train_dir = os.path.join(raw_data_dir, "train")
    raw_data_val_dir = os.path.join(raw_data_dir, 'val')
    os.mkdir(raw_data_train_dir)
    os.mkdir(raw_data_val_dir)

    gt_data_train_dir = os.path.join(gt_data_dir, "train")
    gt_data_val_dir = os.path.join(gt_data_dir, 'val')
    os.chdir(gt_data_dir)
    os.mkdir(gt_data_train_dir)
    os.mkdir(gt_data_val_dir)

    counter = 0
    for scenario_dir in sorted(os.listdir(root)):
        if scenario_dir == "Scenario_Configuration_Files" or scenario_dir == "cityscapes_2975":
            continue
        scenario_id = os.path.basename(scenario_dir)
        new_scenario_dir = scenarioId_refactoring(scenario_id)

        # if len(os.listdir(raw_data_train_dir)) >= 744: # create val folders for 4
        # if len(os.listdir(raw_data_train_dir)) >= 3: # create val folders
        counter += 1
        if counter > train_scenarios_amount + 100: # 100 is size of val split
            break

        if len(os.listdir(raw_data_train_dir)) >= train_scenarios_amount: # create val folders for 5
        # if len(os.listdir(raw_data_train_dir)) >= 3826: # create val folders for 5

            os.chdir(raw_data_val_dir)
            os.mkdir(new_scenario_dir)

            os.chdir(gt_data_val_dir)
            os.mkdir(new_scenario_dir)

        else:
            os.chdir(raw_data_train_dir)
            os.mkdir(new_scenario_dir)

            os.chdir(gt_data_train_dir)
            os.mkdir(new_scenario_dir)


    return cityscapes_dir, raw_data_dir, gt_data_dir

def get_anovox_folders(dataset_root):
    root_prev, _ = os.path.split(dataset_root)
    os.chdir(root_prev)
    new_dataset_root = os.path.join(root_prev, 'AnoVox')
    os.rename(dataset_root, new_dataset_root)

    image_root = os.path.join(new_dataset_root, format_dict['anovox'].image_dir)
    gt_root = os.path.join(new_dataset_root, format_dict['anovox'].ground_truth_dir)

    return new_dataset_root, image_root, gt_root



parser = argparse.ArgumentParser(description='OOD Evaluation')

parser.add_argument('--dataset_path', type=str, default= '/home/tes_unreal/Desktop/Dataset_BA/Final_Output_22_09-08_11_2023', # '/home/lukasnroessler/dataset/NormalityEnv/Normality_Sample',
                    help= """Name the path of dataset to be converted""")

parser.add_argument('--cityscapes_format', action='store_true',
                    help="""If passed, converts anomaly data of AnoVox into cityscapes format, where ground truth is labeled via train ids.""")

parser.add_argument('--train_split_size', type=int, default=595 , # '/home/lukasnroessler/dataset/NormalityEnv/Normality_Sample',
                    help= """number of scenarios for train split""")


args = parser.parse_args()


def main(args):
    dataset_root = args.dataset_path
    # if (not os.path.exists(dataset_root)):
    #     print("no valid path")
    # else:
    root_prev, _ = os.path.split(dataset_root)
    # new_root = os.path.join(root_prev, 'AnoVox')

    os.chdir(root_prev)
        # anovox_dir = os.path.join(dataset_root, "FinalOutput") # rename this later
    # if args.cityscapes_format:
    dataset_format = format_dict['cityscapes']
    cityscapes_dir, raw_data_dir, gt_data_dir = create_cityscapes_folders(dataset_root, args.train_split_size)
    move_to_cityscapes(dataset_root, raw_data_dir, gt_data_dir)
    # else:
    #     dataset_format = format_dict['anovox']
    #     anovox_dir, raw_data_dir, gt_data_dir = get_anovox_folders(dataset_root)

    return


if __name__ == "__main__":
    # args = sys.argv[1:]
    # print("args", args)
    # args = ['/home/lukasnroessler/Projects/voxelworld/Data/Outputs/Final_Output_18_04-16_08_2023']
    main()
