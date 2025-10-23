from PIL import Image, ImageChops
from typing import Dict
import numpy as np
from app.services.onnx_service import onnx_service


class AlgorithmService:
    def process_images(self, query_image: Image.Image, gerber_image: Image.Image, model: str) -> Dict:
        # 将 PIL 转为 numpy RGB 数组
        query_rgb = query_image.convert("RGB")
        gerber_rgb = gerber_image.convert("RGB")
        query_np = np.array(query_rgb)
        gerber_np = np.array(gerber_rgb)

        # 运行 ONNX 推理
        if not onnx_service.model_loaded:
            raise RuntimeError("ONNX 模型未加载，请检查启动日志或模型路径配置")

        raw_outputs = onnx_service.run_inference(query_np, gerber_np)
        parsed = onnx_service.parse_results(raw_outputs)

        # 生成可视化结果：
        # 1) converted_image：优先使用 style_output（若有），否则回退为 gerber 对齐图
        if "style_transfer" in parsed and "data" in parsed["style_transfer"]:
            style_data = parsed["style_transfer"]["data"]
            # 检查输出形状，确保是 [C, H, W] 格式
            if style_data.ndim == 3 and style_data.shape[0] in (1, 3):
                # 已经是 CHW 格式，直接使用反归一化
                style_img = onnx_service.denormalize_image(style_data)
                converted_image = Image.fromarray(style_img)
            elif style_data.ndim == 3 and style_data.shape[2] in (1, 3):
                # 是 HWC 格式，需要转换为 CHW 再反归一化
                style_chw = np.transpose(style_data, (2, 0, 1))
                style_img = onnx_service.denormalize_image(style_chw)
                converted_image = Image.fromarray(style_img)
            else:
                # 其他情况，使用简单归一化作为回退
                style_min = float(style_data.min())
                style_max = float(style_data.max())
                denom = (style_max - style_min) if (style_max - style_min) > 1e-6 else 1.0
                style_norm = (style_data - style_min) / denom
                style_img = (np.clip(style_norm, 0.0, 1.0) * 255.0).astype(np.uint8)
                converted_image = Image.fromarray(style_img)
        else:
            # 回退：使用尺寸对齐后的 gerber 图
            width = min(query_rgb.width, gerber_rgb.width)
            height = min(query_rgb.height, gerber_rgb.height)
            converted_image = gerber_rgb.resize((width, height))

        # 2) anomaly_image：优先使用 anomaly_mask 创建彩色热力图叠加（若有），否则用两图差异
        if "anomaly_mask" in parsed and "data" in parsed["anomaly_mask"]:
            mask = parsed["anomaly_mask"]["data"]
            # 处理不同维度的掩码
            if mask.ndim == 3 and mask.shape[0] == 1:
                mask_2d = mask[0]
            elif mask.ndim == 2:
                mask_2d = mask
            else:
                # 如果形状不符合预期，尝试取第一个通道
                mask_2d = mask.reshape(-1, mask.shape[-1]) if mask.ndim > 2 else mask
            
            # 调整掩码尺寸到查询图像尺寸
            query_size = (query_rgb.height, query_rgb.width)
            mask_resized = onnx_service.resize_mask_to_image(mask_2d, query_size)
            
            # 创建彩色热力图叠加图像
            query_array = np.array(query_rgb)
            overlay = onnx_service.create_heatmap_overlay(query_array, mask_resized)
            anomaly_image = Image.fromarray(overlay)
        else:
            # 回退：使用像素差异（转换为彩色显示）
            width = min(query_rgb.width, gerber_rgb.width)
            height = min(query_rgb.height, gerber_rgb.height)
            q = query_rgb.resize((width, height))
            g = gerber_rgb.resize((width, height))
            diff = ImageChops.difference(q, g)
            # 将差异图像转换为彩色显示（使用红色通道突出差异）
            diff_array = np.array(diff)
            if len(diff_array.shape) == 2:  # 如果是灰度图
                # 创建彩色差异图：红色通道显示差异
                colored_diff = np.zeros((diff_array.shape[0], diff_array.shape[1], 3), dtype=np.uint8)
                colored_diff[:, :, 0] = diff_array  # 红色通道
                colored_diff[:, :, 1] = diff_array // 2  # 绿色通道（较暗）
                colored_diff[:, :, 2] = diff_array // 2  # 蓝色通道（较暗）
                anomaly_image = Image.fromarray(colored_diff)
            else:
                anomaly_image = diff

        # 3) anomaly_score 与缺陷描述
        anomaly_score = 0.0
        defect_description = ""
        if "anomaly_probability" in parsed:
            prob = parsed["anomaly_probability"]
            anomaly_score = float(prob.get("defect", 0.0))
        if "defect_detection" in parsed:
            defect_detection = parsed["defect_detection"]
            defect_description = onnx_service.generate_defect_description(defect_detection)
        else:
            defect_description = "模型未返回缺陷检测结果"

        return {
            "converted_image": converted_image,
            "anomaly_image": anomaly_image,
            "anomaly_score": anomaly_score,
            "defect_description": defect_description,
        }


algorithm_service = AlgorithmService()




