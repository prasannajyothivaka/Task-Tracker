import axios from "axios";
import store from "../store"; // Import your Redux store
import { refreshAccessToken } from "../features/authSlice";

const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
});

let isRefreshing = false;
let failedQueue = [];

// Helper function to decode JWT and check expiration
const isTokenExpired = (token) => {
  if (!token) return true;

  try {
    const payload = JSON.parse(atob(token.split(".")[1]));
    const currentTime = Date.now() / 1000;
    // Check if token expires within 5 minutes
    return payload.exp < currentTime + 300;
  } catch (parseError) {
    console.warn(
      "Failed to parse token for expiration check:",
      parseError.message
    );
    return true;
  }
};

// Helper function to get fresh token from localStorage
const getStoredToken = () => {
  const userInfo = localStorage.getItem("userInfo");
  if (userInfo) {
    const { token } = JSON.parse(userInfo);
    return token;
  }
  return null;
};

const processQueue = (error, token = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor - Add access token and proactively refresh if needed
axiosInstance.interceptors.request.use(
  async (config) => {
    let token = getStoredToken();

    // Check if token is expired or about to expire
    if (token && isTokenExpired(token)) {
      if (!isRefreshing) {
        isRefreshing = true;

        try {
          const resultAction = await store.dispatch(refreshAccessToken());

          if (refreshAccessToken.fulfilled.match(resultAction)) {
            token = resultAction.payload;
          } else {
            // Refresh failed, redirect to login
            window.location.href = "/login";
            return Promise.reject(new Error("Token refresh failed"));
          }
        } catch (error) {
          window.location.href = "/login";
          return Promise.reject(error);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Wait for ongoing refresh
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then(() => {
          token = getStoredToken();
          config.headers.Authorization = `Bearer ${token}`;
          return config;
        });
      }
    }

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor - Auto refresh on 401
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Check if error is 401 and not already retried
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue this request while refresh is in progress
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return axiosInstance(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Dispatch refresh action
        const resultAction = await store.dispatch(refreshAccessToken());

        if (refreshAccessToken.fulfilled.match(resultAction)) {
          const newToken = resultAction.payload;

          processQueue(null, newToken);
          originalRequest.headers.Authorization = `Bearer ${newToken}`;

          return axiosInstance(originalRequest);
        } else {
          // Refresh failed
          processQueue(error, null);
          window.location.href = "/login";
          return Promise.reject(error);
        }
      } catch (refreshError) {
        processQueue(refreshError, null);
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// Handle page visibility changes - refresh token when user returns to app
let visibilityChangeHandler;

const setupVisibilityListener = () => {
  if (visibilityChangeHandler) {
    document.removeEventListener("visibilitychange", visibilityChangeHandler);
  }

  visibilityChangeHandler = async () => {
    if (!document.hidden) {
      // User returned to the app, check token validity
      const token = getStoredToken();
      if (token && isTokenExpired(token)) {
        try {
          await store.dispatch(refreshAccessToken());
        } catch (error) {
          console.warn(
            "Token refresh failed on page visibility change:",
            error
          );
          window.location.href = "/login";
        }
      }
    }
  };

  document.addEventListener("visibilitychange", visibilityChangeHandler);
};

// Initialize visibility listener
if (typeof document !== "undefined") {
  setupVisibilityListener();
}

// Periodic token check (every 10 minutes)
let tokenCheckInterval;

const startTokenChecker = () => {
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval);
  }

  tokenCheckInterval = setInterval(async () => {
    const token = getStoredToken();
    if (token && isTokenExpired(token)) {
      try {
        await store.dispatch(refreshAccessToken());
      } catch (error) {
        console.warn("Periodic token refresh failed:", error);
        clearInterval(tokenCheckInterval);
        window.location.href = "/login";
      }
    }
  }, 10 * 60 * 1000); // Check every 10 minutes
};

// Start periodic checker
if (typeof window !== "undefined") {
  startTokenChecker();
}

export default axiosInstance;