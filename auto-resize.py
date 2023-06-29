from enum import Enum
from PIL import Image
from tqdm import tqdm
import os
import time
import math

class UnderResolutionPolicy(Enum):
    DoNothing = "什么都不做",
    Delete = "删除",
    FitResolutionLimit = "忽略大小限制",

# 必要修改：改成你的 被压缩图片 所在的文件夹
picture_folder = r"E:\图片与视频\pixiv"
picture_folder = r"C:\Users\Eterance\Pictures\Cyberpunk 2077"
# 必要修改：改成你的 压缩后图片 保存的文件夹
save_folder = r"C:\Users\Eterance\Desktop\2077"
# 必要修改：改成你的 被压缩图片 的文件名
image_name = "photomode_11012021_160505.png"
# 可选修改：改成你的 压缩后图片 的格式，支持 jpg、png、webp
extension = 'webp'
# 可选修改：改成你的 压缩后图片 的后缀，例如 “-已缩小”。如果不需要后缀，改成空字符串 ""
suffix = "-已缩小"
# 可选修改：改成你的 压缩后图片 的质量，范围 0-100，越大越清晰，但是文件越大。推荐 90。
_quality = 90
# 可选修改：改成你的 压缩后图片 的目标大小上限，单位 KB。
target_size_kb_upper = 4000
# 可选修改：改成你的 压缩后图片 的目标大小下限，单位 KB。不得大于上限。
target_size_kb_lower = 3600
# 如果为 True，则会将 picture_folder 文件夹下的所有图片都压缩，忽视 image_name。
is_all_folder = False
# 仅在 is_all_folder 为 True 时生效。原图分辨率大于这个值的图片才会被压缩。如果为0，则不限制。
width_lower_limit = 1920
height_lower_limit = 1200
# 门槛是否自适应竖图
is_resolution_limit_fit_vertical = True
# 当压缩后的图片小于门槛时要怎么操作
how_to_deal_with_under_resolution = UnderResolutionPolicy.FitResolutionLimit
# 二分法的尝试次数上限，若超过这个次数仍无法达到目标大小，则会使用最后一次的结果。
try_limit = 20

# 下面的代码不懂就不要改

def try_remove(file_path, times = 3):
    for _time in range(times):
        try:
            os.remove(file_path)
            return
        except Exception as e:
            time.sleep(0.1 * (_time + 1))
    raise Exception(f"尝试了 {_time} 次仍无法删除 {file_path}. {e}")

def is_under_res_limit(width, height):
    if is_resolution_limit_fit_vertical == False:
        if width < width_lower_limit or height < height_lower_limit:
            return True, width_lower_limit, height_lower_limit
        else:
            return False, 0, 0
    else:
        # non vertical image
        if width >= height:
            if width < width_lower_limit or height < height_lower_limit:
                return True, width_lower_limit, height_lower_limit
            else:
                return False, 0, 0
        # vertical image
        else:
            if width < height_lower_limit or height < width_lower_limit:
                return True, height_lower_limit, width_lower_limit
            else:
                return False, 0, 0

if (target_size_kb_lower > target_size_kb_upper): 
    print("目标大小下限不得大于上限。")
    exit()
if (target_size_kb_lower < 0 or target_size_kb_upper < 0): 
    print("目标大小不得小于0。")
    exit()
if _quality < 1 or _quality > 100: 
    print("质量不得小于1或大于100。")
    exit()
if width_lower_limit < 0 or height_lower_limit < 0: 
    print("分辨率不得小于0。")
    exit()

first_start_time = time.time()

# 检查并创建输出文件夹
if not os.path.exists(save_folder): 
    os.makedirs(save_folder, exist_ok=True)

# 如果输出不为空，则结束
if len(os.listdir(save_folder)) != 0 and is_all_folder == True:
    print("输出文件夹不为空，请清空后重试。")
    exit()

original_image_names = []
if (is_all_folder == False):
    if not os.path.exists(os.path.join(picture_folder, image_name)):
        print(f"没有找到 {image_name}")
        exit()
    original_image_names = [image_name]
# 获取所有图片的文件名。不递归
else: 
    for root, dirs, files in os.walk(picture_folder):
        for file in files:
            if (file.endswith(".jpg") or file.endswith(".png") or file.endswith(".webp")):
                original_image_names.append(file)
        break

if len(original_image_names) == 0:
    print("没有找到图片")
    exit()

print(f"开始压缩 {picture_folder} 文件夹下的图片（{len(original_image_names)} 张）。宽度门槛为 {width_lower_limit}, 高度门槛为 {height_lower_limit}, 目标大小为 {target_size_kb_lower} KB - {target_size_kb_upper} KB，格式为 {extension}，质量为 {_quality}，后缀为 {suffix}。")

success_count = 0
total_disk_cost = 0

for _image_name in tqdm(original_image_names):
    original_file_path = os.path.join(picture_folder, _image_name)
    multiple_upper = 1.00
    multiple_lower = 0.10
    current_multiple = 1
    disk_cost = 0
    start_time = time.time()
    try:
        image_file = Image.open(original_file_path)
    except Exception as e:
        print(f"无法打开 {_image_name}，跳过。")
        continue
    image_file = image_file.convert("RGB") # PNG转换为RGB模式，否则无法保存为jpg
    width, height = image_file.size
    if is_all_folder == True:
        is_under, _, _ =is_under_res_limit(width, height)
        if is_under:
            print(f"{_image_name} 边长不符合要求，跳过")
            continue
    target_file_name = os.path.join(save_folder, f"{_image_name.split('.')[0]}{suffix}.{extension}")

    # 先尝试原尺寸压缩，如果满足要求就不用缩小了
    image_file.save(target_file_name, quality= _quality)
    file_size = os.path.getsize(target_file_name)
    disk_cost += file_size
    if (file_size < target_size_kb_upper * 1024):
        print(f"{_image_name} 分辨率未改变，大小为 {int(file_size/1024)} KB，耗时 {round(time.time() - start_time, 2)} s，磁盘总写入 {round(disk_cost/1024/1024, 3)} MB")
    else:
        try_remove(target_file_name)
        # 二分法寻找最适合压缩的分辨率
        tried_count = 0
        while (current_multiple > 0):
            if tried_count > try_limit:
                break
            tried_count += 1
            current_multiple = (multiple_upper + multiple_lower)/2
            img_resized = image_file.resize((int(width*current_multiple),  int(height*current_multiple)), Image.LANCZOS)
            img_resized.save(target_file_name, quality= _quality)
            file_size = os.path.getsize(target_file_name)
            disk_cost += file_size
            if (file_size > target_size_kb_upper * 1024):
                multiple_upper = current_multiple
                try_remove(target_file_name)
            elif (file_size < target_size_kb_lower * 1024):
                multiple_lower = current_multiple
                try_remove(target_file_name)
            else:
                break
        
        resized_width, resized_height = img_resized.size
        pixel_percentage = round((resized_width * resized_height) / (width * height)* 100, 2)
        edge_percentage = round((resized_width / width) * 100, 2)
        
        result, true_width_limit, true_height_limit = is_under_res_limit(resized_width, resized_height)
        if result == True:
            if (how_to_deal_with_under_resolution == UnderResolutionPolicy.Delete): 
                try_remove(target_file_name)
                print(f"[边长小于门槛，将不会被保留] 已经将 {_image_name} 的分辨率缩小到 {resized_width}x{resized_height} ({edge_percentage}% 边长，{(pixel_percentage)}% 像素)，大小为 {int(file_size/1024)} KB，尝试 {tried_count} 次，耗时 {round(time.time() - start_time, 2)} s，磁盘总写入 {round(disk_cost/1024/1024, 3)} MB")
            elif (how_to_deal_with_under_resolution == UnderResolutionPolicy.FitResolutionLimit):
                try_remove(target_file_name)
                # 选取较大的缩放比例
                bigger_multiple = max(true_width_limit / resized_width, true_height_limit / resized_height)
                # 重新计算分辨率，向上取整
                img_resized = image_file.resize((math.ceil(resized_width*bigger_multiple),  math.ceil(resized_height*bigger_multiple)), Image.LANCZOS)
                img_resized.save(target_file_name, quality= _quality)
                final_file_size = os.path.getsize(target_file_name)
                disk_cost += final_file_size
                resized_width2, resized_height2 = img_resized.size
                                
                pixel_percentage2 = round((resized_width2 * resized_height2) / (width * height)* 100, 2)
                edge_percentage2 = round((resized_width2 / width) * 100, 2)
                print(f"[边长小于门槛，忽略大小限制] 试图将 {_image_name} 的分辨率缩小到 {resized_width}x{resized_height} ({edge_percentage}% 边长，{(pixel_percentage)}% 像素)，大小为 {int(file_size/1024)} KB，尝试 {tried_count} 次。由于边长小于门槛，重新计算分辨率为 {resized_width2}x{resized_height2} ({edge_percentage2}% 边长，{pixel_percentage2}% 像素)，大小为 {int(final_file_size/1024)} KB，耗时 {round(time.time() - start_time, 2)} s，磁盘总写入 {round(disk_cost/1024/1024, 3)} MB")
                success_count += 1
            else:        
                print(f"[边长小于门槛，但设置为忽略] 已经将 {_image_name} 的分辨率缩小到 {resized_width}x{resized_height} ({edge_percentage}% 边长，{(pixel_percentage)}% 像素)，大小为 {int(file_size/1024)} KB，尝试 {tried_count} 次，耗时 {round(time.time() - start_time, 2)} s，磁盘总写入 {round(disk_cost/1024/1024, 3)} MB")
                success_count += 1
        else:
            pixel_percentage = round((resized_width * resized_height) / (width * height), 2)            
            print(f"已经将 {_image_name} 的分辨率缩小到 {resized_width}x{resized_height} ({edge_percentage}% 边长，{(pixel_percentage)}% 像素)，大小为 {int(file_size/1024)} KB，尝试 {tried_count} 次，耗时 {round(time.time() - start_time, 2)} s，磁盘总写入 {round(disk_cost/1024/1024, 3)} MB")
            success_count += 1
    total_disk_cost += disk_cost

print(f"压缩完成，共压缩 {success_count} 张图片，耗时 {round(time.time() - first_start_time, 2)} s，磁盘总写入 {round(total_disk_cost/1024/1024, 3)} MB")