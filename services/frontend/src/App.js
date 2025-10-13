import { Container } from "react-bootstrap";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { useSelector } from "react-redux";
import Header from "./components/Header";
import Footer from "./components/Footer";
import HomeScreen from "./screens/HomeScreen";
import ProductScreen from "./screens/ProjectScreen";
import TaskScreen from "./screens/TaskScreen";
import LoginScreen from "./screens/LoginScreen";
import RegisterScreen from "./screens/RegisterScreen";
import ProfileScreen from "./screens/ProfileScreen";
import UserListScreen from "./screens/UserListScreen";
import UserEditScreen from "./screens/UserEditScreen";
import ProjectListScreen from "./screens/ProjectListScreen";
import ProjectEditScreen from "./screens/ProjectEditScreen";
import TaskEditScreen from "./screens/TaskEditScreen";
import GoogleSSO from "./components/Login";
import PrivateRoute from "./components/PrivateRoute";
import useTokenManager from "./hooks/useTokenManager";

function App() {
  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin || {};
  const useDevLogin = process.env.REACT_APP_DEV === "false" ? false : true;

  // Initialize token manager for the entire app
  useTokenManager();

  console.log("useDevLogin:", useDevLogin);

  return (
    <Router>
      {/* <GoogleSSO /> */}
      {userInfo && <Header />}

      <main className="py-3">
        <Container>
          <Routes>
            {/* Public routes */}
            <Route
              path="/login"
              // element={useDevLogin ? <LoginScreen /> : <GoogleSSO />}
              element={<GoogleSSO />}
            />
            <Route path="/register" element={<RegisterScreen />} />

            {/* Private routes */}
            <Route
              path="/"
              element={
                <PrivateRoute>
                  <HomeScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <PrivateRoute>
                  <ProfileScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/tasks"
              element={
                <PrivateRoute>
                  <TaskScreen />
                </PrivateRoute>
              }
            />

            <Route
              path="/project/:id"
              element={
                <PrivateRoute>
                  <ProductScreen />
                </PrivateRoute>
              }
            />

            {/* Admin routes */}
            <Route
              path="/admin/userlist"
              element={
                <PrivateRoute>
                  <UserListScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/admin/user/:userId/edit"
              element={
                <PrivateRoute>
                  <UserEditScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/admin/projectlist"
              element={
                <PrivateRoute>
                  <ProjectListScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/admin/project/:projectId/edit"
              element={
                <PrivateRoute>
                  <ProjectEditScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/project/create"
              element={
                <PrivateRoute>
                  <ProjectEditScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/task/:taskId/edit"
              element={
                <PrivateRoute>
                  <TaskEditScreen />
                </PrivateRoute>
              }
            />
            <Route
              path="/task/create"
              element={
                <PrivateRoute>
                  <TaskEditScreen />
                </PrivateRoute>
              }
            />
          </Routes>
        </Container>
      </main>
      {userInfo && <Footer />}
    </Router>
  );
}

export default App;
