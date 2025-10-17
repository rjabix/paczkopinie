function deleteReview(reviewId) {
  fetch("/delete-review", {
    method: "DELETE",
    body: JSON.stringify({ reviewId: reviewId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}
