/**
 * Shared utility functions for the Master Gateway frontend.
 */

/**
 * Extracts a human-readable error message from an Axios error response.
 * Handles FastAPI/Pydantic validation error formats, plain string details,
 * and generic error objects.
 */
export const handleAxiosError = (err: any, defaultMsg: string): string => {
  const detail = err.response?.data?.detail;
  if (typeof detail === 'string') {
    return detail;
  }
  if (Array.isArray(detail)) {
    return detail
      .map((d: any) =>
        d.msg ? d.msg.replace(/^Value error, /, '') : JSON.stringify(d)
      )
      .join(', ');
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  if (typeof err.response?.data === 'string') {
    return err.response.data;
  }
  if (err.response?.data?.message) {
    return err.response.data.message;
  }
  return err.message || defaultMsg;
};
