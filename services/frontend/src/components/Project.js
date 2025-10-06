import React from "react";
import { Badge } from "react-bootstrap";
import { Link } from "react-router-dom";

function Project({ project }) {
  return (
    <div className="border rounded p-3 mb-3 shadow-sm bg-white d-flex flex-column flex-md-row justify-content-between align-items-start">
      {/* Left side: Project details */}
      <div>
        <Link
          to={`/project/${project.id}`}
          className="text-decoration-none text-dark"
        >
          <h5 className="mb-1 fw-semibold">{project.name}</h5>
        </Link>
        <p className="text-muted small mb-1">
          {project.description || "No description available"}
        </p>
        <p className="small text-secondary mb-0">
          {project.start_date} → {project.end_date}
        </p>
      </div>

      {/* Right side: Status & Dates */}
      <div className="text-md-end mt-3 mt-md-0">
        <Badge
          bg={project.status === "active" ? "success" : "secondary"}
          className="px-3 py-2 text-capitalize"
        >
          {project.status}
        </Badge>
        <div className="small text-muted mt-2">
          <div>
            Created: {new Date(project.created_on).toLocaleDateString()}
          </div>
          <div>
            Updated: {new Date(project.updated_on).toLocaleDateString()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Project;
