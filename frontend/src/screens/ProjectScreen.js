import React, { useEffect } from "react";
import { Link, useParams, useNavigate, useLocation } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import {
  Card,
  ListGroup,
  Button,
  Badge,
  Row,
  Col,
  Spinner,
} from "react-bootstrap";
import Message from "../components/Message";
import { listProjectDetails } from "../features/projectSlice";

function ProjectScreen() {
  const { id } = useParams();
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const { project, loading, error } = useSelector((state) => state.projects);

  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin || {};

  const projectData = project?.data?.project;
  const tasks = project?.data?.tasks || [];

  // Fetch project details when coming back from edit
  useEffect(() => {
    if (location.state?.updated) {
      dispatch(listProjectDetails(id));
      navigate(location.pathname, { replace: true, state: {} });
    } else if (!projectData || projectData.id !== Number(id)) {
      dispatch(listProjectDetails(id));
    }
  }, [dispatch, id, location, navigate, projectData]);

  const editProjectHandler = () => {
    navigate(`/admin/project/${id}/edit`, { state: { project: projectData } });
  };

  const formatDate = (dateString) =>
    dateString ? new Date(dateString).toLocaleDateString() : "N/A";

  // Safe error rendering
  const renderError = (err) => {
    if (!err) return null;
    if (Array.isArray(err)) return err.map((e) => e.msg).join(", ");
    if (typeof err === "string") return err;
    return JSON.stringify(err);
  };

  return (
    <div>
      <Link to="/" className="btn btn-light my-3">
        &larr; Go Back
      </Link>

      {loading ? (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      ) : error ? (
        <Message variant="danger">{renderError(error)}</Message>
      ) : projectData ? (
        <div>
          {/* Project Card */}
          <Card className="mb-4 shadow-sm">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <h2 className="mb-0">{projectData.name}</h2>
              {userInfo?.role_id === 1 && (
                <Button
                  variant="primary"
                  style={{ backgroundColor: "#0066FF", borderColor: "#0066FF" }}
                  onClick={editProjectHandler}
                >
                  Edit Project
                </Button>
              )}
            </Card.Header>
            <ListGroup variant="flush">
              <ListGroup.Item>
                <strong>Description:</strong> {projectData.description}
              </ListGroup.Item>
              <ListGroup.Item>
                <strong>Status:</strong>{" "}
                <Badge
                  bg={projectData.status === "active" ? "success" : "secondary"}
                >
                  {projectData.status}
                </Badge>
              </ListGroup.Item>
              <ListGroup.Item>
                <strong>Start Date:</strong>{" "}
                {formatDate(projectData.start_date)}
              </ListGroup.Item>
              <ListGroup.Item>
                <strong>End Date:</strong> {formatDate(projectData.end_date)}
              </ListGroup.Item>
              <ListGroup.Item>
                <strong>Created On:</strong>{" "}
                {formatDate(projectData.created_on)}
              </ListGroup.Item>
              <ListGroup.Item>
                <strong>Updated On:</strong>{" "}
                {formatDate(projectData.updated_on)}
              </ListGroup.Item>
            </ListGroup>
          </Card>

          {/* Tasks Section */}
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h3 className="mb-3">Tasks</h3>
            {(userInfo?.role_id === 1 || userInfo?.role_id === 2) && (
              <Button
                variant="primary"
                size="sm"
                style={{ backgroundColor: "#0066FF", borderColor: "#0066FF" }}
                onClick={() =>
                  navigate(`/task/create`, {
                    state: { projectId: projectData.id },
                  })
                }
              >
                + Create Task
              </Button>
            )}
          </div>
          {tasks.length > 0 ? (
            <Row xs={1} md={2} lg={3} className="g-4">
              {tasks.map((task) => (
                <Col key={task.id}>
                  <Card className="h-100 shadow-sm">
                    <Card.Body className="d-flex flex-column">
                      <Card.Title>{task.title}</Card.Title>
                      <ListGroup variant="flush" className="mb-3">
                        <ListGroup.Item>
                          <strong>Status:</strong>{" "}
                          <Badge
                            bg={
                              task.status === "pending"
                                ? "warning"
                                : task.status === "completed"
                                ? "success"
                                : "info"
                            }
                          >
                            {task.status}
                          </Badge>
                        </ListGroup.Item>
                        <ListGroup.Item>
                          <strong>Priority:</strong> {task.priority}
                        </ListGroup.Item>
                        <ListGroup.Item>
                          <strong>Start Date:</strong>{" "}
                          {formatDate(task.start_date)}
                        </ListGroup.Item>
                        <ListGroup.Item>
                          <strong>Due Date:</strong> {formatDate(task.due_date)}
                        </ListGroup.Item>
                        <ListGroup.Item>
                          <strong>Description:</strong> {task.description}
                        </ListGroup.Item>
                      </ListGroup>

                      {/* Edit Task Button */}
                      {(userInfo?.role_id === 1 || userInfo?.role_id === 2) && (
                        <div className="mt-auto text-end">
                          <Button
                            variant="primary"
                            size="sm"
                            style={{
                              backgroundColor: "#0066FF",
                              borderColor: "#0066FF",
                            }}
                            onClick={() =>
                              navigate(`/task/${task.id}/edit`, {
                                state: { task, projectId: projectData.id },
                              })
                            }
                          >
                            Edit Task
                          </Button>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              ))}
            </Row>
          ) : (
            <Message>No tasks found for this project</Message>
          )}
        </div>
      ) : null}
    </div>
  );
}

export default ProjectScreen;
