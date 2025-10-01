import React from "react";
import { Pagination } from "react-bootstrap";
import { Link } from "react-router-dom";

function Paginate({ pages, page, keyword = "", basePath = "/" }) {
  if (pages <= 1) return null;

  const pageLinks = [];
  const maxShown = 5; // show at most 5 numbers at once

  let startPage = Math.max(1, page - 2);
  let endPage = Math.min(pages, page + 2);

  if (page <= 3) {
    endPage = Math.min(pages, maxShown);
  } else if (page >= pages - 2) {
    startPage = Math.max(1, pages - (maxShown - 1));
  }

  const link = (p) => `${basePath}?keyword=${keyword}&page=${p}`;

  // Prev button
  pageLinks.push(
    <Pagination.Prev key="prev" disabled={page === 1} as={Link} to={link(page - 1)} />
  );

  // First page + ellipsis
  if (startPage > 1) {
    pageLinks.push(
      <Pagination.Item key={1} as={Link} to={link(1)}>
        1
      </Pagination.Item>
    );
    if (startPage > 2) pageLinks.push(<Pagination.Ellipsis key="start-ellipsis" />);
  }

  // Middle range
  for (let i = startPage; i <= endPage; i++) {
    pageLinks.push(
      <Pagination.Item key={i} active={i === page} as={Link} to={link(i)}>
        {i}
      </Pagination.Item>
    );
  }

  // Last page + ellipsis
  if (endPage < pages) {
    if (endPage < pages - 1) pageLinks.push(<Pagination.Ellipsis key="end-ellipsis" />);
    pageLinks.push(
      <Pagination.Item key={pages} as={Link} to={link(pages)}>
        {pages}
      </Pagination.Item>
    );
  }

  // Next button
  pageLinks.push(
    <Pagination.Next key="next" disabled={page === pages} as={Link} to={link(page + 1)} />
  );

  return <Pagination>{pageLinks}</Pagination>;
}

export default Paginate;
