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
  console.log(response.status);
  if (response.status === 204) {
    return { detail: "Successfully deleted.", success: true };
  } else {
    return { detail: "Something went wrong.", success: false };
  }
};
