/**
 * 清空指定日曆的內容
 * @param {string} calendarId - 要清空的 Google Calendar ID
 */
function clearCalendarSafe(calendarId) {
  if (!calendarId) {
    console.log("錯誤：未提供日曆 ID。");
    return;
  }

  var calendar = CalendarApp.getCalendarById(calendarId);
  
  if (!calendar) {
    console.log("找不到日曆，請確認 ID 是否正確或是否有權限。");
    return;
  }
  
  // 記錄程式開始執行的時間
  var scriptStart = Date.now();
  
  // 設定 年範圍
  var startTime = new Date('2025-01-01T00:00:00');
  var endTime = new Date('2130-12-31T00:00:00');
  
  console.log('正在向 Google 請求事件資料，因為範圍長達 100 多年，請稍候...');
  var events = calendar.getEvents(startTime, endTime);
  console.log('本次找到活動數量: ' + events.length);
  
  if (events.length === 0) {
    console.log('太棒了！日曆已經完全清空，可以準備匯入新的 ICS 檔了！');
    return;
  }
  
  for(var i = 0; i < events.length; i++) {
    // 【防護機制】如果執行時間超過 5.5 分鐘 (330,000 毫秒)，提早安全退出
    if (Date.now() - scriptStart > 330000) {
      console.log('⚠️ 快要觸發 Google 6分鐘限制了！已安全暫停。請再次點擊「執行」來接續刪除！');
      break; 
    }
    
    try {
      events[i].deleteEvent();
      // 將等待時間稍微縮短到 50 毫秒，可以清得快一點，對 Google 來說依然算友善
      Utilities.sleep(50); 
      
      if (i % 100 == 0 && i !== 0) { // 改成每 100 筆回報一次，避免日誌太長
        console.log('已刪除 ' + i + ' 個活動...');
      }
    } catch (e) {
      console.log('刪除到第 ' + i + ' 個時發生錯誤: ' + e.message);
      break; 
    }
  }
  
  console.log('本次清理回合結束。如果上面顯示「安全暫停」，請再按一次執行！');
}

/**
 * 執行用主程式：將您的日曆 ID 放在這裡，然後在介面上執行這個函式即可
 */
function runClearTask() {
  // 將您想要清空的日曆 ID 填入下方變數
  var targetCalendarId = 'ca5edcf8a68fa615a4a7a916472ca3e053782737ec35db1de35642351fa2ab24@group.calendar.google.com';
  
  // 呼叫清空函式
  clearCalendarSafe(targetCalendarId);
}