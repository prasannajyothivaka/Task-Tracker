import React, { useState, useEffect } from "react";
import { Link, useParams, useLocation, useNavigate } from "react-router-dom";
import { Form, Button, Spinner } from "react-bootstrap";
import { useDispatch, useSelector } from "react-redux";
import Message from "../components/Message";
import { getUserById, updateUser } from "../features/authSlice";
import FormContainer from "../components/FormContainer";

function UserEditScreen() {
  const { userId } = useParams();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);

  const dispatch = useDispatch();
  const location = useLocation();
  const navigate = useNavigate();

  const userDetails = useSelector((state) => state.userDetails);
  const { error, loading, user } = userDetails;

  const userUpdate = useSelector((state) => state.userUpdate);
  const {
    error: errorUpdate,
    loading: loadingUpdate,
    success: successUpdate,
  } = userUpdate;

  useEffect(() => {
    if (successUpdate) {
      navigate(`/admin/userlist`);
    } else {
      if (!user || user._id !== Number(userId)) {
        dispatch(getUserById(userId));
      } else {
        setName(user.name || "");
        setEmail(user.email || "");
        setIsAdmin(user.isAdmin || false);
      }
    }
  }, [user, userId, successUpdate, navigate]);

  const submitHandler = (e) => {
    e.preventDefault();
    dispatch(updateUser({ _id: user._id, name, email, isAdmin }));
  };

  return (
    <div>
      <Link to="/admin/userlist">Go Back</Link>
      <FormContainer>
        <h1>Edit User</h1>
        {loadingUpdate && (
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" />
          </div>
        )}
        {errorUpdate && <Message variant="danger">{errorUpdate}</Message>}

        {loading ? (
          <div className="d-flex justify-content-center my-5">
            <Spinner animation="border" />
          </div>
        ) : error ? (
          <Message variant="danger">{error}</Message>
        ) : (
          <Form onSubmit={submitHandler}>
            <Form.Group controlId="name">
              <Form.Label>Name</Form.Label>
              <Form.Control
                type="name"
                placeholder="Enter Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              ></Form.Control>
            </Form.Group>

            <Form.Group controlId="email">
              <Form.Label>Email Address</Form.Label>
              <Form.Control
                type="email"
                placeholder="Enter Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              ></Form.Control>
            </Form.Group>

            <Form.Group controlId="isAdmin">
              <Form.Check
                type="checkbox"
                label="Is Admin"
                checked={isAdmin}
                onChange={(e) => setIsAdmin(e.target.checked)}
              ></Form.Check>
            </Form.Group>

            <Button type="submit" variant="primary">
              Update
            </Button>
          </Form>
        )}
      </FormContainer>
    </div>
  );
}

export default UserEditScreen;
