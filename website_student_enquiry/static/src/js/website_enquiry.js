$(document).ready(function () {

    var loc = window.location;
    var pathName = loc.pathname;
    if (pathName == '/enquiry')
    {
        $("#user_sign_in").hide();
    }
    else
    {
        $("#user_sign_in").show();
    }

    $("#select_country").change(function(){
        var con_id = $("#select_country").val();
        if (con_id != "")
        {
            jQuery.ajax({
            url 	: "/get_status_",
            type	: "POST",
            data 	: {country_id:con_id},
            dataType: 'json',
            success:function(data){
                if (data != "")
                {
                    var size = Object.keys(data).length
                    var des = $('select#select_state');
                    var options = "<option>"+"|-- Place of Birth --|"+"</option>";
                    for (i=0;i<size;i++)
                    {
                        options += "<option value='"+ data[i][0] +"'>"+data[i][1]+"</option>"
                    }
                    des.html( options );
                }
                else
                {
                    options = ''
                    var des = $('select#select_state');
                    options = "<option>"+"|-- Place of Birth --|"+"</option>"
                    des.html( options );
                }
            },
            error: function(){},
            });
        }

    });

    // Class filter
    $("#acdyear").change(function(){
        var acdyr_id = $("#acdyear").val();
        if (acdyr_id != "")
        {
            jQuery.ajax({
            url 	: "/get_class_",
            type	: "POST",
            data 	: {batch_rec:acdyr_id},
            dataType: 'json',
            success:function(data){
                if (data != "")
                {
                    var size = Object.keys(data).length
                    var des = $('select#gradeVal');
                    var options = "<option value=''>"+"|-- Grade for which admission sought --|"+"</option>";
                    for (i=0;i<size;i++)
                    {
                        options += "<option value='"+ data[i][0] +"'>"+data[i][1]+"</option>"
                    }
                    des.html( options );
                }
                else
                {
                    options = ''
                    var des = $('select#gradeVal');
                    options = "<option value=''>"+"|-- Grade for which admission sought --|"+"</option>"
                    des.html( options );
                }
            },
            error: function(){},
            });
        }
    });

    function validateDATE(ch_date)
    {
        var dob = ch_date
        var pattern = /^([0-9]{2})-([0-9]{2})-([0-9]{4})$/;
        if (!pattern.test(dob)) {
            return 0;
        }
        else {
            return 1
        }
    }

    function getAge(tyr,tmo,tday,bday,bmo,byr) {
//      var now = new Date();
//      var today = new Date(now.getYear(),now.getMonth(),now.getDate());
      var yearNow = tyr;
      var monthNow = tmo;
      var dateNow = tday;
     //date must be mm/dd/yyyy
//      var dob = new Date(dateString.substring(6,10),
//                         dateString.substring(0,2)-1,
//                         dateString.substring(3,5)
//                         );

      var yearDob = byr;
      var monthDob = bmo;
      var dateDob = bday;
      var age = {};
      var ageString = "";
      var yearString = "";
      var monthString = "";
      var dayString = "";


      yearAge = yearNow - yearDob;

      if (monthNow >= monthDob)
        var monthAge = monthNow - monthDob;
      else {
        yearAge--;
        var monthAge = 12 + monthNow -monthDob;
      }

      if (dateNow >= dateDob)
        var dateAge = dateNow - dateDob;
      else {
        monthAge--;
        var dateAge = 31 + dateNow - dateDob;

        if (monthAge < 0) {
          monthAge = 11;
          yearAge--;
        }
      }

      age = {
          years: yearAge,
          months: monthAge,
          days: dateAge
          };
      return age
    }

    // When click on Subbmit button then....
    $('#btnSubmit').click(function() {
        // When We click Submit button then this action perform
        var sEmail = document.getElementById("em").value;
        var filter = /^[\w\-\.\+]+\@[a-zA-Z0-9\.\-]+\.[a-zA-z0-9]{2,4}$/;
        var reEmail = document.getElementById("reem").value;
//	    var mob_check = /^\d{8,10}$/;
        var mob_check = /^([+0-9]{1,4})?([0-9]{8,10})$/;
        var mob = document.getElementById("mob").value;

        var effective_date = document.getElementById("effective_date").value;
        var year_id = $("#acdyear option:selected").val();

        if (year_id != ""){
            if (effective_date != ""){
            id_eff = effective_date.split(',');
                for (i = 0; i < id_eff.length; i++)
                {
                    if (year_id == id_eff[i])
                    {
                        id_eff_date = id_eff[i+1];
                    }
                }
            }
        }
        var course = $("#gradeVal option:selected").val();
        var course_id = $("#min_max").val();
        if (course != "") {
            course_min_max = course_id.split(',')
            for (i = 0; i < course_min_max.length; i+=2)
                {
                    if (course == parseInt(course_min_max[i]))
                    {
                     var min_age = parseInt(course_min_max[i+1].split('|')[0])
                     var max_age = parseInt(course_min_max[i+1].split('|')[1])
                    }
                }

            // Calculating Age form Date of Birth
            var date_of_birthday = document.getElementById("demo2").value;
            var dob_validation = validateDATE(date_of_birthday)
            if (dob_validation == 0)
                {
                    $("#demo2").css('border','1px solid #FF0000');
                    $("#msgage").show();
                    $("#demo2").focus();
                    $("#msgage").css('color','#FF0000');
                    $("#msgage").html("Please Enter Valid Date");
                    return false
                }
            else{
                    $("#demo2").css('border','1px solid #ccc');
                    $("#msgage").hide();
            }

            if (date_of_birthday != ""){
                //31-12-2015

                var bday = date_of_birthday.split("-")[0];
                var bmo = date_of_birthday.split("-")[1];
                var byr = date_of_birthday.split("-")[2];
                var age;
                if (id_eff_date != "")
                {
                //2015-07-01
                    tday=parseInt(id_eff_date.split('-')[2]);
                    tmo=parseInt(id_eff_date.split('-')[1]);
                    tyr=parseInt(id_eff_date.split('-')[0]);
                }

                dob = new Date(byr,bmo,bday);
                today = new Date(tyr,tmo,tday);
                var agge = getAge(tyr,tmo,tday,bday,bmo,byr)
                //(age >= min_age and age <= max_age):
                if (parseInt(agge.years) < parseInt(min_age) || parseInt(agge.years) > parseInt(max_age)) {
                        $("#gradeVal").css('border','1px solid #FF0000');
                        $("#demo2").css('border','1px solid #FF0000');
                        $("#msgage").show();
                        $("#demo2").focus();
                        $("#msgage").css('color','#FF0000');
                        $("#msgage").html("Sorry!! Student age must be in between "+min_age+" and "+max_age+" years!.");
                        return false;
                    }
                if ((parseInt(agge.years) == parseInt(max_age)) && (parseInt(agge.months) > 0 || parseInt(agge.days) > 0))
                    {
                            $("#gradeVal").css('border','1px solid #FF0000');
                            $("#demo2").css('border','1px solid #FF0000');
                            $("#msgage").show();
                            $("#msgage").css('color','#FF0000');
                            $("#msgage").html("Sorry!! Student age must be in between "+min_age+" and "+max_age+" years!.");
                            return false;
                    }
                else {

                        $("#demo2").css('border','1px solid #ccc')
                        $("#gradeVal").css('border','1px solid #ccc')
                        $("#msgage").hide();

                        // Mobile validation
                        if (mob_check.test(mob))
                        {
                                $("#mob").css('border','1px solid #ccc')
                                $("#msgmb").hide();
                        }
                        else
                        {
                            $("#mob").css('border','1px solid #FF0000')
                            $("#msgmb").css('color','#FF0000');
                            $("#mob").focus();
                            $("#isd_isd_err").hide();
                            $("#isd_code_code").css('border','1px solid #ccc');
                            $("#msgmb").show();
                            $("#msgmb").html("Please enter valid Contact Number");
                            return false;
                        }

                        // isd code validation
                        var isd_code_code = $("#isd_code_code").val();
                        var isd_code_filter = /^(\+|\d){1}\d{1,3}$/;
                        if (isd_code_code)
                        {
                            if (isd_code_filter.test(isd_code_code))
                            {
                                $("#isd_isd_err").hide();
                                $("#isd_code_code").css('border','1px solid #ccc');
                            }
                            else
                            {
                                $("#isd_code_code").css('border','1px solid #FF0000');
                                $("#isd_isd_err").show();
                                $("#isd_isd_err").css('color','#FF0000');
                                $("#msgmb").hide();
                                $("#mob").css('border','1px solid #ccc')
                                $("#isd_isd_err").html("please enter valid ISD code");
                                return false;
                            }
                        }

                        if (filter.test(sEmail)) {
                            if (sEmail == reEmail){
                                    $("#em").css('border','1px solid #ccc')
                                    $("#msgem").hide();
                                    p_issue_date = document.getElementById("demo1").value;
                                    p_expired_date = document.getElementById("demo3").value;
                                    var p_issue_date_chk = validateDATE(p_issue_date)
                                    if (p_issue_date != "" && p_issue_date_chk == 0)
                                        {
                                            $("#demo1").css('border','1px solid #FF0000');
                                            $("#iss_date_err").show();
                                            $("#demo1").focus();
                                            $("#iss_date_err").css('color','#FF0000');
                                            $("#iss_date_err").html("Please Enter Valid Date");
                                            return false
                                        }
                                    else{
                                            $("#demo1").css('border','1px solid #ccc');
                                            $("#iss_date_err").hide();
                                    }
                                    var p_expired_date_chk = validateDATE(p_expired_date)
                                    if (p_expired_date != "" && p_expired_date_chk == 0)
                                        {
                                            $("#demo3").css('border','1px solid #FF0000');
                                            $("#pass_date_err").show();
                                            $("#demo3").focus();
                                            $("#pass_date_err").css('color','#FF0000');
                                            $("#pass_date_err").html("Please Enter Valid Date");
                                            return false
                                        }
                                    else{
                                            $("#demo3").css('border','1px solid #ccc');
                                            $("#pass_date_err").hide();
                                    }
                                    //09-01-2015
                                    //Date(2010, 00, 15); Year, Month, Date
                                    if (p_issue_date != "" && p_expired_date != "")
                                    {
                                        date_of_issue1 = new Date(parseInt(p_issue_date.split('-')[2]),parseInt(p_issue_date.split('-')[1]),parseInt(p_issue_date.split('-')[0]))
                                        date_of_expired1 = new Date(parseInt(p_expired_date.split('-')[2]),parseInt(p_expired_date.split('-')[1]),parseInt(p_expired_date.split('-')[0]))
                                        if (date_of_expired1 < date_of_issue1)
                                        {
                                            $("#demo1").css('border','1px solid #FF0000')
                                            $("#demo3").css('border','1px solid #FF0000')
                                            $("#demo1").focus();
                                            $("#pass_date_err").css('color','#FF0000');
                                            $("#pass_date_err").html("Passport Expiry date should be after the Passport issue date !");
                                            $("#pass_date_err").show();
                                            $("#visa_date_err").hide();
                                            $("#demo4").css('border','1px solid #ccc')
                                            $("#demo5").css('border','1px solid #ccc')
                                            return false;
                                        }
                                        else
                                        {
                                            $("#pass_date_err").hide();
                                            $("#demo1").css('border','1px solid #ccc')
                                            $("#demo3").css('border','1px solid #ccc')
                                        }
                                    }
                                    v_issue_date = document.getElementById("demo4").value;
                                    v_expired_date = document.getElementById("demo5").value;
                                    l_attend_date = document.getElementById("demo6").value;
                                    /////////////////
                                    // Date validation
                                    var v_issue_date_chk = validateDATE(v_issue_date)
                                    if (v_issue_date != "" && v_issue_date_chk == 0)
                                        {
                                            $("#demo4").css('border','1px solid #FF0000');
                                            $("#visa_iss_date_err").show();
                                            $("#demo4").focus();
                                            $("#visa_iss_date_err").css('color','#FF0000');
                                            $("#visa_iss_date_err").html("Please Enter Valid Date");
                                            return false
                                        }
                                    else{
                                            $("#demo4").css('border','1px solid #ccc');
                                            $("#visa_iss_date_err").hide();
                                        }
                                    // Date validation
                                    var v_expired_date_chk = validateDATE(v_expired_date)
                                    if (v_expired_date != "" && v_expired_date_chk == 0)
                                        {
                                            $("#demo5").css('border','1px solid #FF0000');
                                            $("#visa_date_err").show();
                                            $("#demo5").focus();
                                            $("#visa_date_err").css('color','#FF0000');
                                            $("#visa_date_err").html("Please Enter Valid Date");
                                            return false
                                        }
                                    else{
                                            $("#demo5").css('border','1px solid #ccc');
                                            $("#visa_date_err").hide();
                                        }
                                    // Date validation
                                    var l_attend_date_chk = validateDATE(l_attend_date)
                                    if (l_attend_date != "" && l_attend_date_chk == 0)
                                        {
                                            $("#demo6").css('border','1px solid #FF0000');
                                            $("#l_attend_date_err").show();
                                            $("#demo6").focus();
                                            $("#l_attend_date_err").css('color','#FF0000');
                                            $("#l_attend_date_err").html("Please Enter Valid Date");
                                            return false
                                        }
                                    else{
                                            $("#demo6").css('border','1px solid #ccc');
                                            $("#l_attend_date_err").hide();
                                        }
                                    ////////////////
                                    if (v_issue_date != "" && v_expired_date != "")
                                    {
                                        date_of_issue2 = new Date(parseInt(v_issue_date.split('-')[2]),parseInt(v_issue_date.split('-')[1]),parseInt(v_issue_date.split('-')[0]))
                                        date_of_expired2 = new Date(parseInt(v_expired_date.split('-')[2]),parseInt(v_expired_date.split('-')[1]),parseInt(v_expired_date.split('-')[0]))
                                        if (date_of_expired2 < date_of_issue2)
                                        {
                                            $("#demo4").css('border','1px solid #FF0000')
                                            $("#demo5").css('border','1px solid #FF0000')
                                            $("#demo4").focus();
                                            $("#visa_date_err").css('color','#FF0000');
                                            $("#visa_date_err").html("Visa Expiry date should be after the visa issue date !");
                                            $("#pass_date_err").hide();
                                            $("#visa_date_err").show();
                                            $("#demo1").css('border','1px solid #ccc')
                                            $("#demo3").css('border','1px solid #ccc')
                                            return false;
                                        }
                                        else
                                        {
                                            $("#visa_date_err").hide();
                                            $("#demo4").css('border','1px solid #ccc')
                                            $("#demo5").css('border','1px solid #ccc')
                                        }
                                    }
                                }
                            else {
                                    $("#reem").css('border','1px solid #FF0000')
                                    $("#msgrem").css('color','#FF0000');
                                    $("#reem").focus();
                                    $("#msgrem").html("email id does not match. please enter valid email id");
                                    return false;
                                }
                        }
                        else {
                                $("#em").css('border','1px solid #FF0000')
                                $("#em").focus();
                                $("#msgem").css('color','#FF0000');
                                $("#msgem").html("please enter  valid email id");
                                return false;
                            }
                    }
                    }
        }
    });

    //button submit on student verification
    $('#btnsubmitinfo').click(function() {
        var sEmail = document.getElementById("s_em").value;
        var filter = /^[\w\-\.\+]+\@[a-zA-Z0-9\.\-]+\.[a-zA-z0-9]{2,4}$/;
        var reEmail = document.getElementById("s_reem").value;
        if (filter.test(sEmail)) {
            if (sEmail == reEmail){
                    $("#s_em").css('border','1px solid #ccc')
                    $("#s_msgem").hide();
                    return true;
                }
            else {
                    $("#s_reem").css('border','1px solid #FF0000')
                    $("#s_msgrem").css('color','#FF0000');
                    $("#s_msgrem").html("email id does not match. please enter valid email id");
                    return false;
                }
        }
        else {
                $("#s_em").css('border','1px solid #FF0000')
                $("#s_msgem").css('color','#FF0000');
                $("#s_msgem").html("please enter valid email id");
                return false;
            }
    });

    $('input:radio[name=under_medication]').change(function(){
        if ($(this).val() == 'n'){
            $("#mention_id").hide();
            $("#mention_id1").hide();
            $("#mention_text").attr( "required", false );
            $("#w_treatment_text").attr( "required", false );
        }
        else {
            $("#mention_id").show();
            $("#mention_id1").show();
            $("#mention_text").attr( "required", true );
            $("#w_treatment_text").attr( "required", true );
        }
    });
    $('input:radio[name=allergic]').change(function(){
        if ($(this).val() == 'n'){
            $("#yes_allergic_id").hide();
            $("#yes_allergic_id1").hide();
            $("#yes_allergic_id2").hide();
            $("#yes_allergic_text").attr( "required", false );
            $("#yes_allergic_text1").attr( "required", false );
            $("#yes_allergic_text2").attr( "required", false );
        }
        else {
            $("#yes_allergic_id").show();
            $("#yes_allergic_id1").show();
            $("#yes_allergic_id2").show();
            $("#yes_allergic_text").attr( "required", true );
            $("#yes_allergic_text1").attr( "required", true );
            $("#yes_allergic_text2").attr( "required", true );
        }
    });

    $('#stud_other_submit').click(function(){
        var m_email = $("#mother_email").val();
        var p_email = $("#email_parent").val();
        var filter = /^[\w\-\.\+]+\@[a-zA-Z0-9\.\-]+\.[a-zA-z0-9]{2,4}$/;
        var mother_mobile = $("#reg_mother_mobile_no").val();
        var father_mobile = $("#reg_father_mobile").val();
        var isd_code = $("#reg_isd_code").val();
//        var mobile_filter = /^\d{8,10}$/;
        var mobile_filter = /^([+0-9]{1,4})?([0-9]{8,10})$/;
        var isd_code_filter = /^(\+|\d){1}\d{1,3}$/;
        // mother email address validation
	if (m_email)
	{
            if (filter.test(m_email))
            {
                $("#m_em_er").hide();
                $("#mother_email").css('border','1px solid #ccc');
                if (filter.test(p_email))
                {
                    $("#p_em_er").hide();
                    $("#email_parent").css('border','1px solid #ccc');
                    return true
                }
                else
                {
                    $("#email_parent").css('border','1px solid #FF0000');
                    $("#p_em_er").show();
                    $("#p_em_er").css('color','#FF0000');
                    $("#p_em_er").html("please enter valid email id");
                }
            }
            else
            {
                $("#mother_email").css('border','1px solid #FF0000');
                $("#m_em_er").show();
                $("#m_em_er").css('color','#FF0000');
                $("#m_em_er").html("please enter valid email id");
                return false;
            }
	}

        // isd code validation
        if (isd_code)
        {
            if (isd_code_filter.test(isd_code))
            {
                $("#f_isd_err").hide();
                $("#reg_isd_code").css('border','1px solid #ccc');
            }
            else
            {
                $("#reg_isd_code").css('border','1px solid #FF0000');
                $("#f_isd_err").show();
                $("#f_isd_err").css('color','#FF0000');
                $("#f_isd_err").html("please enter valid ISD code");
                return false;
            }
        }
        else
        {
                $("#reg_isd_code").css('border','1px solid #FF0000');
                $("#f_isd_err").show();
                $("#f_isd_err").css('color','#FF0000');
                $("#f_isd_err").html("please enter valid ISD code");
                return false;
        }

        // father mobile number validation
        if (father_mobile)
        {
            if (mobile_filter.test(father_mobile))
            {
                $("#f_mob_err").hide();
                $("#reg_father_mobile").css('border','1px solid #ccc');
            }
            else
            {
                $("#reg_father_mobile").css('border','1px solid #FF0000');
                $("#f_mob_err").show();
                $("#f_mob_err").css('color','#FF0000');
                $("#f_mob_err").html("please enter valid mobile number");
                return false;
            }
        }
        else
        {
                $("#reg_father_mobile").css('border','1px solid #FF0000');
                $("#f_mob_err").show();
                $("#f_mob_err").css('color','#FF0000');
                $("#f_mob_err").html("please enter valid mobile number");
                return false;
        }

        //mother mobile number validation
        if (mother_mobile)
        {
            if (mobile_filter.test(mother_mobile))
            {
                $("#mother_mob_err").hide();
                $("#reg_mother_mobile_no").css('border','1px solid #ccc');
            }
            else
            {
                $("#reg_mother_mobile_no").css('border','1px solid #FF0000');
                $("#mother_mob_err").show();
                $("#mother_mob_err").css('color','#FF0000');
                $("#mother_mob_err").html("please enter valid mobile number");
                return false;
            }
        }
        else
        {
            $("#reg_mother_mobile_no").css('border','1px solid #FF0000');
            $("#mother_mob_err").show();
            $("#mother_mob_err").css('color','#FF0000');
            $("#mother_mob_err").html("please enter valid mobile number");
            return false;
        }

    });

    $('#transport_type').change(function(){
    var transport_type = $('#transport_type').val();
    console.log("-->",transport_type)
    if (transport_type != ''){
        if (transport_type == 'own'){
            $("#pick_up").attr( "required", false );
            $('#droup_off').attr( "required", false );
            $('#off_droup').hide();
            $('#up_pick').hide();
            $('#pick_up_hide').hide();
            $('#drop_off_points_hide').hide();

        }
        else{
            $('#pick_up_hide').show();
            $('#drop_off_points_hide').show();
            $('#pick_up').attr( "required", true );
            $('#droup_off').attr( "required", true );
            $('#off_droup').show();
            $('#up_pick').show();
        }
    }
    });

    $('#transport_type').change(function(){
        var transport_type = $('#transport_type').val();
        console.log("-->",transport_type)
        if (transport_type != ''){
            if (transport_type == 'own'){
                $("#pick_up").attr( "required", false );
                $('#droup_off').attr( "required", false );
                $('#off_droup').hide();
                $('#up_pick').hide();
                $('#pick_up_hide').hide();
                $('#drop_off_points_hide').hide();
            }
            else{
                $('#pick_up_hide').show();
                $('#drop_off_points_hide').show();
                $('#pick_up').attr( "required", true );
                $('#droup_off').attr( "required", true );
                $('#off_droup').show();
                $('#up_pick').show();

            }
        }
    });

});
