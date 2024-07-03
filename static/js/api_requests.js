const postMethod = async (resource, payload, token) => {
  const response = await fetch(resource, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  return data;
};

const putMethod = async (resource, payload, token) => {
  const response = await fetch(resource, {
    method: "PUT",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  return data;
};

const deleteMethod = async (resource, token) => {
  const response = await fetch(resource, {
    method: "DELETE",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  if (response.status === 204) {
    return { detail: "Successfully Deleted.", success: true };
  } else {
    return { detail: "Something Went Wrong.", success: false };
  }
};

const showToast = (detail, success, url = null) => {
  const toast = document.getElementById("toast");
  const toastBody = document.getElementById("toast-body");
  toastBody.innerHTML = detail;
  if (success) {
    toast.classList.add("text-bg-success", "show");
    !url ? window.location.reload() : (window.location.href = url);
  } else {
    toast.classList.add("text-bg-danger", "show");
    setTimeout(() => {
      toast.classList.remove("show", "text-bg-danger");
    }, 3000);
  }
};
