var chart1 = null
var chart2 = null

function displayUserActivityTable(userActivities) {
  console.log(userActivities)
  document.getElementById("table-body").innerHTML = ""
  userActivities.forEach(activity => {
    var html = `
      <tr>
        <td> ${getFormattedDate(activity.date_column)} </td>
        <td> ${activity.equipment_name} </td>
        <td> ${activity.Location} </td>
        <td> ${activity.num_of_minutes} </td>
      </tr>
    `;
    document.getElementById("table-body").innerHTML += html
  });
}

function getFormattedDate(dateString) {
  if (!dateString) {
    return ""
  }
  var date = new Date(dateString);
  var formattedDate = date.toLocaleDateString("en-US", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric"
  });
  return formattedDate
}

function displayActivityChart(userActivities, chartId) {   
  var keys = Object.keys(userActivities);
  var values = Object.values(userActivities);
  
  document.getElementById(chartId)
  var canvas = document.getElementById(chartId);
  canvas.width = 70; // new width
  canvas.height = 70; // new height
  var ctx = document.getElementById(chartId).getContext('2d');

  var chart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: keys,
    datasets: [{
      label: 'Minutes',
      data: values,
      backgroundColor: 'rgba(0, 255, 0, 0.2)',
      borderColor: 'rgba(0, 255, 0, 1)',
      borderWidth: 1
    }]
  },
  options: {
    title: {
      display: true,
      text: 'Workout : Number of Minutes',
      fontColor: 'Black',
      fontSize: 20,
    },
    layout: {
      padding: {
        left: 10
      }
    },
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true,
          fontColor: 'white'
        },
        gridLines: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }],
      xAxes: [{
        ticks: {
          fontColor: 'white'
        },
        gridLines: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }]
    },
    legend: {
      labels: {
        fontColor: 'white'
      }
    }
  }
});

  if (chartId == "myChart1") {
    chart1 = chart
  } else {
    chart2 = chart
  }

}

function displayPerDayChart(userActivities) {
  var dateDict = {};

  userActivities.forEach(activity => {
    var date = getFormattedDate(activity.date_column)
    var minutes = activity.num_of_minutes
    if (date in dateDict) {
      dateDict[date] += minutes;
    } else {
      dateDict[date] = minutes;
    }
  })

  if (chart1) {
    chart1.destroy()
  }
  displayActivityChart(userActivities=dateDict, chartId="myChart1")
}

function displayPerEquipmentChart(userActivities) {
  var equipmentDict = {};

  userActivities.forEach(activity => {
    var equipment = activity.equipment_name
    var minutes = activity.num_of_minutes
    if (equipment in equipmentDict) {
      equipmentDict[equipment] += minutes;
    } else {
      equipmentDict[equipment] = minutes;
    }
  })

  if (chart2) {
    chart2.destroy()
  }
  displayActivityChart(userActivities=equipmentDict, chartId="myChart2")
}

function loadUserActivity(timeperiod) {
  if (timeperiod == "") {
    timeperiod = "all"
  }

  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var userActivity = JSON.parse(this.responseText);
      displayUserActivityTable(userActivity)
      displayPerDayChart(userActivity)
      displayPerEquipmentChart(userActivity)
    }
  };
  xhr.open("GET", "/userActivity/" + timeperiod, true);
  xhr.send();
}


function displayWorkoutSummary(workoutSummary) {
  document.getElementById("workoutSummaryTotal").innerHTML = workoutSummary.all
  document.getElementById("workoutSummary90d").innerHTML = workoutSummary["90days"]
  document.getElementById("workoutSummary1m").innerHTML = workoutSummary.pastmonth
  document.getElementById("workoutSummary1w").innerHTML = workoutSummary.pastweek
}

function loadUserActivitySummary() {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      var workoutSummary = JSON.parse(this.responseText);
      displayWorkoutSummary(workoutSummary)
      loadUserActivity("all")
    }
  };
  xhr.open("GET", "/workoutSummary", true);
  xhr.send();
}

function loadAllUserActivities() {
  loadUserActivitySummary()
}
