import { Container, Row, Col } from "react-bootstrap";

function Footer() {
  return (
    <footer
      className="text-light py-3 fixed-bottom"
      style={{ backgroundColor: "#6c757d" }}
    >
      <Container>
        <Row className="align-items-center">
          <Col md={6} className="text-center text-md-start">
            <small>&copy; 2025 TaskTracker. All rights reserved.</small>
          </Col>
          <Col md={6} className="text-center text-md-end">
            <small>
              <span className="me-3">📊 Stay Organized</span>
              <span className="me-3">✅ Get Things Done</span>
              <span>🚀 Boost Productivity</span>
            </small>
          </Col>
        </Row>
      </Container>
    </footer>
  );
}

export default Footer;
