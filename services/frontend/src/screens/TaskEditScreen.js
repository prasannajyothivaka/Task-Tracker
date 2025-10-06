import React, { useState, useEffect, useRef } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { Form, Button, Alert, Spinner } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import FormContainer from "../components/FormContainer";
import {
  fetchTaskDetails,
  updateTask,
  createTask,
  resetTaskState,
} from "../features/taskSlice";
import { fetchUsers } from "../features/userSlice";
import { listProjectDetails } from "../features/projectSlice";

function TaskEditScreen() {
  const { taskId } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const initialTask = location.state?.task;
  const projectId = location.state?.projectId;

  const { task, loading, error, success } = useSelector((state) => state.tasks);
  const { userInfo } = useSelector((state) => state.userLogin);
  const { users } = useSelector((state) => state.getUsers);

  useEffect(() => {
    console.log("taskId from URL:", taskId);
    console.log("initialTask from location.state:", initialTask);
    console.log("projectId from location.state:", projectId);
  }, [taskId, initialTask, projectId]);

  const topRef = useRef(null);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    status: "pending",
    priority: "medium",
    assigned_to: "",
    project_id: projectId || "",
    start_date: "",
    due_date: "",
  });

  const [isDirty, setIsDirty] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  // Scroll to top on mount
  useEffect(() => {
    if (topRef.current) topRef.current.scrollIntoView({ behavior: "smooth" });
  }, []);

  // Pre-fill form
  useEffect(() => {
    if (initialTask) {
      setFormData({ ...initialTask });
    } else if (taskId) {
      dispatch(fetchTaskDetails({ taskId, token: userInfo?.token }));
    } else {
      dispatch(resetTaskState());
    }

    if (userInfo?.token) {
      dispatch(fetchUsers(3));
    }
  }, [dispatch, taskId, userInfo?.token, initialTask]);

  // Update form when task comes from API
  useEffect(() => {
    if (task && taskId && !initialTask) {
      setFormData({ ...task });
    }
  }, [task, taskId, initialTask]);

  useEffect(() => {
    if (
      formData.due_date &&
      formData.start_date &&
      formData.due_date < formData.start_date
    ) {
      setFormData((prev) => ({ ...prev, due_date: formData.start_date }));
    }
  }, [formData.start_date]);

  // Handle success
  useEffect(() => {
    if (success) {
      // Refresh project details
      if (projectId) {
        dispatch(listProjectDetails(projectId));
      }
      setShowSuccess(true);

      // Navigate back after short delay
      const timer = setTimeout(() => {
        navigate(-1, { state: { updated: true } });
        dispatch(resetTaskState()); // Move this here, after navigation
      }, 1200);

      return () => clearTimeout(timer);
    }
  }, [success, dispatch, navigate, projectId]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setIsDirty(true);
  };

  const submitHandler = (e) => {
    e.preventDefault();
    if (taskId) {
      console.log("taskId:", taskId);
      dispatch(updateTask({ taskId, task: formData, token: userInfo?.token }));
    } else {
      dispatch(createTask({ task: formData, token: userInfo?.token }));
    }
    setIsDirty(false);
  };

  return (
    <div ref={topRef}>
      <Button variant="light" className="mb-3" onClick={() => navigate(-1)}>
        ← Go Back
      </Button>

      <FormContainer>
        <h1>{taskId ? "Edit Task" : "Create Task"}</h1>
        {loading && (
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" />
          </div>
        )}
        {error && <Alert variant="danger">{error}</Alert>}
        {showSuccess && (
          <Alert variant="success">Task updated successfully!</Alert>
        )}

        <Form onSubmit={submitHandler}>
          {/* Title */}
          <Form.Group controlId="title" className="mb-3">
            <Form.Label>
              Title <span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="text"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
            />
          </Form.Group>

          {/* Description */}
          <Form.Group controlId="description" className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              name="description"
              value={formData.description}
              onChange={handleChange}
            />
          </Form.Group>

          {/* Status */}
          <Form.Group controlId="status" className="mb-3">
            <Form.Label>Status</Form.Label>
            <Form.Select
              name="status"
              value={formData.status}
              onChange={handleChange}
            >
              <option value="pending">Pending</option>
              <option value="in_progress">In Progress</option>
              <option value="completed">Completed</option>
            </Form.Select>
          </Form.Group>

          {/* Priority */}
          <Form.Group controlId="priority" className="mb-3">
            <Form.Label>Priority</Form.Label>
            <Form.Select
              name="priority"
              value={formData.priority}
              onChange={handleChange}
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </Form.Select>
          </Form.Group>

          {/* Assigned To */}
          <Form.Group controlId="assignedTo" className="mb-3">
            <Form.Label>
              Assigned To<span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Select
              name="assigned_to"
              value={formData.assigned_to}
              onChange={handleChange}
            >
              <option value="">-- Select User --</option>
              {users?.map((user) => (
                <option key={user.id} value={user.id}>
                  {user.first_name} {user.last_name}
                </option>
              ))}
            </Form.Select>
          </Form.Group>

          {/* Start Date */}
          <Form.Group controlId="startDate" className="mb-3">
            <Form.Label>
              Start Date<span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="date"
              name="start_date"
              min={taskId ? undefined : new Date().toISOString().split("T")[0]}
              value={formData.start_date}
              onChange={handleChange}
              required
            />
          </Form.Group>

          {/* Due Date */}
          <Form.Group controlId="dueDate" className="mb-3">
            <Form.Label>
              Due Date <span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="date"
              name="due_date"
              value={formData.due_date}
              min={
                formData.start_date || new Date().toISOString().split("T")[0]
              }
              onChange={handleChange}
              required
              disabled={!formData.start_date}
            />
          </Form.Group>

          <Button
            type="submit"
            variant="primary"
            disabled={!isDirty || loading}
            onClick={() => window.scrollTo(0, 0)}
          >
            {taskId ? "Update Task" : "Create Task"}
          </Button>
        </Form>
      </FormContainer>
    </div>
  );
}

export default TaskEditScreen;
