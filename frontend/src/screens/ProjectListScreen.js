import React, { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { LinkContainer } from "react-router-bootstrap";
import { Table, Button, Row, Col, Spinner } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import Message from "../components/Message";
import Paginate from "../components/Paginate";
import { Modal } from "antd";
import {
  listProjects,
  deleteProject,
  createProject,
} from "../features/projectSlice";

function ProjectListScreen() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { ProjectId } = useParams();

  const projectList = useSelector((state) => state.projectList);
  const { loading, error, projects, pages, page } = projectList;

  const projectDelete = useSelector((state) => state.projectDelete);
  const {
    loading: loadingDelete,
    error: errorDelete,
    success: successDelete,
  } = projectDelete;

  const projectCreate = useSelector((state) => state.projectCreate);
  console.log("projectCreate:", projectCreate);
  const {
    loading: loadingCreate,
    error: errorCreate,
    success: successCreate,
    project: createdProject,
  } = projectCreate;

  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin;

  useEffect(() => {
    if (!userInfo.isAdmin) {
      navigate("/login");
    }
    if (successCreate) {
      navigate(`/admin/project/${createdProject._id}/edit`);
    } else {
      dispatch(listProjects());
    }
  }, [
    dispatch,
    navigate,
    userInfo,
    successDelete,
    successCreate,
    createProject,
  ]);

  const deleteHandler = (ProjectId) => {
    Modal.confirm({
      title: "Are you sure you want to delete this project?",
      content: "This action cannot be undone.",
      okText: "Yes, Delete",
      okType: "danger",
      cancelText: "Cancel",
      onOk() {
        dispatch(deleteProject(ProjectId));
      },
    });
  };

  const createProjectHandler = () => {
    dispatch(createProject());
  };

  return (
    <div>
      <Row className="align-items-center">
        <Col>
          <h1>Projects</h1>
        </Col>
        <Col className="text-right">
          <Button className="my-3" onClick={createProjectHandler}>
            <i className="fas fa-plus"></i> Create Project
          </Button>
        </Col>
      </Row>
      {loadingDelete && (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      )}
      {errorDelete && <Message variant="danger">{errorDelete}</Message>}

      {loadingCreate && (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      )}
      {errorCreate && <Message variant="danger">{errorCreate}</Message>}

      {loading ? (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      ) : error ? (
        <Message variant="danger">{error}</Message>
      ) : (
        <div>
          <Table striped bordered hover responsive className="table-sm">
            <thead>
              <tr>
                <th>ID</th>
                <th>NAME</th>
                <th>PRICE</th>
                <th>CATEGORY</th>
                <th>BRAND</th>
                <th></th>
              </tr>
            </thead>

            <tbody>
              {projects.map((project) => (
                <tr key={project._id}>
                  <td>{project._id}</td>
                  <td>{project.name}</td>
                  <td>${project.price}</td>
                  <td>{project.category}</td>
                  <td>{project.brand}</td>

                  <td>
                    <LinkContainer to={`/admin/project/${project._id}/edit`}>
                      <Button variant="light" className="btn-sm">
                        <i className="fas fa-edit"></i>
                      </Button>
                    </LinkContainer>
                    <Button
                      variant="danger"
                      className="btn-sm"
                      onClick={() => deleteHandler(project._id)}
                    >
                      <i className="fas fa-trash"></i>
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
          <Paginate pages={pages} page={page} isAdmin={true} />
        </div>
      )}
    </div>
  );
}

export default ProjectListScreen;
