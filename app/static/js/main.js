// document.addEventListener("DOMContentLoaded", function () {
//   // Dipakai di user_detail.html dan diet_history.html

//   if (typeof postureTrend !== "undefined") {
//     const wtCtx = document.getElementById("weightTrend");
//     if (wtCtx) {
//       new Chart(wtCtx, {
//         type: "line",
//         data: {
//           labels: postureTrend.dates,
//           datasets: [{
//             label: "Weight (kg)",
//             data: postureTrend.weights
//           }]
//         }
//       });
//     }

//     const bmiCtx = document.getElementById("bmiTrend");
//     if (bmiCtx) {
//       new Chart(bmiCtx, {
//         type: "line",
//         data: {
//           labels: postureTrend.dates,
//           datasets: [{
//             label: "BMI",
//             data: postureTrend.bmis
//           }]
//         }
//       });
//     }

//     const psCtx = document.getElementById("postureScoreTrend");
//     if (psCtx) {
//       new Chart(psCtx, {
//         type: "line",
//         data: {
//           labels: postureTrend.dates,
//           datasets: [{
//             label: "Posture Score",
//             data: postureTrend.posture_scores
//           }]
//         }
//       });
//     }
//   }

//   if (typeof calorieTrend !== "undefined") {
//     const calCtx = document.getElementById("calorieTrend");
//     if (calCtx) {
//       new Chart(calCtx, {
//         type: "line",
//         data: {
//           labels: calorieTrend.dates,
//           datasets: [
//             {
//               label: "Intake",
//               data: calorieTrend.intake
//             },
//             {
//               label: "Target",
//               data: calorieTrend.targets
//             }
//           ]
//         }
//       });
//     }
//   }
// });

// ===================== POSTURE DISTRIBUTION PIE =====================
const pieCtx = document.getElementById("posturePie");

if (pieCtx && typeof postureDistribution !== "undefined") {
  new Chart(pieCtx, {
    type: "pie",
    data: {
      labels: Object.keys(postureDistribution),
      datasets: [{
        data: Object.values(postureDistribution)
      }]
    }
  });
}

// ===================== NEW USERS LINE =====================
const newUsersCtx = document.getElementById("newUsersChart");

if (newUsersCtx && typeof newUsersData !== "undefined") {
  new Chart(newUsersCtx, {
    type: "line",
    data: {
      labels: newUsersData.map(d => d.week),
      datasets: [{
        label: "New Users",
        data: newUsersData.map(d => d.count),
        tension: 0.4
      }]
    }
  });
}

// ===================== POSTURE SCORE LINE =====================
const postureScoreCtx = document.getElementById("postureScoreChart");

if (postureScoreCtx && typeof postureScoreTrend !== "undefined") {
  new Chart(postureScoreCtx, {
    type: "line",
    data: {
      labels: postureScoreTrend.map(d => d.date),
      datasets: [{
        label: "Posture Score",
        data: postureScoreTrend.map(d => d.score),
        tension: 0.4
      }]
    }
  });
}
