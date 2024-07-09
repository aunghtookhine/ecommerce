const handleSearch = (searchBoxId, path) => {
  const searchBox = document.getElementById(searchBoxId);
  window.location.href = `/dashboard/${path}?q=${searchBox.value}`;
};
const handleSearchBoxClear = (path) => {
  window.location.href = `/dashboard/${path}`;
};
const previousPage = (path, pages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const page = Number(urlParams.get("page"));
  const previous = page ? (page === 1 ? pages : pages - 1) : pages;
  window.location.href = `/dashboard/${path}?page=${previous}`;
};
const nextPage = (path, pages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const page = Number(urlParams.get("page"));
  const next = page ? (page === Number(pages) ? 1 : page + 1) : 2;
  window.location.href = `/dashboard/${path}?page=${next}`;
};
