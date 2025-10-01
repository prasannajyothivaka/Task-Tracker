import React, { useEffect, useState, useCallback } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";
import { Table, Button, Spinner, Alert, Badge, Form, ButtonGroup } from "react-bootstrap";
import {
  fetchTasks,
  updateTaskColumn,
  deleteTask,
} from "../features/taskSlice";
import { fetchUsers } from "../features/userSlice";
import { listProjectDetails } from "../features/projectSlice";
import Paginate from "../components/Paginate";
import DeleteConfirmModal from "../components/DeleteConfirmModal";

const TaskScreen = () => {
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  const { tasks, loading, error, page, pages } = useSelector(
    (state) => state.tasks
  );
  console.log("tasks:", tasks);
  const { userInfo } = useSelector((state) => state.userLogin);
  const { users, loading: usersLoading } = useSelector(
    (state) => state.getUsers
  );

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);

  // Extract query params from URL
  const searchParams = new URLSearchParams(location.search);
  const keyword = searchParams.get("keyword") || "";
  const pageNumber = parseInt(searchParams.get("page")) || 1;

  const canManageTasks = userInfo?.role_id === 1 || userInfo?.role_id === 2;
  const isNormalUser = userInfo?.role_id === 3;

  // Memoized function to refresh tasks
  const refreshTasks = useCallback(() => {
    if (userInfo) {
      dispatch(
        fetchTasks({ token: userInfo.token, keyword, page: pageNumber })
      );
    }
  }, [dispatch, userInfo, keyword, pageNumber]);

  // Fetch tasks whenever URL changes
  useEffect(() => {
    if (!userInfo) {
      navigate("/login");
    } else {
      refreshTasks();
      if (canManageTasks) {
        dispatch(fetchUsers(3));
      }
    }
  }, [
    dispatch,
    userInfo,
    keyword,
    pageNumber,
    navigate,
    canManageTasks,
    refreshTasks,
  ]);

  const handleStatusChange = async (task, newStatus) => {
    setIsUpdating(true);
    try {
      await dispatch(
        updateTaskColumn({
          taskId: task.id,
          column: "status",
          value: newStatus,
          token: userInfo.token,
        })
      ).unwrap();

      // Refresh tasks after successful update
      refreshTasks();
      dispatch(listProjectDetails(task.project_id));
    } catch (error) {
      console.error("Failed to update task status:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleAssignChange = async (task, newUserId) => {
    setIsUpdating(true);
    try {
      await dispatch(
        updateTaskColumn({
          taskId: task.id,
          column: "assigned_to",
          value: parseInt(newUserId, 10),
          token: userInfo.token,
        })
      ).unwrap();

      // Refresh tasks after successful update
      refreshTasks();
      dispatch(listProjectDetails(task.project_id));
    } catch (error) {
      console.error("Failed to update task assignment:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  // ------------------ DELETE MODAL HANDLERS ------------------
  const handleDeleteClick = (taskId) => {
    setSelectedTaskId(taskId);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setShowDeleteModal(false);
    setSelectedTaskId(null);
  };

  const handleConfirmDelete = async () => {
    if (selectedTaskId) {
      try {
        await dispatch(
          deleteTask({ taskId: selectedTaskId, token: userInfo.token })
        ).unwrap();

        // Refresh tasks after successful deletion
        refreshTasks();
      } catch (error) {
        console.error("Failed to delete task:", error);
      }
    }
    handleCloseDeleteModal();
  };
  // -----------------------------------------------------------

  return (
    <div className="p-4">
      <h2 className="mb-4 text-primary fw-bold">Task Management</h2>

      {loading && (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {isUpdating && (
        <Alert variant="info" className="d-flex align-items-center">
          <Spinner size="sm" className="me-2" />
          Updating task...
        </Alert>
      )}

      {tasks?.length > 0 ? (
        <>
          <Table
            bordered
            hover
            responsive
            className="align-middle shadow-sm text-center"
          >
            <thead className="table-primary">
              <tr>
                <th className="px-3 py-2">Title</th>
                <th className="px-3 py-2">Project</th>
                <th className="px-3 py-2">Priority</th>
                <th className="px-3 py-2">Status</th>
                <th className="px-3 py-2">Due Date</th>
                {canManageTasks && <th className="px-3 py-2">Assigned To</th>}
                {canManageTasks && <th className="px-3 py-2">Actions</th>}
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => {
                const assignedUser =
                  users.find((u) => u.id === task.username) || {};

                return (
                  <tr key={task.id}>
                    <td className="text-start fw-semibold px-3 py-2">
                      {task.title}
                    </td>
                    <td className="px-3 py-2">{task.project_name || "-"}</td>
                    <td className="px-3 py-2">
                      <Badge
                        bg={
                          task.priority === "high"
                            ? "danger"
                            : task.priority === "medium"
                            ? "warning"
                            : "success"
                        }
                      >
                        {task.priority || "-"}
                      </Badge>
                    </td>
                    <td className="px-3 py-2">
                      {isNormalUser ? (
                        <Form.Select
                          size="sm"
                          value={task.status || "pending"}
                          onChange={(e) =>
                            handleStatusChange(task, e.target.value)
                          }
                          disabled={isUpdating}
                          className="form-select-sm shadow-sm"
                        >
                          <option value="pending">Pending</option>
                          <option value="in-progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </Form.Select>
                      ) : (
                        <Badge
                          bg={
                            task.status === "completed"
                              ? "success"
                              : task.status === "pending"
                              ? "secondary"
                              : "info"
                          }
                        >
                          {task.status || "Pending"}
                        </Badge>
                      )}
                    </td>
                    <td className="px-3 py-2">
                      {task.due_date
                        ? new Date(task.due_date).toLocaleDateString()
                        : "-"}
                    </td>
                    {canManageTasks && (
                      <td className="px-3 py-2">
                        {usersLoading ? (
                          <Spinner size="sm" />
                        ) : (
                          <Form.Select
                            size="sm"
                            value={task.assigned_to || ""}
                            onChange={(e) =>
                              handleAssignChange(task, e.target.value)
                            }
                            disabled={isUpdating}
                            className="form-select-sm shadow-sm"
                            style={{ minWidth: "140px" }}
                          >
                            <option value="">-- Select User --</option>
                            {users.map((user) => (
                              <option key={user.id} value={user.id}>
                                {user.username}
                              </option>
                            ))}
                          </Form.Select>
                        )}
                      </td>
                    )}
                    {canManageTasks && (
                      <td className="px-3 py-2">
                        <ButtonGroup size="sm">
                          <Button
                            variant="outline-primary"
                            onClick={() =>
                              navigate(`/task/${task.id}/edit`, {
                                state: { task, projectId: task.project_id },
                              })
                            }
                            disabled={isUpdating}
                          >
                            <i className="fas fa-edit me-1"></i> Edit
                          </Button>
                          <Button
                            variant="outline-danger"
                            onClick={() => handleDeleteClick(task.id)}
                            disabled={isUpdating}
                          >
                            <i className="fas fa-trash me-1"></i> Delete
                          </Button>
                        </ButtonGroup>
                      </td>
                    )}
                  </tr>
                );
              })}
            </tbody>
          </Table>

          {pages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Paginate
                page={page}
                pages={pages}
                keyword={keyword}
                basePath="/tasks"
              />
            </div>
          )}

          <DeleteConfirmModal
            show={showDeleteModal}
            onClose={handleCloseDeleteModal}
            onConfirm={handleConfirmDelete}
          />
        </>
      ) : (
        !loading && <Alert variant="info">No tasks found.</Alert>
      )}
    </div>
  );
};

export default TaskScreen;