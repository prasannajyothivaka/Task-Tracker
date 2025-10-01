// src/slices/projectSlice.js
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axiosInstance from "../api/axiosInstance"; // ✅ use centralized axios

// -------------------- Async Thunks --------------------

// List projects
export const listProjects = createAsyncThunk(
  "projects/listProjects",
  async ({ keyword = "", page = "1" }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get(
        `/projects?keyword=${keyword}&page=${page}`
      );
      return data.data; // payload for success
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Get project details
export const listProjectDetails = createAsyncThunk(
  "projects/listProjectDetails",
  async (id, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get(`/projects/${id}/`);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Delete project
export const deleteProject = createAsyncThunk(
  "projects/deleteProject",
  async (id, { rejectWithValue }) => {
    try {
      await axiosInstance.delete(`/projects/delete/${id}/`);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Create project
export const createProject = createAsyncThunk(
  "projects/createProject",
  async (projectData, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.post(`/projects/create/`, projectData);
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// Update project
export const updateProject = createAsyncThunk(
  "projects/updateProject",
  async (project, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.put(
        `/projects/update/${project.id}/`,
        project
      );
      return data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || error.message);
    }
  }
);

// -------------------- Slice --------------------
const projectSlice = createSlice({
  name: "projects",
  initialState: {
    projects: [],
    project: {},
    loading: false,
    error: null,
    success: false,
    page: 1,
    pages: 1,
  },
  reducers: {
    resetCreate: (state) => {
      state.project = {};
      state.success = false;
      state.error = null;
      state.loading = false;
    },
    resetUpdate: (state) => {
      state.project = {};
      state.success = false;
      state.error = null;
      state.loading = false;
    },
  },
  extraReducers: (builder) => {
    builder
      // List projects
      .addCase(listProjects.pending, (state) => {
        state.loading = true;
        state.projects = [];
      })
      .addCase(listProjects.fulfilled, (state, action) => {
        state.loading = false;
        state.projects = action.payload.projects || action.payload || [];
        state.page = action.payload.page || 1;
        state.pages = action.payload.pages || 1;
      })
      .addCase(listProjects.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Project details
      .addCase(listProjectDetails.pending, (state) => {
        state.loading = true;
      })
      .addCase(listProjectDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.project = action.payload;
      })
      .addCase(listProjectDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete project
      .addCase(deleteProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.projects = state.projects.filter(
          (proj) => proj.id !== action.payload
        );
      })
      .addCase(deleteProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Create project
      .addCase(createProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.project = action.payload;
        state.projects.push(action.payload);
      })
      .addCase(createProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update project
      .addCase(updateProject.pending, (state) => {
        state.loading = true;
      })
      .addCase(updateProject.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.project = action.payload;
        state.projects = state.projects.map((proj) =>
          proj.id === action.payload.id ? action.payload : proj
        );
      })
      .addCase(updateProject.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { resetCreate, resetUpdate } = projectSlice.actions;
export default projectSlice.reducer;
