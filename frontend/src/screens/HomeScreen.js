import React, { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";
import { Button, Spinner } from "react-bootstrap";

import Project from "../components/Project";
import Message from "../components/Message";
import Paginate from "../components/Paginate";
import { listProjects } from "../features/projectSlice";

function HomeScreen() {
  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  // Extract query params
  const searchParams = new URLSearchParams(location.search);
  const keyword = searchParams.get("keyword") || "";
  const pageNumber = searchParams.get("page") || 1;
  console.log("keyword:", keyword);

  // Redux state from slice
  const { projects, loading, error, page, pages } = useSelector(
    (state) => state.projects
  );

  const { userInfo } = useSelector((state) => state.userLogin) || {};

  // Fetch projects
  useEffect(() => {
    if (!userInfo) {
      navigate("/login");
    } else {
      dispatch(listProjects({ keyword, page: pageNumber }));
    }
  }, [dispatch, keyword, pageNumber, userInfo, navigate]);

  return (
    <div className="container mt-4">
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h2 className="mb-4 fw-bold text-primary">Projects</h2>
        {userInfo?.role_id === 1 && (
          <Button
            variant="primary"
            size="sm"
            style={{ backgroundColor: "#0066FF", borderColor: "#0066FF" }}
            onClick={() => navigate(`/project/create`)}
          >
            + Create Project
          </Button>
        )}
      </div>

      {loading ? (
        <div className="d-flex justify-content-center my-5">
          <Spinner animation="border" />
        </div>
      ) : error ? (
        <Message variant="danger">{error}</Message>
      ) : projects && projects.length > 0 ? (
        <>
          <div className="list-group shadow-sm rounded">
            {projects.map((project) => (
              <Project key={project.id} project={project} />
            ))}
          </div>

          {pages > 1 && (
            <div className="d-flex justify-content-center mt-4">
              <Paginate
                page={page}
                pages={pages}
                keyword={keyword}
                basePath="/"
              />
            </div>
          )}
        </>
      ) : (
        <Message variant="info">No projects found.</Message>
      )}
    </div>
  );
}

export default HomeScreen;
