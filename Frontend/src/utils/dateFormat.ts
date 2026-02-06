/**
 * 將 UTC 時間字串轉換為台灣時間（UTC+8）並格式化顯示
 * @param dateString - ISO 格式的日期時間字串（例如：'2026-02-06T04:34:18.671Z'）
 * @returns 格式化後的台灣時間字串（例如：'2026/2/6 下午12:34:18'）
 */
export function formatTaiwanTime(dateString: string): string {
  if (!dateString) return '';
  
  try {
    // 如果時間字符串沒有時區標記（'Z' 或 '+/-'），假設它是 UTC 時間並加上 'Z'
    let normalizedDateString = dateString.trim();
    if (!normalizedDateString.endsWith('Z') && 
        !normalizedDateString.match(/[+-]\d{2}:\d{2}$/)) {
      // 沒有時區信息的 ISO 格式，假設是 UTC，加上 'Z'
      normalizedDateString = normalizedDateString + 'Z';
    }
    
    const date = new Date(normalizedDateString);
    
    // 檢查日期是否有效
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return dateString;
    }
    
    // 使用台灣的語言和時區格式（toLocaleString 會自動處理時區轉換）
    const formatted = date.toLocaleString('zh-TW', {
      timeZone: 'Asia/Taipei',
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      second: '2-digit',
      hour12: true,
    });
    
    return formatted;
  } catch (error) {
    console.error('Error formatting date:', error, dateString);
    return dateString;
  }
}

/**
 * 將 UTC 時間字串轉換為台灣時間的 Date 對象
 * @param dateString - ISO 格式的日期時間字串
 * @returns Date 對象（已轉換為台灣時間）
 */
export function toTaiwanTime(dateString: string): Date {
  const date = new Date(dateString);
  // 台灣時間是 UTC+8，所以加上 8 小時
  return new Date(date.getTime() + 8 * 60 * 60 * 1000);
}
