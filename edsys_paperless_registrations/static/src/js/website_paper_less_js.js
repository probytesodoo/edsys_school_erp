$(document).ready(function() {

    // Email validation
    function email_checked(get_email){
        var filter_email = /^[\w\-\.\+]+\@[a-zA-Z0-9\.\-]+\.[a-zA-z0-9]{2,4}$/;
        if(filter_email.test(get_email)){
            return 1
        }
        else{
            return 0
        }
    }

    //Mobile Validation
    function mobile_checked(get_mobile){
//        var filter_mobile = /^\d{8,10}$/;
//        var filter_mobile = /(^[+0-9]{1,3})*([0-9]{8,10}$)/;
        var filter_mobile = /^([+0-9]{1,4})?([0-9]{8,10})$/;
        if(filter_mobile.test(get_mobile)){
            return 1
        }
        else{
            return 0
        }
    }

    // ---- Default Page ----
    $('#submit_default_page').click(function(){
        // Parent Email validation
        var P_Email = $("#email_parent").val();
        var get_P_Email_result = email_checked(P_Email)
        if(get_P_Email_result == 1)
            {
                $("#p_em_er").hide();
                $("#email_parent").css('border','1px solid #ccc');
            }
        else
            {
                $("#email_parent").css('border','1px solid #FF0000');
                $("#p_em_er").show();
                $("#p_em_er").css('color','#FF0000');
                $("#p_em_er").html("please enter valid email id");
                return false
            }

        // Mobile ISD validation
        var isd_code = $("#reg_isd_code").val();
        var isd_code_filter = /^(\+|\d){1}\d{1,3}$/;
        if (isd_code)
        {
            if (isd_code_filter.test(isd_code))
            {
                $("#f_isd_err").hide();
                $("#reg_isd_code").css('border','1px solid #ccc');
            }
            else
            {
                $("#reg_isd_code").focus();
                $("#reg_isd_code").css('border','1px solid #FF0000');
                $("#f_isd_err").show();
                $("#f_isd_err").css('color','#FF0000');
                $("#f_isd_err").html("please enter valid ISD code");
                return false;
            }
        }

        // Mobile validation
        var father_mobile = $("#reg_father_mobile").val();
        var mobile_filter = /^\d{8,10}$/;
        if (mobile_filter.test(father_mobile))
            {
                $("#f_mob_err").hide();
                $("#reg_father_mobile").css('border','1px solid #ccc');
            }
        else
            {
                $("#reg_father_mobile").css('border','1px solid #FF0000');
                $("#reg_father_mobile").focus();
                $("#f_mob_err").show();
                $("#f_mob_err").css('color','#FF0000');
                $("#f_mob_err").html("please enter valid mobile number");
                return false;
            }

        // mother mobile validation
        var mother_mobile = $("#reg_mother_mobile_no").val();
        if (mother_mobile)
            {
                var get_mother_mobile_retsult = mobile_checked(mother_mobile)

                if (get_mother_mobile_retsult == 1)
                {
                    $("#mother_mob_err").hide();
                    $("#reg_mother_mobile_no").css('border','1px solid #ccc');
                }
                else
                {
                    $("#reg_mother_mobile_no").focus();
                    $("#reg_mother_mobile_no").css('border','1px solid #FF0000');
                    $("#mother_mob_err").show();
                    $("#mother_mob_err").css('color','#FF0000');
                    $("#mother_mob_err").html("please enter valid mobile number");
                    return false;
                }
            }

        // Mother Email Validation
        var m_email = $("#mother_email").val();
        var get_m_email_result = email_checked(m_email)
        if(get_m_email_result == 1)
            {
                $("#m_em_er").hide();
                $("#mother_email").css('border','1px solid #ccc');
            }
        else
            {
                $("#mother_email").focus();
                $("#mother_email").css('border','1px solid #FF0000');
                $("#m_em_er").show();
                $("#m_em_er").css('color','#FF0000');
                $("#m_em_er").html("please enter valid email id");
                return false;
            }

        // Emergency Contact Validation
        var emergency_contact = $("#id_emergency_contact").val();
        if (emergency_contact)
            {
                var get_emergency_contact_retsult = mobile_checked(emergency_contact)

                if (get_emergency_contact_retsult == 1)
                {
                    $("#emergency_contact_err").hide();
                    $("#id_emergency_contact").css('border','1px solid #ccc');
                }
                else
                {
                    $("#id_emergency_contact").focus();
                    $("#id_emergency_contact").css('border','1px solid #FF0000');
                    $("#emergency_contact_err").show();
                    $("#emergency_contact_err").css('color','#FF0000');
                    $("#emergency_contact_err").html("please enter valid mobile number");
                    return false;
                }
            }
    });

    // ---- Page 1 ----
    // passport date error show
    function passport_date_err_show() {
        $('#date3').css('border','1px solid #FF0000')
        $('#date4').css('border','1px solid #FF0000')
        $('#date3').focus();
        $('#pass_date_err').show();
        $('#pass_date_err').css('color','#FF0000');
        $('#pass_date_err').html("Passport Expiry date should be after the Passport issue date !");
    }
    // passport date error hide
    function passport_date_err_hide() {
        $('#date3').css('border','1px solid #ccc')
        $('#date4').css('border','1px solid #ccc')
        $('#pass_date_err').hide();
    }
    // visa date error show
    function visa_date_err_show() {
        $('#date5').css('border','1px solid #FF0000')
        $('#date6').css('border','1px solid #FF0000')
        $('#date5').focus();
        $('#visa_date_err').show();
        $('#visa_date_err').css('color','#FF0000');
        $('#visa_date_err').html("Visa Expiry date should be after the Visa issue date !");
    }
    // visa date error hide
    function visa_date_err_hide() {
        $('#date5').css('border','1px solid #ccc')
        $('#date6').css('border','1px solid #ccc')
        $('#visa_date_err').hide();
    }
    //Subbmit Button click event
    $('#SubmitPaper1').click(function(){
        // set language spoken at home.
        var id_Lang_Spoken_Home = $('#id_Lang_Spoken_Home').val();
        $('#id_Lang_Spoken_Home_value').val(id_Lang_Spoken_Home);

        // Passport Date Validation [ 2012-05-23 ]
        var p_issue_date = $('#date3').val();
        var p_expiry_date = $('#date4').val();
        passport_issue_date = new Date(parseInt(p_issue_date.split('-')[0]),parseInt(p_issue_date.split('-')[1]),parseInt(p_issue_date.split('-')[2]))
        passport_expiry_date = new Date(parseInt(p_expiry_date.split('-')[0]),parseInt(p_expiry_date.split('-')[1]),parseInt(p_expiry_date.split('-')[2]))
        if (passport_expiry_date < passport_issue_date)
            {
                passport_date_err_show()
                return false
            }
            else
            {
                passport_date_err_hide()
            }

        // Visa Date Validation [ 2012-05-23 ]
        var v_issue_date = $('#date5').val();
        var v_expiry_date = $('#date6').val();
        visa_issue_date = new Date(parseInt(v_issue_date.split('-')[0]),parseInt(v_issue_date.split('-')[1]),parseInt(v_issue_date.split('-')[2]))
        visa_expiry_date = new Date(parseInt(v_expiry_date.split('-')[0]),parseInt(v_expiry_date.split('-')[1]),parseInt(v_expiry_date.split('-')[2]))
        console.log('visa_issue_date'+visa_issue_date)
        console.log('v_expiry_date'+visa_expiry_date)
        if (visa_expiry_date < visa_issue_date)
            {
                visa_date_err_show()
                return false
            }
            else
            {
                visa_date_err_hide()
            }

        // Email Address Validation
        var sEmail = document.getElementById("s_email").value;
        var get_sEmail_result = email_checked(sEmail)
        if(get_sEmail_result == 1)
            {
                $("#s_email").css('border','1px solid #ccc');
                $("#blockemail").hide();
            }
        else
            {
                $("#blockemail").show();
                $("#s_email").css('border','1px solid #FF0000');
                $("#s_email").focus();
                $("#blockemail").html("please enter valid email id");
                $("#blockemail").css('color','#FF0000');
                $("#s_mobile").css('border','1px solid #ccc');
                $("#blockmobile").hide();
                return false
            }
        // Mobile Number Validation
        var s_mobile = document.getElementById("s_mobile").value;
        var get_s_mobile_retsult = mobile_checked(s_mobile)
        if (get_s_mobile_retsult == 1)
            {
                $("#s_mobile").css('border','1px solid #ccc');
                $("#blockmobile").hide();
            }
        else
            {
                $("#blockmobile").show();
                $("#s_mobile").css('border','1px solid #FF0000');
                $("#s_mobile").focus();
                $("#blockmobile").html("Please Enter Valid Mobile Number !");
                $("#blockmobile").css('color','#FF0000');
                return false
            }
    });

    // ---- Page 2 ----
    //Subbmit Button click event
    $('#SubmitPaper2').click(function(){
        // Page 2 Father Mobile number Validation
        var f_mobile = document.getElementById("father_mobile").value;
        var get_f_mobile_retsult = mobile_checked(f_mobile)
        if (get_f_mobile_retsult == 1)
            {
                $("#father_mobile").css('border','1px solid #ccc');
                $("#father_mobile_block").hide();
            }
        else{
                $("#father_mobile_block").show();
                $("#father_mobile").css('border','1px solid #FF0000');
                $("#father_mobile").focus();
                $("#father_mobile_block").html("Please Enter Valid Mobile Number !");
                $("#father_mobile_block").css('color','#FF0000');
                return false
            }

        // Page 2 Father Email Validation
        var fEmail = document.getElementById("father_email").value;
        var get_fEmail_result = email_checked(fEmail)
        if(get_fEmail_result == 1)
            {
                $("#father_email").css('border','1px solid #ccc');
                $("#father_email_block").hide();
            }
        else{
                $("#father_email_block").show();
                $("#father_email").css('border','1px solid #FF0000');
                $("#father_email").focus();
                $("#father_email_block").html("please enter valid email id");
                $("#father_email_block").css('color','#FF0000');
                $("#father_mobile").css('border','1px solid #ccc');
                $("#father_mobile_block").hide();
                return false
            }

        // Page 2 Mother Mobile number Validation
        var m_mobile = document.getElementById("mother_mobile").value;
        var get_m_mobile_retsult = mobile_checked(m_mobile)
        if (get_m_mobile_retsult == 1)
            {
                $("#mother_mobile").css('border','1px solid #ccc');
                $("#mother_mobile_block").hide();
            }
        else{
                $("#mother_mobile_block").show();
                $("#mother_mobile").css('border','1px solid #FF0000');
                $("#mother_mobile").focus();
                $("#mother_mobile_block").html("Please Enter Valid Mobile Number !");
                $("#mother_mobile_block").css('color','#FF0000');
                return false
            }

        // Page 2 Mother Email Validation
        var mEmail = document.getElementById("mother_email").value;
        var get_mEmail_result = email_checked(mEmail)
        if(get_mEmail_result == 1)
            {
                $("#mother_email").css('border','1px solid #ccc');
                $("#mother_email_block").hide();
            }
        else{
                $("#mother_email_block").show();
                $("#mother_email").css('border','1px solid #FF0000');
                $("#mother_email").focus();
                $("#mother_email_block").html("please enter valid email id");
                $("#mother_email_block").css('color','#FF0000');
                $("#mother_mobile").css('border','1px solid #ccc');
                $("#mother_mobile_block").hide();
                return false
            }
    });

    // page 2 Special Contribution
    var Special_Contribution = $('#id_Special_Contribution');
    Special_Contribution.change(function(){
        if ($(this).val() != 'any_other'){
            $("#Input_Special_Contribution").attr( "required", false );
            $("#Row_Special_Contribution").hide();
        }
        else {
            $("#Row_Special_Contribution").show();
            $("#Input_Special_Contribution").attr( "required", true );
        }
    });

    // ---- Page 3 ----
    // Page 3 Child_Received_Academic_Distinction
    var Child_Received_Academic_Distinction = $('input:radio[name=Child_Received_Academic_Distinction]');
//    if (Child_Received_Academic_Distinction.val() == 'yes'){
//        $("#Row_Child_Received_Academic_Distinction").show();
//        $("#Input_Child_Received_Academic_Distinction").attr( "required", true );
//    }
//    else{
//        $("#Input_Child_Received_Academic_Distinction").attr( "required", false );
//        $("div[id=Row_Child_Received_Academic_Distinction]").hide();
//    }
    Child_Received_Academic_Distinction.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Child_Received_Academic_Distinction").attr( "required", false );
            $("div[id=Row_Child_Received_Academic_Distinction]").hide();
        }
        else {
            $("div[id=Row_Child_Received_Academic_Distinction]").show();
            $("#Input_Child_Received_Academic_Distinction").attr( "required", true );
        }
    });

    // Page 3 Has_Suspended_Expelled_by_School
    var Has_Suspended_Expelled_by_School = $('input:radio[name=Has_Suspended_Expelled_by_School]');
//    if (Has_Suspended_Expelled_by_School.val() == 'yes'){
//        $("div[id=Row_Has_Suspended_Expelled_by_School]").show();
//        $("#Input_Has_Suspended_Expelled_by_School").attr( "required", true );
//    }
//    else{
//        $("#Input_Has_Suspended_Expelled_by_School").attr( "required", false );
//        $("#Row_Has_Suspended_Expelled_by_School").hide();
//    }
    Has_Suspended_Expelled_by_School.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Suspended_Expelled_by_School").attr( "required", false );
            $("#Row_Has_Suspended_Expelled_by_School").hide();
        }
        else {
            $("#Row_Has_Suspended_Expelled_by_School").show();
            $("#Input_Has_Suspended_Expelled_by_School").attr( "required", true );
        }
    });

    // Page 3 Child_Associated_with_Awareness
    var Child_Associated_with_Awareness = $('input:radio[name=Child_Associated_with_Awareness]');
//    if (Child_Associated_with_Awareness.val() == 'yes'){
//        $("div[id=Row_Child_Associated_with_Awareness]").show();
//        $("#Input_Child_Associated_with_Awareness").attr( "required", true );
//    }
//    else{
//        $("#Input_Child_Associated_with_Awareness").attr( "required", false );
//        $("#Row_Child_Associated_with_Awareness").hide();
//    }
    Child_Associated_with_Awareness.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Child_Associated_with_Awareness").attr( "required", false );
            $("#Row_Child_Associated_with_Awareness").hide();
        }
        else {
            $("#Row_Child_Associated_with_Awareness").show();
            $("#Input_Child_Associated_with_Awareness").attr( "required", true );
        }
    });

    // Page 3 Member_of_Environment_Protection
    var Member_of_Environment_Protection = $('input:radio[name=Member_of_Environment_Protection]');
//    if (Member_of_Environment_Protection.val() == 'yes'){
//        $("div[id=Row_Member_of_Environment_Protection]").show();
//        $("#Input_Member_of_Environment_Protection").attr( "required", true );
//    }
//    else{
//        $("#Input_Member_of_Environment_Protection").attr( "required", false );
//        $("#Row_Member_of_Environment_Protection").hide();
//    }
    Member_of_Environment_Protection.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Member_of_Environment_Protection").attr( "required", false );
            $("#Row_Member_of_Environment_Protection").hide();
        }
        else {
            $("#Row_Member_of_Environment_Protection").show();
            $("#Input_Member_of_Environment_Protection").attr( "required", true );
        }
    });

    // Page 3 Leadership_Positions_in_School
    var Leadership_Positions_in_School = $('input:radio[name=Leadership_Positions_in_School]');
//    if (Leadership_Positions_in_School.val() == 'yes'){
//        $("div[id=Row_Leadership_Positions_in_School]").show();
//        $("#Input_Leadership_Positions_in_School").attr( "required", true );
//    }
//    else{
//        $("#Input_Leadership_Positions_in_School").attr( "required", false );
//        $("#Row_Leadership_Positions_in_School").hide();
//    }
    Leadership_Positions_in_School.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Leadership_Positions_in_School").attr( "required", false );
            $("#Row_Leadership_Positions_in_School").hide();
        }
        else {
            $("#Row_Leadership_Positions_in_School").show();
            $("#Input_Leadership_Positions_in_School").attr( "required", true );
        }
    });

    // Page 3 Special_Education_Programme
    var Special_Education_Programme = $('input:radio[name=Special_Education_Programme]');
//    if (Special_Education_Programme.val() == 'yes'){
//        $("div[id=Row_Special_Education_Programme]").show();
//        $("#Input_Special_Education_Programme").attr( "required", true );
//    }
//    else{
//        $("#Input_Special_Education_Programme").attr( "required", false );
//        $("#Row_Special_Education_Programme").hide();
//    }
    Special_Education_Programme.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Special_Education_Programme").attr( "required", false );
            $("#Row_Special_Education_Programme").hide();
        }
        else {
            $("#Row_Special_Education_Programme").show();
            $("#Input_Special_Education_Programme").attr( "required", true );
        }
    });

    // Page 3 Special_Learning_Disability
    var Special_Learning_Disability = $('input:radio[name=Special_Learning_Disability]');
//    if (Special_Learning_Disability.val() == 'yes'){
//        $("#Row_Special_Learning_Disability").show();
//        $("#Input_Special_Learning_Disability").attr( "required", true );
//    }
    $('input:radio[name=Special_Learning_Disability]').change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Special_Learning_Disability").attr( "required", false );
            $("#Row_Special_Learning_Disability").hide();
        }
        else {
            $("#Row_Special_Learning_Disability").show();
            $("#Input_Special_Learning_Disability").attr( "required", true );
        }
    });

    // Page 3 Has_Other_than_English_Languages
    var Has_Other_than_English_Languages = $('input:radio[name=Has_Other_than_English_Languages]');
//    if (Has_Other_than_English_Languages.val() == 'yes'){
//        $("#Row_Has_Other_than_English_Languages").show();
//        $("#Input_Has_Other_than_English_Languages").attr( "required", true );
//    }
    Has_Other_than_English_Languages.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Other_than_English_Languages").attr( "required", false );
            $("#Row_Has_Other_than_English_Languages").hide();
        }
        else {
            $("#Row_Has_Other_than_English_Languages").show();
            $("#Input_Has_Other_than_English_Languages").attr( "required", true );
        }
    });

    var Has_Child_Detained = $('input:radio[name=Has_Child_Detained]');
    Has_Child_Detained.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Child_Detained").attr( "required", false );
            $("#Row_Has_Child_Detained").hide();
        }
        else {
            $("#Row_Has_Child_Detained").show();
            $("#Input_Has_Child_Detained").attr( "required", true );
        }
    });


    // ---- Page 4 ----
    // Page 4 Subbmit Button click event
    $('#SubmitPaper4').click(function(){
        // Page 4 Person to Contact Validation
        var person_to_call = document.getElementById("person_to_contact").value;
        if(person_to_call.length > 1)
        {
            var get_p_mobile_retsult = mobile_checked(person_to_call)
            if (get_p_mobile_retsult == 1)
                {
                    $("#person_to_contact").css('border','1px solid #ccc');
                    $("#person_to_call_block").hide();
                }
            else{
                    $("#person_to_call_block").show();
                    $("#person_to_contact").css('border','1px solid #FF0000');
                    $("#person_to_contact").focus();
                    $("#person_to_call_block").html("Please Enter Valid Mobile Number !");
                    $("#person_to_call_block").css('color','#FF0000');
                    return false
                }
        }
    });

    // Page 4 Has_Play_any_Musical_Instrument
    var Has_Play_any_Musical_Instrument = $('input:radio[name=Has_Play_any_Musical_Instrument]');
    Has_Play_any_Musical_Instrument.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Play_any_Musical_Instrument").attr( "required", false );
            $("#Row_Has_Play_any_Musical_Instrument").hide();
        }
        else {
            $("#Row_Has_Play_any_Musical_Instrument").show();
            $("#Input_Has_Play_any_Musical_Instrument").attr( "required", true );
        }
    });

    // Page 4 Has_Formal_Training_in_Music
    var Has_Formal_Training_in_Music = $('input:radio[name=Has_Formal_Training_in_Music]');
    Has_Formal_Training_in_Music.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Formal_Training_in_Music").attr( "required", false );
            $("#Row_Has_Formal_Training_in_Music").hide();
        }
        else {
            $("#Row_Has_Formal_Training_in_Music").show();
            $("#Input_Has_Formal_Training_in_Music").attr( "required", true );
        }
    });

    // Page 4 Has_Training_or_Interest_Art
    var Has_Training_or_Interest_Art = $('input:radio[name=Has_Training_or_Interest_Art]');
    Has_Training_or_Interest_Art.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Training_or_Interest_Art").attr( "required", false );
            $("#Row_Has_Training_or_Interest_Art").hide();
        }
        else {
            $("#Row_Has_Training_or_Interest_Art").show();
            $("#Input_Has_Training_or_Interest_Art").attr( "required", true );
        }
    });

    // Page 4 Inter_School_Competitions
    var Inter_School_Competitions = $('input:radio[name=Inter_School_Competitions]');
    Inter_School_Competitions.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Inter_School_Competitions").attr( "required", false );
            $("#Row_Inter_School_Competitions").hide();
        }
        else {
            $("#Row_Inter_School_Competitions").show();
            $("#Input_Inter_School_Competitions").attr( "required", true );
        }
    });

    // Page 4 Social_Emotional_Behavioural_Difficulties
    var Social_Emotional_Behavioural_Difficulties = $('input:radio[name=Social_Emotional_Behavioural_Difficulties]');
    Social_Emotional_Behavioural_Difficulties.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Social_Emotional_Behavioural_Difficulties").attr( "required", false );
            $("#Row_Social_Emotional_Behavioural_Difficulties").hide();
        }
        else {
            $("#Row_Social_Emotional_Behavioural_Difficulties").show();
            $("#Input_Social_Emotional_Behavioural_Difficulties").attr( "required", true );
        }
    });

    // Page 4 Has_Use_Bus_Facility
    var Has_Use_Bus_Facility = $('input:radio[name=Has_Use_Bus_Facility]');
    Has_Use_Bus_Facility.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Has_Use_Bus_Facility").attr( "required", false );
            $("#Row_Has_Use_Bus_Facility").hide();
        }
        else {
            $("#Row_Has_Use_Bus_Facility").show();
            $("#Input_Has_Use_Bus_Facility").attr( "required", true );
        }
    });

    // ---- Page 5 ----
    // Page 5 Can_Child_Indicate_his_Toilet_Needs
    var Can_Child_Indicate_his_Toilet_Needs = $('input:radio[name=Can_Child_Indicate_his_Toilet_Needs]');
    Can_Child_Indicate_his_Toilet_Needs.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Can_Child_Indicate_his_Toilet_Needs").attr( "required", false );
            $("#Row_Can_Child_Indicate_his_Toilet_Needs").hide();
        }
        else {
            $("#Row_Can_Child_Indicate_his_Toilet_Needs").show();
            $("#Input_Can_Child_Indicate_his_Toilet_Needs").attr( "required", true );
        }
    });

    // Page 5 Child_Like_to_Watch_TV_Programmes
    var Child_Like_to_Watch_TV_Programmes = $('input:radio[name=Child_Like_to_Watch_TV_Programmes]');
    Child_Like_to_Watch_TV_Programmes.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Child_Like_to_Watch_TV_Programmes").attr( "required", false );
            $("#Row_Child_Like_to_Watch_TV_Programmes").hide();
        }
        else {
            $("#Row_Child_Like_to_Watch_TV_Programmes").show();
            $("#Input_Child_Like_to_Watch_TV_Programmes").attr( "required", true );
        }
    });

    // Page 5 Child_Have_Any_Health_Problem
    var Child_Have_Any_Health_Problem = $('input:radio[name=Child_Have_Any_Health_Problem]');
    Child_Have_Any_Health_Problem.change(function(){
        if ($(this).val() == 'no'){
            $("#Input_Child_Have_Any_Health_Problem").attr( "required", false );
            $("#Row_Child_Have_Any_Health_Problem").hide();
        }
        else {
            $("#Row_Child_Have_Any_Health_Problem").show();
            $("#Input_Child_Have_Any_Health_Problem").attr( "required", true );
        }
    });

    // Page 5 Under_Medication
    var Under_Medication = $('input:radio[name=Under_Medication]');
    Under_Medication.change(function(){
        if ($(this).val() == 'False'){
            $("#Input_Under_Medication").attr( "required", false );
            $("#Row_Under_Medication").hide();
        }
        else {
            $("#Row_Under_Medication").show();
            $("#Input_Under_Medication").attr( "required", true );
        }
    });

    // Page 6 Subbmit Button click event
    $('#SubmitPaper6').click(function(){
        // Page 6 Father Mobile number Validation
        var f_mobile_no = document.getElementById("father_mobile_no").value;
        if (f_mobile_no.length > 1)
        {
            var get_f_mobile_retsult_no = mobile_checked(f_mobile_no)
            if (get_f_mobile_retsult_no == 1)
                {
                    $("#father_mobile_no").css('border','1px solid #ccc');
                    $("#father_mobile_no_block").hide();
                }
            else{
                    $("#father_mobile_no_block").show();
                    $("#father_mobile_no").css('border','1px solid #FF0000');
                    $("#father_mobile_no").focus();
                    $("#father_mobile_no_block").html("Please Enter Valid Mobile Number !");
                    $("#father_mobile_no_block").css('color','#FF0000');
                    return false
                }
        }
        else
        {
            $("#father_mobile_no").css('border','1px solid #ccc');
            $("#father_mobile_no_block").hide();
        }

        // Page 6 Mother Mobile number Validation
        var m_mobile_no = document.getElementById("mother_mobile_no").value;
        if (m_mobile_no.length > 1)
        {
            var get_m_mobile_retsult_no = mobile_checked(m_mobile_no)
            if (get_m_mobile_retsult_no == 1)
                {
                    $("#mother_mobile_no").css('border','1px solid #ccc');
                    $("#mother_mobile_no_block").hide();
                }
            else{
                    $("#mother_mobile_no_block").show();
                    $("#mother_mobile_no").css('border','1px solid #FF0000');
                    $("#mother_mobile_no").focus();
                    $("#mother_mobile_no_block").html("Please Enter Valid Mobile Number !");
                    $("#mother_mobile_no_block").css('color','#FF0000');
                    return false
                }
        }
        else
        {
            $("#mother_mobile_no").css('border','1px solid #ccc');
            $("#mother_mobile_no_block").hide();
        }
     });

});
