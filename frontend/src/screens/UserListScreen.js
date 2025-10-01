import React, { useEffect, useState } from "react";
import {
  Table,
  Button,
  Spinner,
  Alert,
  Modal,
  Form,
  OverlayTrigger,
  Tooltip,
} from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import {
  listUsers,
  deleteUser,
  updateUserRole,
  logout,
} from "../features/authSlice";

const UserListScreen = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const { userInfo, loading, error } =
    useSelector((state) => state.userLogin) || {};
  const { users: usersResponse } =
    useSelector((state) => state.userLogin) || {};

  const users = usersResponse?.data || {};

  // Delete modal states
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState(null);

  // Role update modal states
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [newRoleId, setNewRoleId] = useState(null);
  const [isUpdatingRole, setIsUpdatingRole] = useState(false);

  // Role mapping
  const roleMapping = {
    1: "Admin",
    2: "Task Creator",
    3: "User",
  };

  useEffect(() => {
    if (userInfo && userInfo.role_id === 1) {
      dispatch(listUsers());
    } else {
      navigate("/login");
    }
  }, [dispatch, navigate, userInfo]);

  // Delete handlers
  const handleDeleteClick = (userId) => {
    setSelectedUserId(userId);
    setShowDeleteModal(true);
  };

  const handleCloseDeleteModal = () => {
    setSelectedUserId(null);
    setShowDeleteModal(false);
  };

  const handleConfirmDelete = () => {
    if (selectedUserId) {
      dispatch(deleteUser(selectedUserId))
        .unwrap()
        .then(() => {
          if (selectedUserId === userInfo?.id) {
            dispatch(logout());
            navigate("/login");
          } else {
            dispatch(listUsers());
          }
          handleCloseDeleteModal();
        })
        .catch(() => {
          handleCloseDeleteModal();
        });
    }
  };

  // Role update handlers
  const handleRoleChange = (user, newRoleValue) => {
    const newRole = parseInt(newRoleValue);

    if (newRole === user.role_id) {
      return;
    }

    setSelectedUser(user);
    setNewRoleId(newRole);
    setShowRoleModal(true);
  };

  const handleCloseRoleModal = () => {
    setShowRoleModal(false);
    setSelectedUser(null);
    setNewRoleId(null);
  };

  const handleConfirmRoleUpdate = async () => {
    if (selectedUser && newRoleId) {
      setIsUpdatingRole(true);

      try {
        await dispatch(
          updateUserRole({
            user_id: selectedUser.id,
            role_id: newRoleId,
          })
        ).unwrap();

        if (selectedUser.id === userInfo?.id && newRoleId === 3) {
          dispatch(logout());
          navigate("/login");
        } else {
          await dispatch(listUsers());
        }

        handleCloseRoleModal();
      } catch (error) {
        console.error("Failed to update user role:", error);
      } finally {
        setIsUpdatingRole(false);
      }
    }
  };

  // ---- UI Rendering for tables ----
  const renderUserTable = (roleName, userList) => (
    <div className="mb-5">
      <h4 className="mb-3 text-secondary fw-bold">{roleName}</h4>
      {userList?.length > 0 ? (
        <Table bordered hover responsive className="align-middle shadow-sm">
          <thead className="table-primary">
            <tr>
              <th className="px-3 py-2">Name</th>
              <th className="px-3 py-2">Email</th>
              <th className="px-3 py-2">Role</th>
              <th className="px-3 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            {userList.map((user) => {
              const isCurrentUser = user.id === userInfo?.user_id;

              return (
                <tr key={user.id}>
                  <td className="text-start fw-semibold px-3 py-2">
                    {user.username}
                  </td>
                  <td className="px-3 py-2">{user.email}</td>
                  <td className="px-3 py-2">
                    <OverlayTrigger
                      placement="top"
                      overlay={
                        isCurrentUser ? (
                          <Tooltip
                            id={`tooltip-role-${user.id}`}
                            className="custom-tooltip"
                          >
                            You cannot change your own role
                          </Tooltip>
                        ) : (
                          <></>
                        )
                      }
                    >
                      <div>
                        <Form.Select
                          size="sm"
                          value={user.role_id}
                          onChange={(e) =>
                            handleRoleChange(user, e.target.value)
                          }
                          disabled={loading || isUpdatingRole || isCurrentUser}
                          style={{
                            minWidth: "140px",
                            opacity: isCurrentUser ? 0.6 : 1,
                            cursor: isCurrentUser ? "not-allowed" : "pointer",
                          }}
                        >
                          <option value={1}>Admin</option>
                          <option value={2}>Task Creator</option>
                          <option value={3}>User</option>
                        </Form.Select>
                      </div>
                    </OverlayTrigger>
                  </td>
                  <td className="px-3 py-2">
                    <OverlayTrigger
                      placement="top"
                      overlay={
                        isCurrentUser ? (
                          <Tooltip
                            id={`tooltip-delete-${user.id}`}
                            className="custom-tooltip"
                          >
                            You cannot delete yourself
                          </Tooltip>
                        ) : (
                          <></>
                        )
                      }
                    >
                      <div>
                        <Button
                          variant="outline-danger"
                          size="sm"
                          onClick={() => handleDeleteClick(user.id)}
                          disabled={loading || isUpdatingRole || isCurrentUser}
                          style={{
                            opacity: isCurrentUser ? 0.6 : 1,
                            cursor: isCurrentUser ? "not-allowed" : "pointer",
                          }}
                        >
                          <i className="fas fa-trash me-1"></i> Delete
                        </Button>
                      </div>
                    </OverlayTrigger>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </Table>
      ) : (
        <Alert variant="info">No users available in {roleName}.</Alert>
      )}
    </div>
  );

  const roleOrder = ["Admin", "Task Creator", "User"];

  return (
    <div className="p-4">
      <h2 className="mb-4 text-primary fw-bold">User Management</h2>

      {loading && (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {isUpdatingRole && (
        <Alert variant="info" className="d-flex align-items-center">
          <Spinner size="sm" className="me-2" />
          Updating user role...
        </Alert>
      )}

      {!loading &&
        users &&
        roleOrder.map((role) =>
          renderUserTable(role, users[role.replace(" ", "")] || [])
        )}

      {/* Delete Confirmation Modal */}
      <Modal show={showDeleteModal} onHide={handleCloseDeleteModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Delete</Modal.Title>
        </Modal.Header>
        <Modal.Body>Are you sure you want to delete this user?</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseDeleteModal}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleConfirmDelete}>
            Delete
          </Button>
        </Modal.Footer>
      </Modal>

      {/* Role Update Confirmation Modal */}
      <Modal show={showRoleModal} onHide={handleCloseRoleModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Confirm Role Update</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedUser && newRoleId && (
            <div>
              <p>Are you sure you want to update the role of:</p>
              <div className="bg-light p-3 rounded mb-3">
                <strong>{selectedUser.username}</strong> ({selectedUser.email})
              </div>
              <p>
                From:{" "}
                <span className="badge bg-secondary">
                  {roleMapping[selectedUser.role_id]}
                </span>
                {" → "}
                To:{" "}
                <span className="badge bg-primary">
                  {roleMapping[newRoleId]}
                </span>
              </p>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button
            variant="secondary"
            onClick={handleCloseRoleModal}
            disabled={isUpdatingRole}
          >
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleConfirmRoleUpdate}
            disabled={isUpdatingRole}
          >
            {isUpdatingRole ? (
              <>
                <Spinner size="sm" className="me-2" />
                Updating...
              </>
            ) : (
              "Yes, Update Role"
            )}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default UserListScreen;
