import axios from "axios";
import { logout } from "../features/authSlice";

let store;
export const injectStore = (_store) => {
  store = _store;
};

// Determine baseURL dynamically
const baseURL =
  process.env.NODE_ENV === "production"
    ? (process.env.REACT_APP_API_BASE_URL || "") + "/api" // for production build
    : ""; // empty for local dev (proxy in package.json handles it)

const axiosInstance = axios.create({
  baseURL,
  headers: { "Content-Type": "application/json" },
});

// Add token to headers
axiosInstance.interceptors.request.use((config) => {
  const token = store?.getState()?.userLogin?.userInfo?.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 globally
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn("Unauthorized, dispatching logout...");
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
