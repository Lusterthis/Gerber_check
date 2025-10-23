from PIL import Image, ImageDraw
import random
import io

class TestImageGenerator:
    """测试图片生成器"""
    
    @staticmethod
    def generate_sample_image(width=400, height=300, image_type="query"):
        """
        生成测试图片
        
        Args:
            width: 图片宽度
            height: 图片高度
            image_type: 图片类型 ('query' 或 'gerber')
            
        Returns:
            PIL.Image: 生成的测试图片
        """
        # 创建新图片
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        if image_type == "query":
            # 生成查询图片（标准模板）
            # 添加一些几何形状模拟PCB设计
            draw.rectangle([50, 50, 150, 100], fill="blue", outline="black")
            draw.ellipse([200, 80, 250, 130], fill="green", outline="black")
            draw.line([100, 150, 300, 150], fill="red", width=3)
            draw.text((50, 180), "PCB Template", fill="black")
            
        else:
            # 生成Gerber图片（可能有缺陷的实际图片）
            # 添加一些随机缺陷
            draw.rectangle([50, 50, 150, 100], fill="blue", outline="black")
            draw.ellipse([200, 80, 250, 130], fill="green", outline="black")
            draw.line([100, 150, 300, 150], fill="red", width=3)
            draw.text((50, 180), "Actual PCB", fill="black")
            
            # 随机添加一些缺陷标记
            if random.random() > 0.5:
                # 模拟油墨污染
                draw.rectangle([120, 70, 140, 90], fill="brown")
                draw.text((120, 95), "INK", fill="red", size=10)
            
        return image
    
    @staticmethod
    def generate_test_images():
        """生成一对测试图片"""
        query_image = TestImageGenerator.generate_sample_image(image_type="query")
        gerber_image = TestImageGenerator.generate_sample_image(image_type="gerber")
        
        return query_image, gerber_image