// Main Application Logic
document.addEventListener('DOMContentLoaded', function() {
    console.log('[APS] DOM Content Loaded - Initializing application');
    
    // 캘린더 초기화
    console.log('[APS] Initializing calendar...');
    initCalendar();
    
    // 이벤트 리스너 설정
    console.log('[APS] Setting up event listeners...');
    setupEventListeners();
    
    // 초기 데이터 로드
    console.log('[APS] Loading initial data...');
    loadInitialData();
});

// 이벤트 리스너 설정
function setupEventListeners() {
    // 뷰 변경 버튼
    document.querySelectorAll('.view-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('[Event] View button clicked:', this.dataset.view);
            document.querySelector('.view-btn.active').classList.remove('active');
            this.classList.add('active');
            changeView(this.dataset.view);
        });
    });
    
    // 파일 업로드 영역
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('fileInput');
    
    uploadArea.addEventListener('click', () => {
        console.log('[Event] Upload area clicked');
        fileInput.click();
    });
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('drop', handleDrop);
    
    fileInput.addEventListener('change', function(e) {
        console.log('[Event] File selected:', e.target.files[0]?.name);
        handleFileSelect(e);
    });
    
    // 전체 선택 체크박스
    document.getElementById('all-equipment').addEventListener('change', function() {
        const checkboxes = document.querySelectorAll('#equipment-list input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = this.checked;
            toggleEquipmentVisibility(cb.value, cb.checked);
        });
    });
    
    // 제품 검색
    document.getElementById('product-search').addEventListener('input', function() {
        filterProducts(this.value);
    });
}

// 초기 데이터 로드
async function loadInitialData() {
    try {
        console.log('[API] Loading equipment list...');
        // 장비 목록 로드
        const equipment = await getEquipment();
        console.log('[API] Equipment loaded:', equipment.length, 'items');
        renderEquipmentList(equipment);
        
        console.log('[API] Loading products list...');
        // 제품 목록 로드
        const products = await getProducts();
        console.log('[API] Products loaded:', products.length, 'items');
        renderProductList(products);
        
        console.log('[API] Loading schedule data...');
        // 스케줄 데이터 로드
        loadScheduleData();
    } catch (error) {
        console.error('[ERROR] Failed to load initial data:', error);
        showNotification('초기 데이터 로드 실패', 'error');
    }
}

// 장비 목록 렌더링
function renderEquipmentList(equipment) {
    const container = document.getElementById('equipment-list');
    container.innerHTML = '';
    
    equipment.forEach(eq => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" value="${eq.id}" checked>
            <span>${eq.name}</span>
        `;
        
        label.querySelector('input').addEventListener('change', function() {
            toggleEquipmentVisibility(this.value, this.checked);
        });
        
        container.appendChild(label);
    });
}

// 제품 목록 렌더링
function renderProductList(products) {
    const container = document.getElementById('product-list');
    container.innerHTML = '';
    
    products.forEach(product => {
        const item = document.createElement('div');
        item.className = 'product-item';
        item.dataset.productId = product.id;
        item.innerHTML = `
            <span class="product-color" style="background: ${PRODUCT_COLORS[product.id] || '#95a5a6'}"></span>
            <span class="product-name">${product.name}</span>
        `;
        container.appendChild(item);
    });
}

// 장비 표시/숨김 토글
function toggleEquipmentVisibility(equipmentId, visible) {
    calendar.setCalendarVisibility(equipmentId, visible);
}

// 제품 필터링
function filterProducts(searchText) {
    const items = document.querySelectorAll('.product-item');
    const lowerSearch = searchText.toLowerCase();
    
    items.forEach(item => {
        const productName = item.querySelector('.product-name').textContent.toLowerCase();
        item.style.display = productName.includes(lowerSearch) ? 'flex' : 'none';
    });
}

// 파일 처리 함수들
function handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.add('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    e.currentTarget.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

function handleFile(file) {
    if (!file.name.match(/\.(xlsx|xls)$/)) {
        showNotification('Excel 파일만 업로드 가능합니다.', 'error');
        return;
    }
    
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileInfo').style.display = 'flex';
    document.getElementById('uploadArea').style.display = 'none';
    
    window.selectedFile = file;
}

// 파일 제거
function removeFile() {
    window.selectedFile = null;
    document.getElementById('fileInfo').style.display = 'none';
    document.getElementById('uploadArea').style.display = 'block';
    document.getElementById('fileInput').value = '';
}

// 모달 함수들
function showUploadModal() {
    document.getElementById('uploadModal').style.display = 'block';
}

function closeUploadModal() {
    document.getElementById('uploadModal').style.display = 'none';
    removeFile();
}

function closeEventPopup() {
    document.getElementById('eventPopup').style.display = 'none';
    selectedEvent = null;
}

// 파일 업로드
async function uploadFile() {
    if (!window.selectedFile) {
        showNotification('파일을 선택해주세요.', 'error');
        return;
    }
    
    showLoading();
    
    try {
        const result = await uploadSalesPlan(window.selectedFile);
        closeUploadModal();
        showNotification('판매계획이 업로드되었습니다.', 'success');
        
        // 자동으로 스케줄 생성 여부 확인
        if (confirm('스케줄을 생성하시겠습니까?')) {
            generateSchedule();
        }
    } catch (error) {
        console.error('Upload failed:', error);
        showNotification('업로드 실패', 'error');
    } finally {
        hideLoading();
    }
}

// 스케줄 생성
async function generateSchedule() {
    console.log('[Action] Generate schedule button clicked');
    showLoading();
    
    try {
        console.log('[API] Calling schedule generation API...');
        const result = await generateScheduleFromSales();
        console.log('[API] Schedule generation result:', result);
        showNotification('스케줄이 생성되었습니다.', 'success');
        loadScheduleData();
    } catch (error) {
        console.error('[ERROR] Schedule generation failed:', error);
        showNotification('스케줄 생성 실패', 'error');
    } finally {
        hideLoading();
    }
}

// 스케줄 내보내기
async function exportSchedule() {
    try {
        await exportSchedule('excel');
        showNotification('스케줄이 내보내졌습니다.', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        showNotification('내보내기 실패', 'error');
    }
}

// 이벤트 삭제
function deleteEvent() {
    if (!selectedEvent) return;
    
    if (confirm('정말 삭제하시겠습니까?')) {
        deleteBatch(selectedEvent.id).then(() => {
            calendar.deleteEvent(selectedEvent.id, selectedEvent.calendarId);
            closeEventPopup();
            showNotification('삭제되었습니다.', 'success');
        });
    }
}

// 이벤트 수정
function editEvent() {
    // TODO: 수정 모달 구현
    showNotification('수정 기능은 준비 중입니다.', 'info');
}

// 로딩 표시
function showLoading() {
    document.getElementById('loadingOverlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loadingOverlay').style.display = 'none';
}

// 알림 표시
function showNotification(message, type = 'info') {
    // 간단한 알림 구현 (실제로는 토스트 라이브러리 사용 권장)
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: ${type === 'success' ? '#2ecc71' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        border-radius: 4px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// 윈도우 클릭 이벤트 (팝업 닫기)
window.addEventListener('click', function(e) {
    const popup = document.getElementById('eventPopup');
    if (!popup.contains(e.target) && popup.style.display === 'block') {
        closeEventPopup();
    }
});