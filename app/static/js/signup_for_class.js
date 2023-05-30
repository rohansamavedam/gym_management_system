function displayGymMembershipAndScheduleInfo(gymInfo, location) {
  gymInfo.schedule.forEach(classInfo => {
    var html = `
      <div class="col-lg-6">
        <div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative"; style="width:50%;left: 25%;top: 10%;">
          <div class="col p-4 d-flex flex-column position-static" style="background-color: whitesmoke;">
            <strong class="d-inline-block mb-2 text-primary">Class: ${classInfo.class_name}</strong>
            <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Hours:</strong> ${classInfo.class_timing}</div>
            <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Days:</strong> ${classInfo.class_days} </div>
            <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Group Size:</strong> ${classInfo.group_size} </div>
            <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Instructor:</strong> ${classInfo.instructor} </div>
    `;

    if (classInfo.no_enrolled < classInfo.group_size) {
      if (classInfo.is_enrolled == false) {
        html += `
          <a href="/enrollInClass/${location}/${classInfo.class_name}" class="mb-1 text-muted" role="button" aria-disabled="true">enroll</a>
        `;
      } else {
        html += `
        <a href="/unenrollClass/${location}/${classInfo.class_name}" class="mb-1 text-muted" role="button" aria-disabled="true">unenroll</a>
        `;
      }
    }

    html += `
          </div>
        </div>
      </div> 
    `;
    document.getElementById("gym-enroll-schedule-row").innerHTML += html
  })
}

function loadGymEnrollmentScheduleInfo(location) {
  var xhr = new XMLHttpRequest();
  xhr.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          var gymInfo = JSON.parse(this.responseText);
          displayGymMembershipAndScheduleInfo(gymInfo, location)
      }
  };
  xhr.open("GET", "/gym_enrollment_schedule/" + location, true);
  xhr.send();
}