# Adaptive Image Resolution Compression and Format Conversion

[简体中文](README.md) | English

Attention: This README is translate by ChatGPT, and the author of this project is not a native English speaker. If you find any grammatical mistakes, please feel free to open an issue or pull request.

## What is this?

This is a script that utilizes the binary search algorithm to automatically (lossy) compress image resolution and convert image formats, reducing the file size of images for scenarios such as blogs.

## Dependencies

```bash
pip install pillow tqdm
```

## Usage

Modify the parameters in the code and run the script [auto-resize.py](./auto-resize.py).

## Instructions and Parameter Meanings

### picture_folder

The path to the image folder. If you want to compress all images in a folder, set this parameter to the path of your image folder. If you only want to compress a single image, for example, if the image you want to compress is `C:\Users\<YourUsername>\Desktop\1.jpg`, then this parameter should be `C:\Users\<YourUsername>\Desktop`.

Note that subfolders inside the picture_folder will not be compressed recursively. For example, if `C:\Users\<YourUsername>\Desktop` has a subfolder `C:\Users\<YourUsername>\Desktop\subfolder`, the images in `C:\Users\<YourUsername>\Desktop\subfolder` will not be compressed.

### save_folder

The path to save the compressed images. If the folder does not exist, it will be created automatically. If the folder is not empty, it will output “输出文件夹不为空，请清空后重试。”（The output folder is not empty. Please clear it and try again.） and exit.

### image_name

The file name of the image to compress. If you want to compress all images in a folder (with `is_all_folder` set to `True`), this parameter will be ignored. If you only want to compress a single image, for example, if the image you want to compress is `C:\Users\<YourUsername>\Desktop\1.jpg`, then this parameter should be `1.jpg`. The supported image formats are `jpg`, `png`, and `webp` (other formats have not been tested yet).

### extension

The format of the compressed image. It supports `jpg`, `png`, and `webp`.

### suffix

The suffix to be added to the compressed image file name. For example, if the image you want to compress is `C:\Users\<YourUsername>\Desktop\1.jpg`, you set save_folder to `C:\Users\<YourUsername>\Desktop\output`, extension to `webp`, and `suffix` to `-compressed`, then the compressed image will be saved as `C:\Users\<YourUsername>\Desktop\output\1-compressed.webp`.

### _quality

The quality of the compressed image. The range is 1-100, where a higher value indicates higher quality. It is recommended to use 80-90 to achieve a good balance between compression and image quality.

### target_size_kb_upper

The upper limit of the compressed image file size in kilobytes (KB). Used in conjunction with `target_size_kb_lower` below.

### target_size_kb_lower

The lower limit of the compressed image file size in kilobytes (KB). The file size of the compressed image will be within this upper and lower limit.

A smaller range between the upper and lower limits will result in a longer time to find a resolution that meets the size requirements using binary search. If you don't require precise file sizes, you can widen the limits to reduce the running time.

### is_all_folder

Whether to compress all images in the folder. If you want to compress all images in a folder, set this parameter to `True` and ignore `image_name`. If you only want to compress a single image, for example, if the image you want to compress is `C:\Users\<YourUsername>\Desktop\1.jpg`, set this parameter to `False`.

### width_lower_limit

The lower limit of the image resolution width in pixels. Used in conjunction with `height_lower_limit` below.

### height_lower_limit

The lower limit of the image resolution height in pixels. These two parameters only take effect when `is_all_folder` is set to `True`.

The purpose of these two parameters is as follows:

1. To exclude images from the compression/output folder that do not meet the resolution size requirement. If there are images with resolutions smaller than the specified limits in the image folder to be compressed, and you do not want to include them in the output folder after compression/format conversion, you can set these two parameters. This way, those images will be ignored. For example, if you set `width_lower_limit` to 1000 and `height_lower_limit` to 1000, all images with resolutions smaller than 1000x1000 in the input folder will be ignored.
2. To handle images that do not meet the minimum resolution after compression, see the `how_to_deal_with_under_resolution` parameter.

### is_resolution_limit_fit_vertical

Whether to recognize and adjust portrait-oriented images to match the minimum resolution requirement. For example, if you set `width_lower_limit` to 1920 and `height_lower_limit` to 1080, and there is an image with a resolution of 1200x1920 (a portrait image), if `is_resolution_limit_fit_vertical` is set to `True`, the minimum resolution will be adjusted to 1080x1920 to include the portrait image. If `is_resolution_limit_fit_vertical` is set to `False`, the portrait image will be ignored due to insufficient width (below 1920).

### how_to_deal_with_under_resolution

The action to take when the compressed image resolution is lower than the minimum resolution.

Let's assume a scenario where the target compressed size is 360-400 KB, and the minimum resolution limit is 1920x1200. Now, there is an image with an original resolution of 2000x1333, size of 3.24 MB, and a compressed resolution of 1212x808, size of 371 KB. Although the compressed image size meets the requirement, the resolution is lower than the minimum. In this case, you can choose:

1. `UnderResolutionPolicy.DoNothing`: Keep the compressed image with resolution 1212x808 and size 371 KB without any further action.
2. `UnderResolutionPolicy.Delete`: Delete the compressed image with resolution 1212x808 and size 371 KB.
3. `UnderResolutionPolicy.FitResolutionLimit`: Discard the requirement of 360-400 KB and compress the image to a resolution that better fits the minimum resolution while preserving the aspect ratio. The calculated resolution that fits the minimum resolution and maintains the aspect ratio is 1920x1280, with a compressed size of 775 KB.

### try_limit

The number of attempts for the binary search algorithm, set to 20 by default. If the algorithm exceeds this number of attempts without finding a resolution that meets the size requirement, the program will stop searching and retain the last found resolution.
