const handleSearch = (searchBoxId, path) => {
  const searchBox = document.getElementById(searchBoxId);
  window.location.href = `/dashboard/${path}?q=${searchBox.value}`;
};
const handleSearchBoxClear = (path) => {
  window.location.href = `/dashboard/${path}`;
};
const previousPage = (path, pages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const currentPage = Number(urlParams.get("page"));
  const q = urlParams.get("q");
  const previous = currentPage
    ? currentPage === 1
      ? pages
      : Number(pages) - 1
    : pages;
  window.location.href = q
    ? `/dashboard/${path}?q=${q}&page=${previous}`
    : `/dashboard/${path}?page=${previous}`;
};
const nextPage = (path, pages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const currentPage = Number(urlParams.get("page"));
  const q = urlParams.get("q");
  const next = currentPage
    ? currentPage === Number(pages)
      ? 1
      : currentPage + 1
    : 1 === Number(pages)
    ? 1
    : 2;
  window.location.href = q
    ? `/dashboard/${path}?q=${q}&page=${next}`
    : `/dashboard/${path}?page=${next}`;
};

const customPage = (path, pageNumber) => {
  const urlParams = new URLSearchParams(window.location.search);
  const q = urlParams.get("q");
  window.location.href = q
    ? `/dashboard/${path}?q=${q}&page=${pageNumber}`
    : `/dashboard/${path}?page=${pageNumber}`;
};
