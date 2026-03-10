const HISTORY_STORAGE_KEY = "sentiment-analysis-history";

export function loadHistoryRecords() {
  try {
    const rawValue = localStorage.getItem(HISTORY_STORAGE_KEY);
    if (!rawValue) {
      return [];
    }
    const parsedValue = JSON.parse(rawValue);
    return Array.isArray(parsedValue) ? parsedValue : [];
  } catch (error) {
    return [];
  }
}

export function saveHistoryRecords(records) {
  localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(records));
}

export function appendHistoryRecord(record) {
  const currentRecords = loadHistoryRecords();
  const nextRecords = [record, ...currentRecords].slice(0, 50);
  saveHistoryRecords(nextRecords);
  return nextRecords;
}

export function removeHistoryRecord(recordId) {
  const nextRecords = loadHistoryRecords().filter((item) => item.id !== recordId);
  saveHistoryRecords(nextRecords);
  return nextRecords;
}

export function clearHistoryRecords() {
  localStorage.removeItem(HISTORY_STORAGE_KEY);
  return [];
}
