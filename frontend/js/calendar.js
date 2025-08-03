// Calendar configuration and initialization
let calendar;
let currentView = 'week';
let selectedEvent = null;

// 장비별 캘린더 설정
const EQUIPMENT_CALENDARS = [
    { id: 'EQ001', name: '혼합기 1호', backgroundColor: '#3498db' },
    { id: 'EQ002', name: '혼합기 2호', backgroundColor: '#2980b9' },
    { id: 'EQ003', name: '타정기 1호', backgroundColor: '#e74c3c' },
    { id: 'EQ004', name: '타정기 2호', backgroundColor: '#c0392b' },
    { id: 'EQ005', name: '코팅기 1호', backgroundColor: '#2ecc71' },
    { id: 'EQ006', name: '코팅기 2호', backgroundColor: '#27ae60' },
    { id: 'EQ007', name: '포장기 1호', backgroundColor: '#f39c12' },
    { id: 'EQ008', name: '포장기 2호', backgroundColor: '#d68910' }
];

// 제품별 색상 매핑
const PRODUCT_COLORS = {
    '500002': '#FF6B6B',  // 기넥신에프정 40mg 100T
    '500005': '#4ECDC4',  // 기넥신에프정 40mg 300T
    '500008': '#45B7D1',  // 기넥신에프정 80mg 100T
    '505227': '#96CEB4',  // 기넥신에프정 80mg 500T
    '500023': '#FECA57',  // 리넥신정
    '500041': '#DDA0DD',  // 조인스정
    '507123': '#98D8C8',  // 페브릭정 40mg
    '507242': '#F7DC6F'   // 신플랙스세이프정
};

// 캘린더 초기화
function initCalendar() {
    const container = document.getElementById('calendar');
    
    calendar = new tui.Calendar(container, {
        defaultView: 'week',
        taskView: false,
        scheduleView: ['time'],
        useCreationPopup: false,
        useDetailPopup: false,
        calendars: EQUIPMENT_CALENDARS,
        week: {
            startDayOfWeek: 1, // 월요일 시작
            dayNames: ['일', '월', '화', '수', '목', '금', '토'],
            workweek: true,    // 주말 제외
            hourStart: 6,      // 오전 6시부터
            hourEnd: 22,       // 오후 10시까지
            narrowWeekend: true
        },
        month: {
            dayNames: ['일', '월', '화', '수', '목', '금', '토'],
            startDayOfWeek: 1,
            narrowWeekend: true,
            workweek: true
        },
        template: {
            time: function(event) {
                const html = `
                    <div style="color: white; padding: 2px 4px;">
                        <strong>${event.title}</strong>
                        <div style="font-size: 11px;">${event.raw.process || ''}</div>
                    </div>
                `;
                return html;
            },
            monthDayName: function(model) {
                return '<span style="font-weight: bold;">' + model.label + '</span>';
            }
        },
        theme: {
            'common.border': '1px solid #dfe6e9',
            'common.backgroundColor': 'white',
            'common.holiday.color': '#e74c3c',
            'common.saturday.color': '#3498db',
            'common.dayname.color': '#2c3e50',
            'common.today.color': '#fff',
            
            // week view
            'week.timegridLeft.width': '100px',
            'week.timegridLeft.backgroundColor': '#f8f9fa',
            'week.timegridLeft.borderRight': '1px solid #dfe6e9',
            'week.timegridOneHour.height': '60px',
            'week.timegridHalfHour.height': '30px',
            'week.currentTimeLinePast.border': '1px solid rgba(231, 76, 60, 0.3)',
            'week.currentTimeLineBullet.backgroundColor': '#e74c3c',
            'week.currentTimeLineToday.border': '2px solid #e74c3c',
            'week.currentTimeLineFuture.border': '1px solid rgba(231, 76, 60, 0.3)',
            'week.pastTime.color': '#95a5a6',
            'week.futureTime.color': '#2c3e50',
            'week.weekend.backgroundColor': 'rgba(236, 240, 241, 0.3)',
            'week.today.backgroundColor': 'rgba(52, 152, 219, 0.05)',
            'week.dayname.height': '42px',
            'week.dayname.borderBottom': '1px solid #dfe6e9',
            'week.dayname.textAlign': 'center',
            'week.today.color': '#3498db',
            'week.pastDay.color': '#95a5a6'
        }
    });
    
    // 이벤트 핸들러 등록
    calendar.on('beforeCreateEvent', onBeforeCreateEvent);
    calendar.on('beforeUpdateEvent', onBeforeUpdateEvent);
    calendar.on('beforeDeleteEvent', onBeforeDeleteEvent);
    calendar.on('clickEvent', onClickEvent);
    
    updateCalendarRange();
}

// 이벤트 생성 전 처리
function onBeforeCreateEvent(e) {
    console.log('Create event:', e);
    
    const event = {
        calendarId: e.calendarId,
        title: '새 작업',
        category: 'time',
        dueDateClass: '',
        start: e.start,
        end: e.end,
        isAllday: e.isAllday,
        state: 'Busy',
        raw: {
            product_id: '',
            equipment_id: e.calendarId,
            process: '',
            lot_number: ''
        }
    };
    
    calendar.createEvents([event]);
}

// 이벤트 업데이트 전 처리
function onBeforeUpdateEvent(e) {
    const event = e.event;
    const changes = e.changes;
    
    // 서버에 업데이트 요청
    const updateData = {
        id: event.id,
        start: changes.start || event.start,
        end: changes.end || event.end,
        calendarId: changes.calendarId || event.calendarId
    };
    
    // API 호출
    updateBatch(updateData).then(response => {
        if (response.success) {
            calendar.updateEvent(event.id, event.calendarId, changes);
            showNotification('일정이 수정되었습니다.', 'success');
        } else {
            showNotification('일정 수정에 실패했습니다.', 'error');
        }
    });
}

// 이벤트 삭제 전 처리
function onBeforeDeleteEvent(e) {
    if (confirm('정말 삭제하시겠습니까?')) {
        deleteBatch(e.event.id).then(response => {
            if (response.success) {
                calendar.deleteEvent(e.event.id, e.event.calendarId);
                showNotification('일정이 삭제되었습니다.', 'success');
            }
        });
    }
}

// 이벤트 클릭 처리
function onClickEvent(e) {
    const event = e.event;
    selectedEvent = event;
    
    // 팝업에 정보 표시
    document.getElementById('popupTitle').textContent = event.title;
    document.getElementById('popupProduct').textContent = event.title;
    document.getElementById('popupProcess').textContent = event.raw.process || '-';
    document.getElementById('popupEquipment').textContent = getEquipmentName(event.calendarId);
    document.getElementById('popupStart').textContent = formatDateTime(event.start);
    document.getElementById('popupEnd').textContent = formatDateTime(event.end);
    document.getElementById('popupLot').textContent = event.raw.lot_number || '-';
    
    // 팝업 위치 설정
    const popup = document.getElementById('eventPopup');
    popup.style.display = 'block';
    popup.style.left = e.event.clientX + 'px';
    popup.style.top = e.event.clientY + 'px';
}

// 캘린더 뷰 변경
function changeView(viewName) {
    calendar.changeView(viewName);
    currentView = viewName;
    updateCalendarRange();
}

// 캘린더 범위 업데이트
function updateCalendarRange() {
    const range = calendar.getDateRangeStart().toDate().toLocaleDateString() + 
                  ' ~ ' + 
                  calendar.getDateRangeEnd().toDate().toLocaleDateString();
    document.querySelector('.current-range').textContent = range;
}

// 장비명 가져오기
function getEquipmentName(equipmentId) {
    const equipment = EQUIPMENT_CALENDARS.find(eq => eq.id === equipmentId);
    return equipment ? equipment.name : equipmentId;
}

// 날짜 포맷팅
function formatDateTime(date) {
    const d = date.toDate ? date.toDate() : new Date(date);
    return d.toLocaleDateString() + ' ' + d.toLocaleTimeString();
}

// 스케줄 데이터 로드
function loadScheduleData() {
    showLoading();
    
    getSchedule().then(data => {
        calendar.clear();
        
        // 배치 데이터를 캘린더 이벤트로 변환
        const events = data.batches.map(batch => ({
            id: batch.id,
            calendarId: batch.equipment_id,
            title: batch.product_name,
            category: 'time',
            start: new Date(batch.start_time),
            end: new Date(batch.end_time),
            backgroundColor: PRODUCT_COLORS[batch.product_id] || '#95a5a6',
            borderColor: PRODUCT_COLORS[batch.product_id] || '#95a5a6',
            raw: {
                product_id: batch.product_id,
                equipment_id: batch.equipment_id,
                process: batch.process_name,
                lot_number: batch.lot_number
            }
        }));
        
        calendar.createEvents(events);
        updateStatistics(data);
        hideLoading();
    }).catch(error => {
        console.error('Failed to load schedule:', error);
        hideLoading();
        showNotification('스케줄을 불러오는데 실패했습니다.', 'error');
    });
}

// 통계 업데이트
function updateStatistics(data) {
    document.getElementById('total-batches').textContent = data.batches.length;
    
    const uniqueProducts = new Set(data.batches.map(b => b.product_id));
    document.getElementById('total-products').textContent = uniqueProducts.size;
}