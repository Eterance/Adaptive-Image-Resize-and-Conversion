# 自适应图片分辨率压缩与格式转换

简体中文 | [English](./README.en.md)

## 这是什么？

这是一个使用二分查找算法，自动（有损）压缩图片分辨率与转换图片格式的脚本，以缩小图片文件的体积，适用于博客等场景。

## 安装依赖

```bash
pip install pillow tqdm
```

## 使用方法

直接修改代码里的参数，然后运行 [auto-resize.py](./auto-resize.py) 即可。

## 使用说明与参数含义

### picture_folder

图片文件夹路径。如果你是要压缩一整个文件夹下的图片，那么这个参数就是你的图片文件夹路径；如果你只压缩一张图片，比如你要压缩的图片是`C:\Users\<你的用户名>\Desktop\1.jpg`，那么这个参数就是`C:\Users\<你的用户名>\Desktop`。

请注意，不会递归压缩子文件夹里的图片，也就是说，如果 `C:\Users\<你的用户名>\Desktop` 下有一个子文件夹 `C:\Users\<你的用户名>\Desktop\subfolder`，那么 `C:\Users\<你的用户名>\Desktop\subfolder` 下的图片不会被压缩。

### save_folder

压缩后的图片保存路径。不存在的话会自动创建。如果该文件夹下不是空的，会输出“输出文件夹不为空，请清空后重试。”并退出。

### image_name

要压缩的图片文件名。如果你是要压缩一整个文件夹下的图片（`is_all_folder` 设置为 `True`），那么这个参数将会被程序忽略；如果你只压缩一张图片，比如你要压缩的图片是`C:\Users\<你的用户名>\Desktop\1.jpg`，那么这个参数就是`1.jpg`。图片的种类支持 `jpg`，`png` 和 `webp` （其他格式尚未测试）。

### extension

压缩后的图片格式。支持 `jpg`，`png` 和 `webp`。

### suffix

压缩后会被添加到图片文件名后缀。比如你要压缩的图片是`C:\Users\<你的用户名>\Desktop\1.jpg`，你设置的 `save_folder` 是 `C:\Users\<你的用户名>\Desktop\output`，`extension` 是 `webp`，`suffix` 是 `-已缩小`，那么压缩后的图片会被保存为 `C:\Users\<你的用户名>\Desktop\output\1-已缩小.webp`。

### _quality

压缩后的图片质量。范围是 1-100，数值越大质量越高，推荐 80-90，在这个范围内能在取得较好的压缩效果的同时保证图片质量和原图相差无几。

### target_size_kb_upper

压缩后的图片文件大小上限。单位是 KB。与下面的 `target_size_kb_lower` 一起配合使用。

### target_size_kb_lower

压缩后的图片文件大小下限。单位是 KB。压缩后的图片文件大小会在这个上下限之内。

上下限区间越小，二分查找到符合要求的分辨率所花费的时间越长。如果你对大小要求不是非常精准，可以适当放宽上下限以减少运行时间。

### is_all_folder

是否压缩整个文件夹下的图片。如果你是要压缩一整个文件夹下的图片，那么这个参数应设为 `True`，并忽略 `image_name`；如果你只压缩一张图片，比如你要压缩的图片是`C:\Users\<你的用户名>\Desktop\1.jpg`，那么这个参数应设为 `False`。

### width_lower_limit

图片分辨率宽度下限，单位是像素。与下面的 `height_lower_limit` 一起配合使用。

### height_lower_limit

图片分辨率高度下限，单位是像素。这两个参数只有在 `is_all_folder` 为 `True` 时才会生效。

这两个参数的作用：

1. 用于在压缩前剔除掉不符合该分辨率尺寸要求的图片。当你要压缩的图片文件夹里有一些分辨率过小的图片，你不想把压缩/转换格式到你的输出文件夹中，那么你可以设置这两个参数，这样这些图片就会被忽略。比如，你设置了 `width_lower_limit` 为 1000，`height_lower_limit` 为 1000，那么输入文件夹内所有分辨率小于 1000x1000 的图片就会被忽略。
2. 用于处理压缩后不符合该最低分辨率的图片，详见 `how_to_deal_with_under_resolution` 参数。

### is_resolution_limit_fit_vertical

是否识别并适应竖屏图片来匹配最低分辨率的要求。比如，如果你设置了 `width_lower_limit` 为 1920，`height_lower_limit` 为 1080，现在有一张图片是 1200x1920 的，也就是说这是一张竖图。如果 `is_resolution_limit_fit_vertical` 为 `True`，那么最低分辨率也会适配竖图为 1080x1920，这样这张竖图就处于最低分辨率的要求之上；如果 `is_resolution_limit_fit_vertical` 为 `False`，那么这张竖图因为宽度不足 1920 而被忽略。

### how_to_deal_with_under_resolution

当压缩后的图片分辨率小于最低分辨率时的处理方式。

我们假设一个场景：图片的目标压缩大小是 360-400 KB，最低分辨率限制为 1920x1200。现在有一张图片，原分辨率是 2000x1333，大小是 3.24 MB，压缩后分辨率是 1212x808，大小为 371 KB。虽然压缩后的图片大小符合要求，但是分辨率却小于最低分辨率。这时候，你可以选择：

1. `UnderResolutionPolicy.DoNothing`：保留这个 1212x808，大小为 371 KB 的压缩后图片，不做任何处理。
2. `UnderResolutionPolicy.Delete`：删除这个 1212x808，大小为 371 KB 的压缩后图片。
3. `UnderResolutionPolicy.FitResolutionLimit`：放弃  360-400 KB 的限制，而是把图片压缩到更好适应最低分辨率的大小。计算得到既适应最低分辨率，又能保留图片长宽比的分辨率是 1920x1280，压缩后大小为 775 KB。

### try_limit

二分查找法的尝试次数，默认为 20。如果超过这个次数还没找到符合大小要求的分辨率，那么程序会放弃继续搜索，直接保留最后一次查找到的分辨率。
