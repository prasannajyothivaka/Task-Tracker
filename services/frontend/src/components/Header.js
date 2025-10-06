import { useDispatch, useSelector } from "react-redux";
import Container from "react-bootstrap/Container";
import SearchBox from "./SearchBox";
import Nav from "react-bootstrap/Nav";
import Navbar from "react-bootstrap/Navbar";
import { LinkContainer } from "react-router-bootstrap";
import { NavDropdown } from "react-bootstrap";
import { useNavigate, useLocation } from "react-router-dom";
import { resetAll } from "../features/authSlice";

function Header() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const userLogin = useSelector((state) => state.userLogin);
  const { userInfo } = userLogin || {}; // safeguard against undefined

  const logoutHandler = () => {
    localStorage.removeItem("userInfo"); // remove token
    dispatch(resetAll()); // reset redux state
    navigate("/login"); // redirect to login page
  };

  const hideSearchRoutes = [
    "/project/create",
    "/task/create",
    "/admin/userlist",
  ];

  // check edit routes dynamically
  const isEditRoute =
    location.pathname.includes("/project/") ||
    (location.pathname.includes("/project/") &&
      location.pathname.includes("/edit")) ||
    (location.pathname.includes("/task/") &&
      location.pathname.includes("/edit"));

  const hideSearch =
    hideSearchRoutes.includes(location.pathname) || isEditRoute;

  return (
    <header>
      <Navbar
        expand="lg"
        variant="dark"
        className="custom-navbar"
        collapseOnSelect
        fixed="top"
      >
        <Container>
          <LinkContainer to="/">
            <Navbar.Brand>Task Tracker</Navbar.Brand>
          </LinkContainer>
          <Navbar.Toggle aria-controls="basic-navbar-nav" />
          <Navbar.Collapse
            id="basic-navbar-nav"
            className="justify-content-between"
          >
            {/* Left side: tasks */}
            <Nav className="d-flex align-items-center">
              <LinkContainer to="/tasks">
                <Nav.Link>
                  <i className="fas fa-tasks"></i> Tasks
                </Nav.Link>
              </LinkContainer>
            </Nav>

            <div className="d-flex align-items-center">
              {!hideSearch && <SearchBox />}
              <Nav className="ms-3">
                {userInfo ? (
                  <NavDropdown
                    title={userInfo.name || userInfo.username}
                    id="username"
                  >
                    {/* Only show Users link if role_id is 1 */}
                    {userInfo.role_id === 1 && (
                      <LinkContainer to="/admin/userlist">
                        <NavDropdown.Item>Users</NavDropdown.Item>
                      </LinkContainer>
                    )}

                    {/* Logout always visible */}
                    <NavDropdown.Item onClick={logoutHandler}>
                      Logout
                    </NavDropdown.Item>
                  </NavDropdown>
                ) : (
                  <LinkContainer to="/login">
                    <Nav.Link>
                      <i className="fas fa-user"></i> Login
                    </Nav.Link>
                  </LinkContainer>
                )}
              </Nav>
            </div>
          </Navbar.Collapse>
        </Container>
      </Navbar>
    </header>
  );
}

export default Header;
