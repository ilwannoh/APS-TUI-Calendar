// API Communication Module
const API_BASE_URL = 'http://localhost:8000/api';

// API 헬퍼 함수
async function apiRequest(endpoint, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...defaultOptions,
        ...options,
    });
    
    if (!response.ok) {
        throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
}

// 스케줄 관련 API
async function getSchedule() {
    return apiRequest('/schedule');
}

async function generateScheduleFromSales(salesData) {
    return apiRequest('/schedule/generate', {
        method: 'POST',
        body: JSON.stringify(salesData),
    });
}

async function updateBatch(batchData) {
    return apiRequest(`/batches/${batchData.id}`, {
        method: 'PUT',
        body: JSON.stringify(batchData),
    });
}

async function deleteBatch(batchId) {
    return apiRequest(`/batches/${batchId}`, {
        method: 'DELETE',
    });
}

// 마스터 데이터 API
async function getEquipment() {
    return apiRequest('/equipment');
}

async function getProducts() {
    return apiRequest('/products');
}

async function getProcesses() {
    return apiRequest('/processes');
}

// 파일 업로드 API
async function uploadSalesPlan(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload/sales-plan`, {
        method: 'POST',
        body: formData,
    });
    
    if (!response.ok) {
        throw new Error(`Upload Error: ${response.status}`);
    }
    
    return response.json();
}

// 내보내기 API
async function exportSchedule(format = 'excel') {
    const response = await fetch(`${API_BASE_URL}/export/schedule?format=${format}`);
    
    if (!response.ok) {
        throw new Error(`Export Error: ${response.status}`);
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schedule_${new Date().toISOString().split('T')[0]}.${format === 'excel' ? 'xlsx' : 'csv'}`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}