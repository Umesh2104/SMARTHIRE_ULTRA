// Auto-hide alerts
document.addEventListener("DOMContentLoaded", function () {
  setTimeout(function () {
    document.querySelectorAll(".alert").forEach(function (alert) {
      alert.classList.add("fade");
      setTimeout(() => alert.remove(), 300);
    });
  }, 5000);
});

// Confirm delete actions
document.querySelectorAll(".delete-confirm").forEach(function (btn) {
  btn.addEventListener("click", function (e) {
    if (!confirm("Are you sure?")) e.preventDefault();
  });
});
