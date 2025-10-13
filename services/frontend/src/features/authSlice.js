// src/slices/authSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axios from "axios";
import axiosInstance from "../api/axiosInstance"; // ✅ use centralized axios

// --------------------- Async Thunks ---------------------

// Login
export const login = createAsyncThunk(
  "auth/login",
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const { data } = await axiosInstance.post("/login/", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      // ✅ Store both tokens
      localStorage.setItem("userInfo", JSON.stringify(data.data));
      localStorage.setItem("access_token", data.data.token);
      localStorage.setItem("refresh_token", data.data.refresh_token); // if backend provides it

      return data.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// SSO Login
export const ssoLogin = createAsyncThunk(
  "auth/ssoLogin",
  async ({ token }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.post("/sso-login", { token });

      const userData = {
        ...data.data,
        token: data.data.token, // access token
        refresh_token: data.data.refresh_token, // refresh token
      };

      localStorage.setItem("userInfo", JSON.stringify(userData));
      localStorage.setItem("access_token", data.data.token);
      localStorage.setItem("refresh_token", data.data.refresh_token);

      return userData;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Refresh access token
export const refreshAccessToken = createAsyncThunk(
  "auth/refreshToken",
  async (_, { rejectWithValue }) => {
    try {
      const refresh_token = localStorage.getItem("refresh_token");

      if (!refresh_token) {
        throw new Error("No refresh token available");
      }

      // Check if refresh token itself is expired
      const isRefreshTokenExpired = (token) => {
        try {
          const payload = JSON.parse(atob(token.split(".")[1]));
          const currentTime = Date.now() / 1000;
          return payload.exp < currentTime;
        } catch (parseError) {
          console.warn("Failed to parse refresh token:", parseError.message);
          return true;
        }
      };

      if (isRefreshTokenExpired(refresh_token)) {
        throw new Error("Refresh token expired");
      }

      // Create a basic axios instance to avoid circular dependencies
      const basicAxios = axios.create({
        baseURL: process.env.REACT_APP_API_URL || "http://localhost:8000",
      });

      const { data } = await basicAxios.post("/refresh-token", {
        refresh_token,
      });

      // Update stored access token
      const userInfo = JSON.parse(localStorage.getItem("userInfo"));
      if (userInfo) {
        userInfo.token = data.data.token;
        localStorage.setItem("userInfo", JSON.stringify(userInfo));
        localStorage.setItem("access_token", data.data.token);
      }

      return data.data.token;
    } catch (error) {
      // Clear tokens on failure
      localStorage.removeItem("userInfo");
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      // If it's a network error, don't immediately redirect
      if (!error.response) {
        console.warn("Network error during token refresh:", error.message);
      }

      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Logout
export const logout = createAsyncThunk(
  "auth/logout",
  async (_, { dispatch }) => {
    localStorage.removeItem("userInfo");
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");

    // Clear any ongoing token checks
    if (typeof window !== "undefined" && window.tokenCheckInterval) {
      clearInterval(window.tokenCheckInterval);
    }

    dispatch(authSlice.actions.resetAll());
  }
);

// Register
export const register = createAsyncThunk(
  "auth/register",
  async ({ name, email, password }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.post("/users/register/", {
        name,
        email,
        password,
      });
      localStorage.setItem("userInfo", JSON.stringify(data));
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Get User Profile (self)
export const getUserProfile = createAsyncThunk(
  "auth/getUserProfile",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get("/users/profile/");
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Update Profile
export const updateUserProfile = createAsyncThunk(
  "auth/updateUserProfile",
  async (user, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.put("/users/profile/update/", user);
      localStorage.setItem("userInfo", JSON.stringify(data));
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Get User by ID (admin)
export const getUserById = createAsyncThunk(
  "auth/getUserById",
  async (id, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get(`/users/${id}/`);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// List Users (admin)
export const listUsers = createAsyncThunk(
  "auth/listUsers",
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get("/users/userlist");
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Delete User (admin)
export const deleteUser = createAsyncThunk(
  "auth/deleteUser",
  async (id, { rejectWithValue }) => {
    try {
      await axiosInstance.delete(`/users/delete_user/${id}`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Update User by ID (admin)
export const updateUser = createAsyncThunk(
  "auth/updateUser",
  async ({ id, user }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.put(`/users/${id}/`, user);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Update User Role (admin)
export const updateUserRole = createAsyncThunk(
  "auth/updateUserRole",
  async ({ user_id, role_id }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.put(
        `/users/update_role/?user_id=${user_id}&role_id=${role_id}`,
        {}
      );
      return { user_id, role_id, message: data.message };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// --------------------- Slice ---------------------
const userInfoFromStorage = localStorage.getItem("userInfo")
  ? JSON.parse(localStorage.getItem("userInfo"))
  : null;

const initialState = {
  userInfo: userInfoFromStorage,
  user: {},
  users: [],
  loading: false,
  error: null,
  success: false,
};

const authSlice = createSlice({
  name: "auth",
  initialState,
  reducers: {
    resetAll: (state) => {
      state.userInfo = null;
      state.user = {};
      state.users = [];
      state.loading = false;
      state.error = null;
      state.success = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.userInfo = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // SSO Login
      .addCase(ssoLogin.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(ssoLogin.fulfilled, (state, action) => {
        state.loading = false;
        state.userInfo = action.payload;
      })
      .addCase(ssoLogin.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Refresh Token
      .addCase(refreshAccessToken.pending, (state) => {
        state.loading = true;
      })
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.loading = false;
        if (state.userInfo) {
          state.userInfo.token = action.payload;
        }
      })
      .addCase(refreshAccessToken.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.userInfo = null; // Logout on refresh failure
      })

      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.loading = false;
        state.userInfo = action.payload;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Get Profile
      .addCase(getUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(getUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update Profile
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.userInfo = action.payload;
        state.success = true;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Get User By ID
      .addCase(getUserById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(getUserById.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload;
      })
      .addCase(getUserById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // List Users
      .addCase(listUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(listUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload;
      })
      .addCase(listUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete User
      .addCase(deleteUser.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(deleteUser.fulfilled, (state) => {
        state.loading = false;
        state.success = true;
      })
      .addCase(deleteUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
        state.success = false;
      })

      // Update User Role
      .addCase(updateUserRole.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateUserRole.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;

        const { user_id, role_id } = action.payload;

        // Update role in nested or flat users structure
        if (state.users?.data) {
          Object.keys(state.users.data).forEach((role) => {
            const userIndex = state.users.data[role].findIndex(
              (u) => u.id === user_id
            );
            if (userIndex !== -1) {
              state.users.data[role][userIndex].role_id = role_id;
              const roleNames = { 1: "Admin", 2: "TaskCreator", 3: "User" };
              state.users.data[role][userIndex].role_name = roleNames[role_id];
            }
          });
        } else if (Array.isArray(state.users)) {
          const userIndex = state.users.findIndex((u) => u.id === user_id);
          if (userIndex !== -1) {
            state.users[userIndex].role_id = role_id;
            const roleNames = { 1: "Admin", 2: "TaskCreator", 3: "User" };
            state.users[userIndex].role_name = roleNames[role_id];
          }
        }
      })
      .addCase(updateUserRole.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update User
      .addCase(updateUser.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateUser.fulfilled, (state) => {
        state.loading = false;
        state.success = true;
      })
      .addCase(updateUser.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { resetAll } = authSlice.actions;
export default authSlice.reducer;
