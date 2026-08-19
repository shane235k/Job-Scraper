/**
 * Utility to format ISO datetime strings into Indian Standard Time (IST - Asia/Kolkata).
 */
export function formatIST(dateStr) {
  if (!dateStr) return 'Never';
  
  // Ensure UTC parsing by appending Z if missing timezone offset
  let normalized = dateStr;
  if (typeof dateStr === 'string' && !dateStr.endsWith('Z') && !dateStr.includes('+')) {
    normalized += 'Z';
  }
  
  try {
    const date = new Date(normalized);
    if (isNaN(date.getTime())) return 'Invalid Date';

    return date.toLocaleString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    }) + ' IST';
  } catch (e) {
    return String(dateStr);
  }
}

export function formatDateIST(dateStr) {
  if (!dateStr) return 'N/A';
  let normalized = dateStr;
  if (typeof dateStr === 'string' && !dateStr.endsWith('Z') && !dateStr.includes('+')) {
    normalized += 'Z';
  }
  try {
    const date = new Date(normalized);
    if (isNaN(date.getTime())) return 'N/A';

    return date.toLocaleDateString('en-IN', {
      timeZone: 'Asia/Kolkata',
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (e) {
    return String(dateStr);
  }
}
