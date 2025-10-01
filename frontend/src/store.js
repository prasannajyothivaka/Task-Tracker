import { createStore, combineReducers, applyMiddleware } from "redux";
import thunk from "redux-thunk";
import { composeWithDevTools } from "redux-devtools-extension";

import taskReducer from "./features/taskSlice";
import userReducer from "./features/userSlice";
import projectReducer from "./features/projectSlice";
import authReducer from "./features/authSlice";
import { injectStore } from "./api/axiosInstance";

// ------------------- Combine Reducers -------------------
const reducer = combineReducers({
  projects: projectReducer,
  tasks: taskReducer,
  getUsers: userReducer,
  userLogin: authReducer, // <-- Keep this key as "userLogin"
});

// ------------------- Load userInfo from localStorage -------------------
const userInfoFromStorage = localStorage.getItem("userInfo")
  ? JSON.parse(localStorage.getItem("userInfo"))
  : null;

// ------------------- Initial State -------------------
const initialState = {
  userLogin: { userInfo: userInfoFromStorage },
};

const middleware = [thunk];

// ------------------- Create Store -------------------
const store = createStore(
  reducer,
  initialState,
  composeWithDevTools(applyMiddleware(...middleware))
);

injectStore(store);

export default store;
