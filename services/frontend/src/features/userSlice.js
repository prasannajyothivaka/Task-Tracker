import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axiosInstance from "../api/axiosInstance";


// Async thunk to fetch users by role
export const fetchUsers = createAsyncThunk(
  "users/fetchUsers",
  async (roleId, { rejectWithValue }) => {
    try {
      // No need to pass token manually; interceptor adds it
      const { data } = await axiosInstance.get(`/users/get_all_users/${roleId}`);
      return data.data; // API returns { message, status, data }
    } catch (error) {
      return rejectWithValue(
        error.response?.data?.detail || error.message
      );
    }
  }
);

const userSlice = createSlice({
  name: "users",
  initialState: {
    users: [],
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchUsers.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUsers.fulfilled, (state, action) => {
        state.loading = false;
        state.users = action.payload;
      })
      .addCase(fetchUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export default userSlice.reducer;
