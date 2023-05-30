function displayGymContactInfo(gymsInfo) {
    gymsInfo.forEach(gymInfo => {
        var html = `
            <div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative";> 
                <div class="col p-4 d-flex flex-column position-static" style="background-color: whitesmoke;">      
                    <a href="/show_gym_schedule_membership/${gymInfo.location}" aria-disabled="true">
                        <header>
                            <h2>${gymInfo.location}</h2>
                        </header>
                        <div class="content">
                            <p>${gymInfo.address}</p>
                            <p>${gymInfo.phone}</p>
                            <p>${gymInfo.hours}</p>
                        </div>
                    </a>
                </div>
            </div>
        `;
        document.getElementById("gym_info_row").innerHTML += html
    });
}

function loadGymContactInfo() {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var gymsInfo = JSON.parse(this.responseText);
            displayGymContactInfo(gymsInfo)
        }
    };
    xhr.open("GET", "/gym_info", true);
    xhr.send();
}


function displayGymMembershipAndScheduleInfo(gymInfo) {

    gymInfo.schedule.forEach(classInfo => {
        var html = `
            <div class="col-lg-6">
                <div class="row g-0 border rounded overflow-hidden flex-md-row mb-4 shadow-sm h-md-250 position-relative"; style="width:50%;left: 25%;top: 10%;">
                <div class="col p-4 d-flex flex-column position-static" style="background-color: whitesmoke;">
                    <strong class="d-inline-block mb-2 text-primary">Class: ${classInfo.class_name}</strong>
                    <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Hours:</strong> ${classInfo.class_timing}</div>
                    <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Days:</strong> ${classInfo.class_days}</div>
                    <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Group Size:</strong> ${classInfo.group_size}</div>
                    <div class="mb-1 text-muted"><strong class="d-inline-block mb-2 text-primary">Instructor:</strong> ${classInfo.instructor}</div>
                </div>
                <div></div>
                <div class="d-lg-block"></div>
                </div>
            </div>
        `;
        document.getElementById("gym-schedule-row").innerHTML += html
    })

}

function loadGymMembershipAndScheduleInfo(location) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            var gymInfo = JSON.parse(this.responseText);
            displayGymMembershipAndScheduleInfo(gymInfo)
        }
    };
    xhr.open("GET", "/gym_schedule/" + location, true);
    xhr.send();
}