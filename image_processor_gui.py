import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from image_processor import ImageProcessor
import os

class ImageProcessorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("图片批处理工具 v1.0 By Kevin")
        self.root.geometry("600x400")
        self.processor = None
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 选择目录
        ttk.Label(self.main_frame, text="图片目录:").grid(row=0, column=0, sticky=tk.W)
        self.dir_path = tk.StringVar()
        ttk.Entry(self.main_frame, textvariable=self.dir_path, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(self.main_frame, text="浏览", command=self.select_directory).grid(row=0, column=2)
        
        # 批量重命名设置
        rename_frame = ttk.LabelFrame(self.main_frame, text="批量重命名", padding="5")
        rename_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(rename_frame, text="前缀:").grid(row=0, column=0, sticky=tk.W)
        self.prefix = tk.StringVar(value="商详")
        ttk.Entry(rename_frame, textvariable=self.prefix, width=20).grid(row=0, column=1, padx=5)
        
        ttk.Label(rename_frame, text="起始编号:").grid(row=0, column=2, sticky=tk.W)
        self.start_num = tk.StringVar(value="01")
        ttk.Entry(rename_frame, textvariable=self.start_num, width=10).grid(row=0, column=3, padx=5)
        
        ttk.Button(rename_frame, text="开始重命名", command=self.rename_images).grid(row=0, column=4, padx=5)
        
        # 修改调整尺寸设置部分
        resize_frame = ttk.LabelFrame(self.main_frame, text="批量调整尺寸(保持原比例)", padding="5")
        resize_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(resize_frame, text="目标宽度:").grid(row=0, column=0, sticky=tk.W)
        self.width = tk.StringVar(value="750")
        ttk.Entry(resize_frame, textvariable=self.width, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(resize_frame, text="像素").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Button(resize_frame, text="调整尺寸", command=self.resize_images).grid(row=0, column=3, padx=5)
        
        # 合并图片设置
        merge_frame = ttk.LabelFrame(self.main_frame, text="合并为长图", padding="5")
        merge_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(merge_frame, text="输出文件:").grid(row=0, column=0, sticky=tk.W)
        self.output_path = tk.StringVar(value="merged_output.jpg")
        ttk.Entry(merge_frame, textvariable=self.output_path, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(merge_frame, text="合并图片", command=self.merge_images).grid(row=0, column=2, padx=5)
        
        # 在合并图片设置后添加切片功能
        slice_frame = ttk.LabelFrame(self.main_frame, text="长图切片", padding="5")
        slice_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(slice_frame, text="目标高度:").grid(row=0, column=0, sticky=tk.W)
        self.slice_height = tk.StringVar(value="1000")
        ttk.Entry(slice_frame, textvariable=self.slice_height, width=10).grid(row=0, column=1, padx=5)
        ttk.Label(slice_frame, text="像素").grid(row=0, column=2, sticky=tk.W)
        
        ttk.Button(slice_frame, text="选择长图", command=self.select_image_to_slice).grid(row=0, column=3, padx=5)
        
        # 状态栏移到最后一行
        self.status_var = tk.StringVar()
        ttk.Label(self.main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=3, pady=10)

    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_path.set(directory)
            self.processor = ImageProcessor(directory)
            self.status_var.set(f"已选择目录: {directory}")

    def rename_images(self):
        if not self.check_processor():
            return
        try:
            prefix = self.prefix.get()
            start_num = int(self.start_num.get())
            self.processor.batch_rename(prefix, start_num)
            self.status_var.set("重命名完成")
            messagebox.showinfo("成功", "图片重命名完成！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def resize_images(self):
        if not self.check_processor():
            return
        try:
            width = int(self.width.get())
            if width <= 0:
                raise ValueError("宽度必须大于0")
            
            self.processor.batch_resize(width)
            self.status_var.set("调整尺寸完成")
            messagebox.showinfo("成功", "图片尺寸调整完成！")
        except ValueError as e:
            messagebox.showerror("错误", "请输入有效的宽度数值！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def merge_images(self):
        if not self.check_processor():
            return
        try:
            output_path = self.output_path.get()
            self.processor.merge_images_vertical(output_path)
            self.status_var.set("合并完成")
            messagebox.showinfo("成功", "图片合并完成！")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def select_image_to_slice(self):
        """选择要切片的图片"""
        file_path = filedialog.askopenfilename(
            filetypes=[("图片文件", "*.jpg;*.jpeg;*.png")],
            title="选择要切片的长图"
        )
        if file_path:
            try:
                height = int(self.slice_height.get())
                if height <= 0:
                    raise ValueError("切片高度必须大于0")
                
                # 如果没有选择目录，使用图片所在目录
                if self.processor is None:
                    self.processor = ImageProcessor(os.path.dirname(file_path))
                
                self.processor.slice_long_image(file_path, height)
                self.status_var.set("切片完成")
                messagebox.showinfo("成功", "长图切片完成！")
            except ValueError as e:
                messagebox.showerror("错误", "请输入有效的切片高度！")
            except Exception as e:
                messagebox.showerror("错误", str(e))

    def check_processor(self):
        if self.processor is None:
            messagebox.showerror("错误", "请先选择图片目录！")
            return False
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorGUI(root)
    root.mainloop() 