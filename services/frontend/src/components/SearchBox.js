import React, { useState } from "react";
import { Button, Form } from "react-bootstrap";
import { useLocation, useNavigate } from "react-router-dom";

function SearchBox() {
  const [keyword, setKeyword] = useState("");
  const location = useLocation();
  const navigate = useNavigate();

  const submitHandler = (e) => {
    e.preventDefault();
    const path = location.pathname; // current screen path, e.g., /tasks
    if (keyword) {
      navigate(`${path}?keyword=${keyword}&page=1`);
    } else {
      navigate(path);
    }
  };

  const getPlaceholder = () => {
    if (location.pathname === "/") {
      return "Search Projects...";
    } else if (location.pathname === "/tasks") {
      return "Search Tasks...";
    }
    return "Search...";
  };

  return (
    <Form onSubmit={submitHandler} className="d-flex search-box">
      <Form.Control
        type="text"
        name="q"
        onChange={(e) => setKeyword(e.target.value)}
        className="me-2"
        placeholder={getPlaceholder()}
      />
      <Button type="submit" variant="light" className="search-btn">
        Search
      </Button>
    </Form>
  );
}

export default SearchBox;
