// src/api/config.js
export const API_CONFIG = {
  baseUrl: '/api', // 添加 /api 前缀
  rootUrl: '/',
  uploadUrl: '/upload', // 移除 /api 前缀，因为 baseUrl 已经包含
  getFileUrl: '/files/{file_type}/{filename}',
};
