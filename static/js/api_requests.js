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

const patchMethod = async (resource, payload, token) => {
  const response = await fetch(resource, {
    method: "PATCH",
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
  const toast = $("#toast");
  const toastBody = $("#toast-body");
  toastBody.html(detail);
  if (success) {
    toast.addClass(["text-bg-success", "show"]);
    !url ? window.location.reload() : (window.location.href = url);
  } else {
    toast.addClass(["text-bg-danger", "show"]);
    setTimeout(() => {
      toast.removeClass(["show", "text-bg-danger"]);
    }, 3000);
  }
};
