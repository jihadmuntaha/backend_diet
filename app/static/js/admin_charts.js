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
  
  const ctx = document.getElementById('userReviewChart');
    if (ctx) {
        fetch('/api/user_reviews/stats')
            .then(res => res.json())
            .then(data => {
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: ['1★', '2★', '3★', '4★', '5★'],
                        datasets: [{
                            label: 'Jumlah Review',
                            data: [
                                data.distribution[1], 
                                data.distribution[2], 
                                data.distribution[3], 
                                data.distribution[4], 
                                data.distribution[5]
                            ],
                            backgroundColor: '#4e73df'
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: { y: { beginAtZero: true } }
                    }
                });
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
