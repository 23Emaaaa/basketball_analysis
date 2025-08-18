
basketball-player-detection-2 - v1 v1.1-Unified-Aug3x-NoMosaic-17-08-2025
==============================

This dataset was exported via roboflow.com on August 18, 2025 at 3:50 PM GMT

Roboflow is an end-to-end computer vision platform that helps you
* collaborate with your team on computer vision projects
* collect & organize images
* understand and search unstructured image data
* annotate, and create datasets
* export, train, and deploy computer vision models
* use active learning to improve your dataset over time

For state of the art Computer Vision training notebooks you can use with this dataset,
visit https://github.com/roboflow/notebooks

To find over 100k other datasets and pre-trained models, visit https://universe.roboflow.com

The dataset includes 4286 images.
Players are annotated in COCO format.

The following pre-processing was applied to each image:
* Auto-orientation of pixel data (with EXIF-orientation stripping)
* Resize to 640x640 (Stretch)

The following augmentation was applied to create 3 versions of each source image:
* 50% probability of horizontal flip
* Random brigthness adjustment of between -25 and +25 percent
* Random Gaussian blur of between 0 and 2 pixels
* Salt and pepper noise was applied to 0.5 percent of pixels


