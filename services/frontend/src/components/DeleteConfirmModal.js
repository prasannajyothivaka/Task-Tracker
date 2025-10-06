// components/DeleteConfirmModal.js
import React from "react";
import { Modal, Button } from "react-bootstrap";

const DeleteConfirmModal = ({ show, onClose, onConfirm }) => {
  return (
    <Modal show={show} onHide={onClose} centered>
      <Modal.Header closeButton className="bg-danger text-white">
        <Modal.Title>Delete Task</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p className="text-muted mb-0">
          Are you sure you want to delete this task? This action cannot be
          undone.
        </p>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" className="btn-cancel" onClick={onClose}>
          Cancel
        </Button>
        <Button
          variant="danger"
          className="btn-confirm-delete"
          onClick={onConfirm}
        >
          Delete
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeleteConfirmModal;
