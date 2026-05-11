/**
 * Convert UTC date to IST (Indian Standard Time)
 * IST is UTC+5:30
 */
export const convertToIST = (utcDateString: string): Date => {
  const utcDate = new Date(utcDateString);
  // Add 5 hours 30 minutes (330 minutes) to convert UTC to IST
  const istDate = new Date(utcDate.getTime() + (330 * 60 * 1000));
  return istDate;
};

export const formatISTDateTime = (utcDateString: string): string => {
  const istDate = convertToIST(utcDateString);

  const day = istDate.getDate().toString().padStart(2, '0');
  const month = istDate.getMonth();
  
  let hours = istDate.getHours();
  const minutes = istDate.getMinutes().toString().padStart(2, '0');

  const ampm = hours >= 12 ? 'pm' : 'am';

  hours = hours % 12 || 12;

  const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

  return `${day} ${monthNames[month]}, ${hours}:${minutes} ${ampm}`;
};

/**
 * Format date in IST with full date time
 */
export const formatISTFull = (utcDateString: string): string => {
  const istDate = convertToIST(utcDateString);
  
  const day = istDate.getUTCDate().toString().padStart(2, '0');
  const month = (istDate.getUTCMonth() + 1).toString().padStart(2, '0');
  const year = istDate.getUTCFullYear();
  
  let hours = istDate.getUTCHours();
  const minutes = istDate.getUTCMinutes().toString().padStart(2, '0');
  const seconds = istDate.getUTCSeconds().toString().padStart(2, '0');
  
  const ampm = hours >= 12 ? 'pm' : 'am';
  hours = hours % 12;
  hours = hours ? hours : 12;
  
  return `${day}/${month}/${year}, ${hours}:${minutes}:${seconds} ${ampm}`;
};

/**
 * Format just the date in IST
 */
export const formatISTDate = (utcDateString: string): string => {
  const istDate = convertToIST(utcDateString);
  
  const day = istDate.getUTCDate().toString().padStart(2, '0');
  const month = (istDate.getUTCMonth() + 1).toString().padStart(2, '0');
  const year = istDate.getUTCFullYear();
  
  return `${day}/${month}/${year}`;
};
