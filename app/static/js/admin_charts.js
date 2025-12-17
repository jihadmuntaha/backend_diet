document.addEventListener("DOMContentLoaded", function () {
  const postureCtx = document.getElementById("posturePie");
  if (postureCtx) {
    new Chart(postureCtx, {
      type: "pie",
      data: {
        labels: postureLabels,
        datasets: [{
          data: postureValues
        }]
      }
    });
  }

  const newUsersCtx = document.getElementById("newUsersLine");
  if (newUsersCtx) {
    new Chart(newUsersCtx, {
      type: "line",
      data: {
        labels: newUsers.labels,
        datasets: [{
          label: "New Users",
          data: newUsers.counts
        }]
      }
    });
  }

  const postureScoreCtx = document.getElementById("postureScoreLine");
  if (postureScoreCtx) {
    new Chart(postureScoreCtx, {
      type: "line",
      data: {
        labels: postureScores.labels,
        datasets: [{
          label: "Avg Posture Score",
          data: postureScores.scores
        }]
      }
    });
  }
});
