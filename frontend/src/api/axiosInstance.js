import axios from "axios";
import { logout } from "../features/authSlice";

let store;

export const injectStore = (_store) => {
  store = _store;
};

const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL + "/api",
  headers: { "Content-Type": "application/json" },
});

axiosInstance.interceptors.request.use((config) => {
  const token = store?.getState()?.userLogin?.userInfo?.token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

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
