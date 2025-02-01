from PIL import Image
import os
from typing import List, Tuple
import glob

class ImageProcessor:
    def __init__(self, input_dir: str):
        self.input_dir = input_dir
        
    def batch_rename(self, prefix: str, start_num: int = 1) -> None:
        """批量重命名图片"""
        files = glob.glob(os.path.join(self.input_dir, "*.[jJ][pP][gG]")) + \
                glob.glob(os.path.join(self.input_dir, "*.[pP][nN][gG]"))
        
        for i, old_path in enumerate(files, start=start_num):
            directory = os.path.dirname(old_path)
            extension = os.path.splitext(old_path)[1]
            new_name = f"{prefix}_{str(i).zfill(2)}{extension}"
            new_path = os.path.join(directory, new_name)
            os.rename(old_path, new_path)
            print(f"已重命名: {old_path} -> {new_path}")

    def batch_resize(self, target_width: int) -> None:
        """批量修改图片尺寸，保持原始比例"""
        files = glob.glob(os.path.join(self.input_dir, "*.[jJ][pP][gG]")) + \
                glob.glob(os.path.join(self.input_dir, "*.[pP][nN][gG]"))
        
        for file_path in files:
            with Image.open(file_path) as img:
                # 计算等比例缩放后的高度
                ratio = target_width / img.width
                target_height = int(img.height * ratio)
                
                resized_img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                resized_img.save(file_path)
                print(f"已调整尺寸: {file_path} -> {target_width}x{target_height}")

    def merge_images_vertical(self, output_path: str) -> None:
        """将多张图片垂直合并为长图"""
        files = glob.glob(os.path.join(self.input_dir, "*.[jJ][pP][gG]")) + \
                glob.glob(os.path.join(self.input_dir, "*.[pP][nN][gG]"))
        files.sort()  # 确保图片按名称顺序合并
        
        if not files:
            print("未找到图片文件")
            return
            
        # 打开所有图片
        images = [Image.open(f) for f in files]
        
        # 计算合并后的尺寸
        width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        
        # 创建新图片
        merged_image = Image.new('RGB', (width, total_height))
        
        # 垂直拼接图片
        current_height = 0
        for img in images:
            # 如果图片宽度小于最大宽度，居中放置
            x_offset = (width - img.width) // 2
            merged_image.paste(img, (x_offset, current_height))
            current_height += img.height
            img.close()
        
        # 保存结果
        merged_image.save(output_path)
        print(f"已合并图片到: {output_path}")

# 使用示例
if __name__ == "__main__":
    processor = ImageProcessor("./images")  # 指定输入图片目录
    
    # 批量重命名（将图片重命名为 photo_1.jpg, photo_2.jpg 等）
    processor.batch_rename("商详")
    
    # 批量调整尺寸
    processor.batch_resize(750)
    
    # 合并为长图
    processor.merge_images_vertical("merged_output.jpg") 