$(document).ready(function () {
    //get student value
    var dateofbirth = document.getElementById("J_Date_of_Birth").innerHTML;
    document.getElementById("demo2").value = dateofbirth.split("-")[1]+'-'+dateofbirth.split("-")[2]+"-"+dateofbirth.split("-")[0];
    var dateofpass = document.getElementById("J_Date_of_pass").innerHTML;
    document.getElementById("demo1").value = dateofpass.split("-")[1]+'-'+dateofpass.split("-")[2]+"-"+dateofpass.split("-")[0];
    var dateofxpass = document.getElementById("J_Date_ex_pass").innerHTML;
    document.getElementById("demo3").value = dateofxpass.split("-")[1]+'-'+dateofxpass.split("-")[2]+"-"+dateofxpass.split("-")[0];
    var dateofvisa = document.getElementById("J_Date_visa").innerHTML;
    document.getElementById("demo4").value = dateofvisa.split("-")[1]+'-'+dateofvisa.split("-")[2]+"-"+dateofvisa.split("-")[0];
    var dateofexvisa = document.getElementById("J_Date_ex_visa").innerHTML;
    document.getElementById("demo5").value = dateofexvisa.split("-")[1]+'-'+dateofexvisa.split("-")[2]+"-"+dateofexvisa.split("-")[0];
    var dateofatt = document.getElementById("J_Date_att").innerHTML;
    document.getElementById("demo6").value = dateofatt.split("-")[1]+'-'+dateofatt.split("-")[2]+"-"+dateofatt.split("-")[0];
    var redio_about = document.getElementById("radio_about_us").innerHTML;
    var redio_gender = document.getElementById("rec_gender").innerHTML;
    //check for about us
    if (redio_about == 'fb'){
        $('#rad_fb').attr('checked', true);
    }
    else if (redio_about == 'np'){
        $('#rad_np').attr('checked', true);
    }
    else if (redio_about == 'google'){
        $('#rad_google').attr('checked', true);
    }
    else if (redio_about == 'friend'){
        $('#rad_friend').attr('checked', true);
    }
    else if (redio_about == 'sms_camp'){
        $('#rad_sms_camp').attr('checked', true);
    }
    else if (redio_about == 'visitnearbyarea'){
        $('#rad_visitnearbyarea').attr('checked', true);
    }
    else if (redio_about == 'marketing_leaflet'){
        $('#rad_marketing_leaflet').attr('checked', true);
    }
    else if (other == 'other'){
        $('#rad_other').attr('checked', true);
    }
    //check for gender
    if (redio_gender == 'f'){
        $('#f_gender').attr('checked', true);
    }
    else if (redio_gender == 'm'){
        $('#m_gender').attr('checked', true);
    }
});