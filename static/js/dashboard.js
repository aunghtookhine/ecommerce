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
  const previous = currentPage
    ? currentPage === 1
      ? pages
      : Number(pages) - 1
    : pages;
  window.location.href = `/dashboard/${path}?page=${previous}`;
};
const nextPage = (path, pages) => {
  const urlParams = new URLSearchParams(window.location.search);
  const currentPage = Number(urlParams.get("page"));
  const next = currentPage
    ? currentPage === Number(pages)
      ? 1
      : currentPage + 1
    : 1 === Number(pages)
    ? 1
    : 2;
  console.log(next);
  window.location.href = `/dashboard/${path}?page=${next}`;
};
