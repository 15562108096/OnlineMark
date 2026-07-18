import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL ? import.meta.env.VITE_API_URL : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = 'Bearer ' + token;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.hash = '#/login';
    }
    return Promise.reject(error);
  }
);

export default api;

export const authApi = {
  login: (data: { username: string; password: string; role: string }) =>
    api.post('/auth/login', data),
  getMe: () => api.get('/auth/me'),
  changePassword: (data: { old_password: string; new_password: string }) =>
    api.put('/auth/password', data),
};

export const userApi = {
  list: (role?: string) => api.get('/users/', { params: { role } }),
  create: (data: any) => api.post('/users/', data),
  delete: (id: string) => api.delete('/users/' + id),
  toggleActive: (id: string) => api.put('/users/' + id + '/toggle-active'),
  listTeachers: () => api.get('/users/teachers'),
};

export const templateApi = {
  uploadImage: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return api.post('/templates/upload-image', form);
  },
  create: (data: any) => api.post('/templates/', data),
  list: () => api.get('/templates/'),
  get: (id: string) => api.get('/templates/' + id),
  update: (id: string, data: any) => api.put('/templates/' + id, data),
  delete: (id: string) => api.delete('/templates/' + id),
  export: (id: string) => api.get('/templates/' + id + '/export'),
};

export const scanApi = {
  createBatch: (data: { name: string; template_id: string; exam_name?: string }) =>
    api.post('/scan/batch', data),
  uploadSheets: (batchId: string, files: File[]) => {
    const form = new FormData();
    form.append('batch_id', batchId);
    files.forEach((f) => form.append('files', f));
    return api.post('/scan/upload', form);
  },
  recognize: (batchId: string) => api.post('/scan/recognize/' + batchId),
  listBatches: () => api.get('/scan/batch'),
  getBatch: (id: string) => api.get('/scan/batch/' + id),
};

export const gradingApi = {
  createTask: (data: any) => api.post('/grading/task', data),
  listTasks: () => api.get('/grading/task'),
  assign: (data: any) => api.post('/grading/assign', data),
  getPending: () => api.get('/grading/pending'),
  submitGrade: (data: any) => api.post('/grading/grade', data),
};

export const scoreApi = {
  calculate: (batchId: string) => api.post('/scores/calculate/' + batchId),
  getBatchScores: (batchId: string) => api.get('/scores/batch/' + batchId),
  getStatistics: (batchId: string) => api.get('/scores/statistics/' + batchId),
  export: (batchId: string) => api.get('/scores/export/' + batchId),
};

