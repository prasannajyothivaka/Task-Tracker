import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import axiosInstance from "../api/axiosInstance";

// --------------------- Async Thunks ---------------------

// Get all tasks
export const fetchTasks = createAsyncThunk(
  "tasks/fetchTasks",
  async ({ keyword = "", page = 1 }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get("/tasks/", {
        params: { keyword, page },
      });
      return data.data; // {tasks, page, pages, total}
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

// Update single column (status / assigned_to / due_date etc)
export const updateTaskColumn = createAsyncThunk(
  "tasks/updateTaskColumn",
  async ({ taskId, column, value }, { rejectWithValue }) => {
    try {
      const payload = { [column]: value };
      const { data } = await axiosInstance.post(`/tasks/edit/${taskId}/`, payload);
      return data.data; // updated task
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

// Fetch single task
export const fetchTaskDetails = createAsyncThunk(
  "tasks/fetchTaskDetails",
  async ({ taskId }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.get(`/tasks/${taskId}/`);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

// Create task
export const createTask = createAsyncThunk(
  "tasks/createTask",
  async (task, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.post("/tasks/", task);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

// Update task
export const updateTask = createAsyncThunk(
  "tasks/updateTask",
  async ({ taskId, task }, { rejectWithValue }) => {
    try {
      const { data } = await axiosInstance.post(`/tasks/update/${taskId}/`, task);
      return data;
    } catch (err) {
      return rejectWithValue(err.response?.data?.detail || err.message);
    }
  }
);

// Delete task
export const deleteTask = createAsyncThunk(
  "tasks/deleteTask",
  async (taskId, { rejectWithValue }) => {
    try {
      await axiosInstance.delete(`/tasks/${taskId}`);
      return taskId; // return deleted id
    } catch (err) {
      return rejectWithValue(err.response?.data?.message || "Failed to delete task");
    }
  }
);

// --------------------- Slice ---------------------
const taskSlice = createSlice({
  name: "tasks",
  initialState: {
    tasks: [],
    page: 1,
    pages: 1,
    total: 0,
    task: null,
    loading: false,
    error: null,
    success: false,
  },

  reducers: {
    resetTaskState: (state) => {
      state.task = null;
      state.tasks = [];
      state.loading = false;
      state.error = null;
      state.success = false;
    },
  },

  extraReducers: (builder) => {
    builder
      // Get all tasks
      .addCase(fetchTasks.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTasks.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = action.payload.tasks;
        state.page = action.payload.page;
        state.pages = action.payload.pages;
        state.total = action.payload.total;
      })
      .addCase(fetchTasks.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Get single task
      .addCase(fetchTaskDetails.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchTaskDetails.fulfilled, (state, action) => {
        state.loading = false;
        state.task = action.payload;
      })
      .addCase(fetchTaskDetails.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Create task
      .addCase(createTask.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(createTask.fulfilled, (state, action) => {
        state.loading = false;
        state.task = action.payload;
        state.success = true;
      })
      .addCase(createTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update task
      .addCase(updateTask.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateTask.fulfilled, (state, action) => {
        state.loading = false;
        state.task = action.payload;
        state.success = true;

        // update tasks list if already loaded
        const index = state.tasks.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) {
          state.tasks[index] = action.payload;
        }
      })
      .addCase(updateTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Delete task
      .addCase(deleteTask.pending, (state) => {
        state.loading = true;
      })
      .addCase(deleteTask.fulfilled, (state, action) => {
        state.loading = false;
        state.tasks = state.tasks.filter((t) => t.id !== action.payload);
      })
      .addCase(deleteTask.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update single column
      .addCase(updateTaskColumn.pending, (state) => {
        state.loading = true;
        state.error = null;
        state.success = false;
      })
      .addCase(updateTaskColumn.fulfilled, (state, action) => {
        state.loading = false;
        state.success = true;
        state.task = action.payload;

        // update tasks list if already loaded
        const index = state.tasks.findIndex((t) => t.id === action.payload.id);
        if (index !== -1) state.tasks[index] = action.payload;
      })
      .addCase(updateTaskColumn.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { resetTaskState } = taskSlice.actions;
export default taskSlice.reducer;
