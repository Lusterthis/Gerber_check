// src/api/api.js
import { API_CONFIG } from './config.js';

export const testRoot = async () => {
  const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.rootUrl, {
    method: 'GET',
  });
  if (!response.ok) throw new Error('根路径测试失败');
  return await response.text();  // 返回 string
};

export const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);  // 注意：文档中是 'file'，非 'upload_image'
  const response = await fetch(API_CONFIG.baseUrl + API_CONFIG.uploadUrl, {
    method: 'POST',
    body: formData,
  });
  if (!response.ok) {
    if (response.status === 422) {
      const error = await response.json();
      throw new Error(`验证错误: ${JSON.stringify(error.detail)}`);
    }
    throw new Error('上传失败');
  }
  return await response.text();  // 返回 string（如路径）
};

export const getFile = async (fileType, filename) => {
  const url = API_CONFIG.baseUrl + API_CONFIG.getFileUrl
    .replace('{file_type}', fileType)
    .replace('{filename}', filename);
  const response = await fetch(url, {
    method: 'GET',
  });
  if (!response.ok) {
    if (response.status === 422) {
      const error = await response.json();
      throw new Error(`验证错误: ${JSON.stringify(error.detail)}`);
    }
    throw new Error('获取文件失败');
  }
  return await response.text();  // 返回 string（如 URL 或 base64）
};
