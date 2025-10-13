import { useEffect, useCallback } from 'react';
import { useDispatch } from 'react-redux';
import { refreshAccessToken, logout } from '../features/authSlice';

export const useTokenManager = () => {
  const dispatch = useDispatch();

  const isTokenExpired = useCallback((token) => {
    if (!token) return true;
    
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;
      // Consider token expired if it expires within 5 minutes
      return payload.exp < (currentTime + 300);
    } catch (error) {
      console.warn("Failed to parse token:", error.message);
      return true;
    }
  }, []);

  const checkTokenValidity = useCallback(async () => {
    const userInfo = localStorage.getItem("userInfo");
    if (!userInfo) return;

    const { token } = JSON.parse(userInfo);
    if (isTokenExpired(token)) {
      try {
        await dispatch(refreshAccessToken()).unwrap();
      } catch (error) {
        console.warn("Token refresh failed, logging out:", error);
        dispatch(logout());
      }
    }
  }, [dispatch, isTokenExpired]);

  useEffect(() => {
    // Check token validity on mount
    checkTokenValidity();

    // Set up periodic token checking (every 5 minutes)
    const interval = setInterval(checkTokenValidity, 5 * 60 * 1000);

    // Set up visibility change handler
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        // User returned to the app
        checkTokenValidity();
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Cleanup
    return () => {
      clearInterval(interval);
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [checkTokenValidity]);

  return {
    checkTokenValidity,
    isTokenExpired
  };
};

export default useTokenManager;