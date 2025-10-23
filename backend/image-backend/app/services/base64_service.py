import base64
import io
from PIL import Image


class Base64Service:
    def image_to_base64(self, image: Image.Image, format: str = "PNG") -> str:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    def base64_to_image(self, b64_str: str) -> Image.Image:
        # 兼容 data URL 与纯 base64 两种输入
        if b64_str.startswith("data:"):
            try:
                b64_str = b64_str.split(",", 1)[1]
            except Exception:
                raise ValueError("无效的Base64数据URL格式")
        b64_str = b64_str.strip()
        data = base64.b64decode(b64_str)
        return Image.open(io.BytesIO(data)).convert("RGB")


base64_service = Base64Service()


