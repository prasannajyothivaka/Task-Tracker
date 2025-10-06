import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { Form, Button, Spinner } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import Message from "../components/Message";
import FormContainer from "../components/FormContainer";
import {
  updateProject,
  createProject,
  resetCreate,
  resetUpdate,
} from "../features/projectSlice";

function ProjectEditScreen() {
  const { projectId } = useParams(); // undefined for create
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const isEditMode = !!projectId;

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [status, setStatus] = useState("active");
  const [isActive, setIsActive] = useState(true);

  // ✅ Get state from slice
  const { project, loading, error, success } = useSelector(
    (state) => state.projects
  );

  // Populate form fields if editing
  useEffect(() => {
    if (isEditMode && location.state?.project) {
      const p = location.state.project;
      setName(p.name || "");
      setDescription(p.description || "");
      setStartDate(p.start_date?.split("T")[0] || "");
      setEndDate(p.end_date?.split("T")[0] || "");
      setStatus(p.status || "active");
      setIsActive(p.is_active ?? true);
    }
  }, [isEditMode, location.state]);

  // Handle success (update or create)
  useEffect(() => {
    if (isEditMode && success) {
      dispatch(resetUpdate());
      navigate(`/project/${projectId}`, { state: { updated: true } });
    } else if (!isEditMode && success) {
      dispatch(resetCreate());
      navigate(`/`);
    }
  }, [success, dispatch, navigate, projectId, isEditMode]);

  const submitHandler = (e) => {
    e.preventDefault();
    const projectData = {
      name,
      description,
      start_date: startDate,
      end_date: endDate,
      status,
      is_active: isActive,
    };

    if (isEditMode) {
      dispatch(updateProject({ id: projectId, ...projectData }));
    } else {
      dispatch(createProject(projectData));
    }
  };

  return (
    <div>
      <Button variant="light" className="my-3" onClick={() => navigate(-1)}>
        &larr; Go Back
      </Button>
      <FormContainer>
        <h1>{isEditMode ? "Edit Project" : "Create Project"}</h1>
        {loading && (
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" />
          </div>
        )}
        {error && <Message variant="danger">{error}</Message>}
        <Form onSubmit={submitHandler}>
          <Form.Group controlId="name" className="mb-3">
            <Form.Label>
              Name<span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter project name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group controlId="description" className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Form.Group>

          <Form.Group controlId="startDate" className="mb-3">
            <Form.Label>
              Start Date<span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="date"
              min={new Date().toISOString().split("T")[0]}
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
              disabled={isEditMode}
            />
          </Form.Group>

          <Form.Group controlId="endDate" className="mb-3">
            <Form.Label>
              End Date<span style={{ color: "red" }}>*</span>
            </Form.Label>
            <Form.Control
              type="date"
              name="due_date"
              value={endDate}
              min={startDate || new Date().toISOString().split("T")[0]}
              onChange={(e) => setEndDate(e.target.value)}
              disabled={!startDate}
            />
          </Form.Group>

          <Form.Group controlId="status" className="mb-3">
            <Form.Label>Status</Form.Label>
            <Form.Control
              as="select"
              value={status}
              onChange={(e) => setStatus(e.target.value)}
            >
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="completed">Completed</option>
            </Form.Control>
          </Form.Group>

          <Button type="submit" variant="primary">
            {isEditMode ? "Update Project" : "Create Project"}
          </Button>
        </Form>
      </FormContainer>
    </div>
  );
}

export default ProjectEditScreen;
