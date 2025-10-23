import os
import cv2
import numpy as np
import onnxruntime as ort
from typing import Dict, Tuple
from app.config import settings

class ONNXService:
    """ONNX模型推理服务"""
    
    def __init__(self):
        self.session = None
        self.model_loaded = False
        self.input_shape = (256, 256)
        
        # ImageNet标准化参数
        self.imagenet_mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape(1, 1, 3)
        self.imagenet_std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape(1, 1, 3)
    
    def load_model(self, model_path: str = None):
        """加载ONNX模型"""
        # 如果模型已经加载，直接返回
        if self.model_loaded and self.session is not None:
            print("✅ ONNX模型已加载，跳过重复加载")
            return True
            
        if model_path is None:
            model_path = getattr(settings, 'ONNX_MODEL_PATH', 'models/pcb_defect_detection.onnx')
        
        if not os.path.exists(model_path):
            print(f"警告: ONNX模型文件不存在: {model_path}")
            self.model_loaded = False
            return False
        
        try:
            # 如果已有session，先清理
            if self.session is not None:
                del self.session
                self.session = None
            
            # 创建推理会话
            providers = ['CPUExecutionProvider']
            # 如果有GPU，可以添加: ['CUDAExecutionProvider', 'CPUExecutionProvider']
            
            self.session = ort.InferenceSession(model_path, providers=providers)
            self.model_loaded = True
            
            print(f"✅ ONNX模型加载成功: {model_path}")
            print(f"📊 使用执行提供者: {self.session.get_providers()}")
            
            # 打印模型信息
            self._print_model_info()
            
            return True
            
        except Exception as e:
            print(f"❌ ONNX模型加载失败: {e}")
            self.model_loaded = False
            if self.session is not None:
                del self.session
                self.session = None
            return False
    
    def _print_model_info(self):
        """打印模型信息"""
        if not self.session:
            return
        
        print("\n=== ONNX模型信息 ===")
        
        # 输入信息
        print("📥 输入信息:")
        for input_meta in self.session.get_inputs():
            print(f"  - 名称: {input_meta.name}")
            print(f"    形状: {input_meta.shape}")
            print(f"    类型: {input_meta.type}")
        
        # 输出信息
        print("📤 输出信息:")
        for output_meta in self.session.get_outputs():
            print(f"  - 名称: {output_meta.name}")
            print(f"    形状: {output_meta.shape}")
            print(f"    类型: {output_meta.type}")
    
    def preprocess_image(self, image_array: np.ndarray) -> np.ndarray:
        """
        预处理图像
        
        Args:
            image_array: 图像数组，形状为 [H, W, C] 或 [H, W]
            
        Returns:
            预处理后的图像数组，形状为 [1, 3, 256, 256]
        """
        # 确保是彩色图像
        if len(image_array.shape) == 2:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
        elif image_array.shape[2] == 4:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
        elif image_array.shape[2] == 3:
            pass  # 已经是RGB
        else:
            raise ValueError(f"不支持的图像通道数: {image_array.shape[2]}")
        
        # 调整尺寸
        image_resized = cv2.resize(image_array, self.input_shape)
        
        # 转换为float32并归一化到[0,1]
        image_float = image_resized.astype(np.float32) / 255.0
        
        # ImageNet标准化
        image_normalized = (image_float - self.imagenet_mean) / self.imagenet_std
        
        # 转换为CHW格式并添加batch维度
        image_chw = np.transpose(image_normalized, (2, 0, 1))  # HWC -> CHW
        image_batch = np.expand_dims(image_chw, axis=0)       # 添加batch维度
        
        return image_batch
    
    def run_inference(self, query_image: np.ndarray, gerber_image: np.ndarray) -> Dict[str, np.ndarray]:
        """
        运行ONNX模型推理
        
        Args:
            query_image: 查询图像数组
            gerber_image: Gerber图像数组
            
        Returns:
            包含模型输出的字典
        """
        if not self.model_loaded:
            raise RuntimeError("ONNX模型未加载，请先调用 load_model()")
        
        # 预处理图像
        query_array = self.preprocess_image(query_image)
        gerber_array = self.preprocess_image(gerber_image)
        
        # 准备输入数据
        input_data = {
            'img': query_array,      # 实物图像
            'gerber': gerber_array   # Gerber图像
        }
        
        # 运行推理
        outputs = self.session.run(None, input_data)
        
        # 构建输出字典
        output_names = [output.name for output in self.session.get_outputs()]
        result = {}
        for i, name in enumerate(output_names):
            result[name] = outputs[i]
        
        return result
    
    def parse_results(self, results: Dict[str, np.ndarray]) -> Dict[str, any]:
        """
        解析模型输出结果
        
        Args:
            results: 模型原始输出
            
        Returns:
            解析后的结果字典
        """
        parsed = {}
        
        # 解析异常预测
        if 'anomaly_pred' in results:
            anomaly_pred = results['anomaly_pred'][0]  # 取第一个batch
            parsed['anomaly_probability'] = {
                'normal': float(anomaly_pred[0]),
                'defect': float(anomaly_pred[1])
            }
            
            # 判断逻辑：异常概率大于0.35就判定为缺陷
            anomaly_threshold = 0.35
            is_defect = anomaly_pred[1] > anomaly_threshold
            confidence = anomaly_pred[1] if is_defect else anomaly_pred[0]
            
            parsed['defect_detection'] = {
                'is_defect': bool(is_defect),
                'confidence': float(confidence),
                'threshold': anomaly_threshold
            }
        
        # 解析异常掩码
        if 'anomaly_mask' in results:
            mask = results['anomaly_mask'][0]  # 取第一个batch
            parsed['anomaly_mask'] = {
                'shape': mask.shape,
                'min_value': float(mask.min()),
                'max_value': float(mask.max()),
                'mean_value': float(mask.mean()),
                'data': mask  # 保留原始数据
            }
        
        # 解析风格迁移结果
        if 'style_output' in results:
            style_output = results['style_output'][0]  # 取第一个batch
            parsed['style_transfer'] = {
                'shape': style_output.shape,
                'min_value': float(style_output.min()),
                'max_value': float(style_output.max()),
                'mean_value': float(style_output.mean()),
                'data': style_output  # 保留原始数据
            }
        
        return parsed
    
    def denormalize_image(self, image: np.ndarray) -> np.ndarray:
        """
        反归一化图像，将ImageNet标准化的图像转换回[0,255]范围
        
        Args:
            image (np.ndarray): 标准化后的图像数组，形状为 [C, H, W]
            
        Returns:
            np.ndarray: 反归一化后的图像数组，形状为 [H, W, C]，值范围[0,255]
        """
        # 复制数组避免修改原数据
        img = image.copy()
        
        # 反标准化
        for i in range(3):
            img[i] = img[i] * self.imagenet_std[0, 0, i] + self.imagenet_mean[0, 0, i]
        
        # 转换为HWC格式
        img = np.transpose(img, (1, 2, 0))
        
        # 限制到[0,1]范围并转换为[0,255]
        img = np.clip(img, 0, 1)
        img = (img * 255).astype(np.uint8)
        
        return img

    def resize_mask_to_image(self, mask: np.ndarray, target_size: tuple) -> np.ndarray:
        """
        将异常掩码调整到目标图像尺寸
        
        Args:
            mask (np.ndarray): 异常掩码，形状为 [H, W]
            target_size (tuple): 目标尺寸 (height, width)
            
        Returns:
            np.ndarray: 调整尺寸后的掩码
        """
        return cv2.resize(mask, (target_size[1], target_size[0]), interpolation=cv2.INTER_LINEAR)

    def create_heatmap_overlay(self, image: np.ndarray, mask: np.ndarray, alpha: float = 0.6) -> np.ndarray:
        """
        创建热力图叠加图像
        
        Args:
            image (np.ndarray): 原始图像，形状为 [H, W, C]
            mask (np.ndarray): 异常掩码，形状为 [H, W]
            alpha (float): 热力图透明度
            
        Returns:
            np.ndarray: 叠加后的彩色图像
        """
        # 归一化掩码到[0,1]
        mask_norm = (mask - mask.min()) / (mask.max() - mask.min() + 1e-8)
        
        # 创建热力图颜色映射 (使用jet colormap)
        import matplotlib.pyplot as plt
        colormap = plt.cm.jet
        heatmap = colormap(mask_norm)[:, :, :3]  # 去掉alpha通道
        heatmap = (heatmap * 255).astype(np.uint8)
        
        # 叠加图像
        overlay = cv2.addWeighted(image, 1-alpha, heatmap, alpha, 0)
        
        return overlay

    def generate_defect_description(self, defect_result: Dict) -> str:
        """根据缺陷检测结果生成描述文本（两个梯度：正常/异常）"""
        if not defect_result['is_defect']:
            return "电路板正常，未检测到明显缺陷"
        else:
            confidence = defect_result['confidence']
            return f"检测到缺陷（置信度: {confidence:.1%}）：建议检查并处理"

# 创建全局服务实例
onnx_service = ONNXService()