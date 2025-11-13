import axios from 'axios';

// 配置axios
const axiosInstance = axios.create({
  baseURL: '/api', // API请求将被代理到Express服务器
  timeout: 10000,
});

// 请求拦截器
axiosInstance.interceptors.request.use(
  (config) => {
    // 可以在这里添加认证信息
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器
axiosInstance.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API请求错误:', error);
    return Promise.reject(error);
  }
);

// API 方法

export const listRules = () => {
  return axiosInstance.get('/list_rules');
};

export const addRule = (ruleData) => {
  return axiosInstance.post('/add_rule', ruleData);
};

export const validateRuleset = (ruleset) => {
  return axiosInstance.post('/validate_ruleset', { ruleset });
};

export const generateRule = (queryData) => {
  return axiosInstance.post('/generate_rule_from_query', queryData);
};

export default axiosInstance;