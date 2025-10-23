<template>
  <div class="meta-uas-wrapper">
    <h1 class="huoyan-zh">Gerber图-实物图跨域对齐</h1>

    <div class="meta-uas-container">
      <div class="main-content">
        <!-- 左侧区域 -->
        <div class="left-section">
          <!-- 上部分：两个图像上传区水平排列 -->
          <div class="top-row">
            <div class="image-section">
              <div class="image-upload">
                <div class="upload-area square-box" @click="triggerFileInput('query')" @dragover.prevent
                  @drop="handleFileDrop($event, 'query')">
                  <h2 class="section-title">查询图像</h2>
                  <div class="image-container">
                    <img v-if="queryImage" :src="queryImage" class="preview-image" alt="查询图像" />
                    <template v-else>
                      <p>将图像拖放到此处</p>
                      <p class="upload-or">- 或 -</p>
                      <p>点击上传</p>
                    </template>
                  </div>
                  <input type="file" accept="image/bmp,image/png,image/jpeg" ref="queryInput"
                    @change="handleFileUpload($event, 'query')" class="file-input" />
                </div>
              </div>
            </div>

            <div class="image-section">
              <div class="image-upload">
                <div class="upload-area square-box" @click="triggerFileInput('gerber')" @dragover.prevent
                  @drop="handleFileDrop($event, 'gerber')">
                  <h2 class="section-title">Gerber图</h2>
                  <div class="image-container">
                    <img v-if="gerberImage" :src="gerberImage" class="preview-image" alt="Gerber图" />
                    <template v-else>
                      <p>将图像拖放到此处</p>
                      <p class="upload-or">- 或 -</p>
                      <p>点击上传</p>
                    </template>
                  </div>
                  <input type="file" accept="image/bmp,image/png,image/jpeg" ref="gerberInput"
                    @change="handleFileUpload($event, 'gerber')" class="file-input" />
                </div>
              </div>
            </div>
          </div>

          <!-- 下部分：示例按钮和操作按钮 -->
          <div class="bottom-row">
            <div class="button-container">
              <div class="example-buttons">
                <button class="example-btn" @click="loadExample(1)" :disabled="isLoading">示例1</button>
                <button class="example-btn" @click="loadExample(2)" :disabled="isLoading">示例2</button>
                <button class="example-btn" @click="loadExample(3)" :disabled="isLoading">示例3</button>
              </div>
            </div>
            <div class="button-container">
              <div class="action-buttons">
                <button class="submit-btn" @click="handleSubmit" :disabled="!queryImage || !gerberImage || isLoading"
                  :class="{
                    'submit-btn-loading': isLoading,
                    'submit-btn-disabled': !queryImage || !gerberImage
                  }">
                  <span v-if="isLoading">处理中...</span>
                  <span v-else>提交</span>
                </button>
                <button class="clear-btn" @click="handleClear" :disabled="isLoading">清除</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧区域 -->
        <div class="right-section">
          <!-- 上部分：结果显示 -->
          <div class="top-row">
            <div class="image-section">
              <div class="result-display">
                <div class="result-area square-box">
                  <h2 class="section-title">风格迁移结果</h2>
                  <div class="image-container">
                    <!-- 仅弧形加载 -->
                    <div v-if="isLoading" class="loading-arc-container">
                      <div class="loading-arc"></div>
                    </div>
                    <!-- 结果图像 -->
                    <img v-else-if="convertedGerber" :src="convertedGerber" class="preview-image" alt="风格迁移结果" />
                    <p v-else class="placeholder-text">转换结果展示</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="image-section">
              <div class="result-display">
                <div class="result-area square-box">
                  <h2 class="section-title">异常图</h2>
                  <div class="image-container">
                    <!-- 仅弧形加载 -->
                    <div v-if="isLoading" class="loading-arc-container">
                      <div class="loading-arc"></div>
                    </div>
                    <!-- 结果图像 -->
                    <img v-else-if="anomalyImage" :src="anomalyImage" class="preview-image" alt="异常图" />
                    <p v-else class="placeholder-text"><strong>异常图（缺陷检测结果）</strong></p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 下部分：模型选择和异常检测结果 -->
          <div class="bottom-row">
            <!-- 模型选择方框 -->
            <div class="button-container">
              <div class="model-panel" :class="{ disabled: isLoading }">
                <span class="model-label">模型选择:</span>
                <div class="model-buttons">
                  <span class="model-btn" :class="{ active: selectedModel === '256', disabled: isLoading }"
                    @click="!isLoading && selectModel('256')">model:256</span>
                  <span class="model-btn" :class="{ active: selectedModel === '512', disabled: isLoading }"
                    @click="!isLoading && selectModel('512')">model:512</span>
                </div>
              </div>
            </div>

            <!-- 异常检测结果方框 -->
            <div class="button-container">
              <div class="score-panel" :class="{ disabled: isLoading }">
                <div class="score-section">
                  <span class="score-label">异常检测结果:</span>
                  <div class="score-value" :class="getDetectionStateClass()">
                    {{ getDetectionText() }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// ------------------- 状态 -------------------
const queryImage = ref(null);
const gerberImage = ref(null);
const convertedGerber = ref(null);
const anomalyImage = ref(null);
const anomalyScore = ref(0.87);
const defectDescription = ref('');
const selectedModel = ref('256');
const isLoading = ref(false);
const queryInput = ref(null);
const gerberInput = ref(null);
const queryPath = ref('');
const gerberPath = ref('');

// 示例图片
import Cons03371 from '@/assets/examples/Cons_03371.jpg';
import Cons03371G from '@/assets/examples/Cons_03371_G.jpg';
import Cons03402 from '@/assets/examples/Cons_03402.jpg';
import Cons03402G from '@/assets/examples/Cons_03402_G.jpg';
import Cons03415 from '@/assets/examples/Cons_03415.jpg';
import Cons03415G from '@/assets/examples/Cons_03415_G.jpg';

const exampleData = {
  1: { queryImage: Cons03371, gerberImage: Cons03371G, queryPath: 'example_1_query.jpg', gerberPath: 'example_1_gerber.jpg' },
  2: { queryImage: Cons03402, gerberImage: Cons03402G, queryPath: 'example_2_query.jpg', gerberPath: 'example_2_gerber.jpg' },
  3: { queryImage: Cons03415, gerberImage: Cons03415G, queryPath: 'example_3_query.jpg', gerberPath: 'example_3_gerber.jpg' },
};

// ------------------- 工具函数 -------------------
async function srcToFile(src, filename) {
  if (src.startsWith('data:')) {
    const [header, base64] = src.split(',');
    const mime = header.match(/:(.*?);/)?.[1] || 'image/jpeg';
    const binary = atob(base64);
    const array = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
      array[i] = binary.charCodeAt(i);
    }
    return new File([array], filename, { type: mime });
  }
  const response = await fetch(src);
  if (!response.ok) throw new Error(`加载图片失败: ${response.status}`);
  const blob = await response.blob();
  return new File([blob], filename, { type: blob.type || 'image/jpeg' });
}

// ------------------- 交互函数 -------------------
const triggerFileInput = (type) => {
  if (isLoading.value) return;
  if (type === 'query') queryInput.value.click();
  else gerberInput.value.click();
};

const handleFileDrop = (event, type) => {
  if (isLoading.value) return;
  event.preventDefault();
  const file = event.dataTransfer.files[0];
  if (file && ['image/bmp', 'image/png', 'image/jpeg'].includes(file.type) && file.size < 10 * 1024 * 1024) {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (type === 'query') {
        queryImage.value = e.target.result;
        queryPath.value = `local_query_${Date.now()}`;
      } else {
        gerberImage.value = e.target.result;
        gerberPath.value = `local_gerber_${Date.now()}`;
      }
      // 只清除结果
      convertedGerber.value = null;
      anomalyImage.value = null;
      anomalyScore.value = 0.87;
      defectDescription.value = '';
    };
    reader.readAsDataURL(file);
  } else {
    alert('请上传小于10MB的 bmp、png 或 jpg 格式的图像！');
  }
};

const selectModel = (model) => {
  if (isLoading.value) return;
  selectedModel.value = model;
};

const loadExample = (exampleId) => {
  if (isLoading.value) return;
  const example = exampleData[exampleId];
  if (example) {
    queryImage.value = example.queryImage;
    gerberImage.value = example.gerberImage;
    queryPath.value = example.queryPath;
    gerberPath.value = example.gerberPath;

    // 清除结果
    convertedGerber.value = null;
    anomalyImage.value = null;
    anomalyScore.value = 0.87;
    defectDescription.value = '';
  } else {
    alert('示例数据不可用！');
  }
};

const handleFileUpload = async (event, type) => {
  if (isLoading.value) return;
  const file = event.target.files[0];
  if (file && ['image/bmp', 'image/png', 'image/jpeg'].includes(file.type) && file.size < 10 * 1024 * 1024) {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (type === 'query') {
        queryImage.value = e.target.result;
        queryPath.value = `local_query_${Date.now()}`;
      } else {
        gerberImage.value = e.target.result;
        gerberPath.value = `local_gerber_${Date.now()}`;
      }
      // 只清除结果，保留另一张图
      convertedGerber.value = null;
      anomalyImage.value = null;
      anomalyScore.value = 0.87;
      defectDescription.value = '';
    };
    reader.readAsDataURL(file);
  } else {
    alert('请上传小于10MB的 bmp、png 或 jpg 格式的图像！');
  }
  event.target.value = '';
};

// ------------------- 异常检测状态 -------------------
const getDetectionText = () => {
  if (isLoading.value) return '检测中...';
  if (!anomalyImage.value) return '待检测';
  return anomalyScore.value > 0.35 ? '异常' : '无异常';
};

const getDetectionStateClass = () => {
  if (isLoading.value || !anomalyImage.value) return 'waiting';
  return anomalyScore.value > 0.35 ? 'anomaly' : 'normal';
};

// ------------------- 提交处理 -------------------
const handleSubmit = async () => {
  if (!queryImage.value || !gerberImage.value) {
    alert('请上传查询图像和Gerber图！');
    return;
  }

  isLoading.value = true;

  try {
    const queryFile = await srcToFile(queryImage.value, 'query.jpg');
    const gerberFile = await srcToFile(gerberImage.value, 'gerber.jpg');

    const formData = new FormData();
    formData.append('query', queryFile);
    formData.append('gerber', gerberFile);
    formData.append('model', selectedModel.value);

    const response = await fetch('http://127.0.0.1:8000/api/process', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    const result = await response.json();

    convertedGerber.value = `data:image/png;base64,${result.convertedGerber}`;
    anomalyImage.value = `data:image/png;base64,${result.anomalyImage}`;
    anomalyScore.value = parseFloat(result.anomalyScore).toFixed(3);
    defectDescription.value = result.defectDescription || '处理完成';

  } catch (error) {
    console.error('处理失败:', error);
    alert(
      error.message.includes('Failed to fetch')
        ? '无法连接后端服务，请检查 http://127.0.0.1:8000 是否运行'
        : `处理失败: ${error.message}`
    );
  } finally {
    isLoading.value = false;
  }
};

// ------------------- 清空 -------------------
const handleClear = () => {
  queryImage.value = null;
  gerberImage.value = null;
  convertedGerber.value = null;
  anomalyImage.value = null;
  anomalyScore.value = 0.87;
  defectDescription.value = '';
  selectedModel.value = '256';
  queryPath.value = '';
  gerberPath.value = '';
  isLoading.value = false;

  if (queryInput.value) queryInput.value.value = '';
  if (gerberInput.value) gerberInput.value.value = '';
};
</script>

<style scoped>
/* =============== 全局容器 =============== */
.meta-uas-wrapper {
  width: 100vw;
  height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  background-image: linear-gradient(to top, #f3e7e9 0%, #e3eeff 99%, #e3eeff 100%);
  padding: 20px;
  box-sizing: border-box;
}

.meta-uas-container {
  width: 90vw;
  height: calc(85vh - 70px);
  background: white;
  border-radius: 25px;
  padding: 30px;
  box-shadow: 0 0 10px 4px rgba(192, 196, 204, 0.27);
  display: flex;
  flex-direction: column;
  margin-top: 20px;
  overflow: hidden;
}

.huoyan-zh {
  font-family: "Microsoft YaHei", "黑体", "SimHei", Arial, sans-serif;
  font-weight: bold;
  font-size: 36px;
  color: #1c1983;
  text-align: center;
  margin: 0;
  padding: 20px 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
}

.main-content {
  display: flex;
  flex: 1;
  gap: 30px;
  min-height: 0;
  overflow: hidden;
  position: relative;
  width: 100%;
  box-sizing: border-box;
}

.main-content::after {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 50%;
  width: 1px;
  background: #91aee8;
  transform: translateX(-50%);
  display: block;
}

.left-section,
.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 50%;
  max-width: 50%;
}

.top-row {
  display: flex;
  gap: 25px;
  flex: 3;
  min-height: 0;
  align-items: stretch;
}

.bottom-row {
  display: flex;
  flex-direction: column;
  gap: 15px;
  flex: 2;
  min-height: 0;
  margin-top: 0;
}

.button-container {
  flex: 1;
  width: 100%;
  padding: 12px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  display: flex;
  justify-content: center;
  align-items: center;
  box-sizing: border-box;
  min-height: 60px;
  max-height: 20vh;
}

.image-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

/* =============== 正方形容器（统一） =============== */
.square-box {
  aspect-ratio: 1 / 1;
  width: 100%;
  max-height: 80vh;
  border: 1px solid #a0a0a0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  padding: 50px 15px 15px;
  box-sizing: border-box;
  position: relative;
  background: white;
  transition: all 0.3s ease;
  overflow: hidden;
}

/* 标题悬浮 */
.section-title {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
  z-index: 10;
  background: white;
  padding: 0 12px;
  border-radius: 4px;
  text-align: center;
  white-space: nowrap;
  pointer-events: none;
}

/* =============== 图片容器（白色背景） =============== */
.image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 0;
  padding: 20px;
  box-sizing: border-box;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  position: relative;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
  object-position: center;
  background: white;
  border-radius: 8px;
  display: block;
}

/* =============== 上传区 =============== */
.file-input {
  display: none;
}

.upload-area {
  cursor: pointer;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  height: 100%;
}

.upload-area:hover {
  border-color: #667eea;
  background: #f8f9ff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

.upload-area p {
  margin: 5px 0;
  color: #5a5a5a;
  font-size: 14px;
  font-weight: 500;
}

.upload-or {
  color: #888 !important;
  font-size: 13px;
  margin: 3px 0;
}

/* =============== 结果区 =============== */
.result-area {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
}

.result-area:hover {
  border-color: #667eea;
  background: #f8f9ff;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* =============== 占位文字 =============== */
.placeholder-text {
  color: #6c757d;
  font-size: 14px;
  margin: 0;
  text-align: center;
  background: white;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
}

/* =============== 加载状态 =============== */
.loading-arc-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 8px;
}

.loading-arc {
  width: 60px;
  height: 60px;
  border: 6px solid rgba(102, 126, 234, 0.1);
  border-top: 6px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* =============== 按钮组 =============== */
.example-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

.example-btn {
  padding: 10px 20px;
  background: #6b9cf8c9;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #495057;
  white-space: nowrap;
  box-shadow: 0 0 2px #7981a2;
  flex: 1;
  max-width: 130px;
}

.example-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.example-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-buttons {
  display: flex;
  gap: 12px;
  width: 100%;
  justify-content: center;
}

.submit-btn,
.clear-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  flex: 1;
  max-width: 180px;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.submit-btn-disabled {
  background: #cccccc !important;
  color: #666666 !important;
  cursor: not-allowed !important;
  box-shadow: none !important;
}

.submit-btn:not(.submit-btn-disabled):not(.submit-btn-loading) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.submit-btn:not(.submit-btn-disabled):not(.submit-btn-loading):hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b3e8e 100%);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.submit-btn-loading {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: wait;
  background-size: 200% 200%;
  animation: gradient-shift 2s ease infinite;
}

@keyframes gradient-shift {
  0% {
    background-position: 0% 50%;
  }

  50% {
    background-position: 100% 50%;
  }

  100% {
    background-position: 0% 50%;
  }
}

.clear-btn {
  background: #470790cc;
  color: #ffffff;
  box-shadow: 0 0 3px #6633a1;
}

.clear-btn:hover:not(:disabled) {
  background: #3a0677;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.clear-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* =============== 模型与检测结果 =============== */
.model-panel {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.model-label {
  font-size: 16px;
  color: #495057;
  font-weight: 600;
  white-space: nowrap;
}

.model-buttons {
  display: flex;
  gap: 8px;
}

.model-btn {
  padding: 8px 16px;
  background: white;
  border: 2px solid #dee2e6;
  border-radius: 6px;
  text-align: center;
  cursor: pointer;
  font-weight: 600;
  color: #495057;
  transition: all 0.3s ease;
  font-size: 14px;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.model-btn.active,
.model-btn:hover:not(.disabled) {
  background: #667eea;
  color: white;
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.model-btn.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  background: #f8f9fa !important;
  color: #6c757d !important;
  border-color: #dee2e6 !important;
}

.disabled {
  opacity: 0.6;
  pointer-events: none;
}

.score-panel {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.score-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.score-label {
  font-size: 16px;
  color: #495057;
  font-weight: 600;
}

.score-value {
  font-size: 16px;
  /* 与 model-label 一致 */
  font-weight: bold;
  transition: color 0.3s ease;
}

.score-value.waiting {
  color: #6c757d;
}

.score-value.anomaly {
  color: #e74c3c;
}

.score-value.normal {
  color: #28a745;
}

/* =============== 响应式 =============== */
@media (max-width: 1024px) {
  .meta-uas-container {
    width: 95vw;
    height: calc(90vh - 60px);
    padding: 20px;
  }

  .huoyan-zh {
    font-size: 28px;
    padding: 15px 0;
  }

  .main-content {
    flex-direction: column;
    gap: 20px;
  }

  .main-content::after {
    display: none;
  }

  .left-section,
  .right-section {
    width: 100%;
    max-width: 100%;
  }

  .top-row {
    flex-direction: column;
    gap: 15px;
    flex: 2;
  }

  .bottom-row {
    flex: 1;
    gap: 10px;
  }

  .section-title {
    font-size: 16px;
  }

  .square-box {
    max-height: 150px;
  }

  .model-panel {
    flex-direction: column;
    gap: 8px;
  }

  .model-label {
    font-size: 14px;
  }
}

@media (max-width: 768px) {
  .meta-uas-wrapper {
    padding: 10px;
  }

  .meta-uas-container {
    width: 100vw;
    height: calc(95vh - 50px);
    border-radius: 15px;
    padding: 15px;
  }

  .huoyan-zh {
    font-size: 24px;
    padding: 10px 0;
  }

  .example-buttons,
  .action-buttons {
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }

  .example-btn,
  .submit-btn,
  .clear-btn {
    max-width: 100%;
    width: 100%;
  }

  .model-buttons {
    flex-direction: column;
    gap: 6px;
  }

  .model-btn {
    width: 100%;
    max-width: none;
  }

  .loading-arc {
    width: 50px;
    height: 50px;
    border-width: 5px;
  }
}
</style>
