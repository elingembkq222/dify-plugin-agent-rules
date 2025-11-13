import express from 'express';
import axios from 'axios';
import path from 'path';
import { fileURLToPath } from 'url';

// 获取当前文件的目录路径
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3000;
const DIFY_BACKEND_URL = process.env.DIFY_BACKEND_URL || 'http://localhost:3001';

// 解析JSON请求体
app.use(express.json());

// 静态文件服务，用于提供React应用
app.use(express.static(path.join(__dirname, 'dist')));

// API代理路由
app.all(/^\/api\//, async (req, res) => {
  try {
    const apiPath = req.originalUrl.replace(/^\/api\//, '');
    const targetUrl = `${DIFY_BACKEND_URL}/${apiPath}`;
    console.log('Proxying request to:', targetUrl);
    console.log('Request body:', req.body);
    const response = await axios.request({
      method: req.method,
      url: targetUrl,
      data: req.body,
      headers: { ...req.headers, host: new URL(targetUrl).host }
    });
    console.log('Proxy response:', response.data);
    res.json(response.data);
  } catch (error) {
      console.error('API代理错误:', error);
      console.error('API代理错误详情:', error.stack);
      if (error.response) {
        console.error('错误响应状态:', error.response.status);
        console.error('错误响应数据:', error.response.data);
      }
      res.status(500).json({ error: 'API请求失败', message: error.message, stack: error.stack });
    }
});

// 所有其他路由都返回React应用的入口文件
app.get(/^(.*)$/, (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`API代理指向: ${DIFY_BACKEND_URL}`);
});