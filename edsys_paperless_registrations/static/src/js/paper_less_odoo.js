$(document).ready(function() {
    Student_Id = $('#Student_Id').val();
    Page_Code = $('#Page_Code').val();
//    alert(window.location.href)
//    alert(window.location.hostname)
    if (window.location.pathname == '/student/verification/pagecode'){
        if (Page_Code == '0' || Page_Code == '3' || Page_Code == '4' || Page_Code == '5'){
            jQuery.ajax({
                url 	: "/get_value_field",
                type	: "POST",
                data 	: {
                            student_id: Student_Id,
                            Page_Code : Page_Code,
                          },
                dataType: 'json',
                success:function(data){
                    if (data)
                    {
                        var size = Object.keys(data).length
                        if(Page_Code == '0')
                        {
                            for (i=0;i<size;i++)
                            {
                                if (data[i][0] == 'allergic'){
                                    if (data[i][1] == true){
                                        $('#id_allergic_1').attr('checked', true);
                                        $('#yes_allergic_id').show();
                                        $('#yes_allergic_id1').show();
                                        $('#yes_allergic_id2').show();
                                    }
                                    else if (data[i][1] == false){
                                        $('#id_allergic_2').attr('checked', true);
                                        $('#yes_allergic_id').hide();
                                        $('#yes_allergic_id1').hide();
                                        $('#yes_allergic_id2').hide();
                                    }
                                }
                                if (data[i][0] == 'under_medication'){
                                    if (data[i][1] == true){
                                        $('#id_under_medication_1').attr('checked', true);
                                        $('#mention_id').show();
                                        $('#mention_id1').show();
                                    }
                                    else if (data[i][1] == false){
                                        $('#id_under_medication_2').attr('checked', true);
                                        $('#mention_id').hide();
                                        $('#mention_id1').hide();
                                    }
                                }

                                if (data[i][0] == 'transport_type'){
                                    if (data[i][1] == 'own'){
                                        $('#id_own_transport').attr('selected', 'selected');
                                        $('#pick_up_hide').hide();
                                        $('#drop_off_points_hide').hide();
                                    }
                                    else if (data[i][1] == 'school'){
                                        $('#id_school_transport').attr('selected', 'selected');
                                        $('#pick_up_hide').show();
                                        $('#drop_off_points_hide').show();
                                    }
                                }
                            }
                        }

                        if(Page_Code == '3')
                        {
                            for (i=0;i<size;i++)
                            {
                                if (data[i][0] == 'has_child_detained'){
                                    if (data[i][1] == 'yes'){
                                        $('#id_Has_Child_Detained_1').attr('checked', true);
                                        $('#Row_Has_Child_Detained').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_Has_Child_Detained_2').attr('checked', true);
                                        $('#Row_Has_Child_Detained').hide();
                                    }
                                }

                                if (data[i][0] == 'child_received_academic_distinction'){
                                    if (data[i][1] == 'yes'){
                                        $('#id_child_received_academic_distinction_1').attr('checked', true);
                                        $('#Row_Child_Received_Academic_Distinction').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_child_received_academic_distinction_2').attr('checked', true);
                                        $('#Row_Child_Received_Academic_Distinction').hide();
                                    }
                                }

                                if (data[i][0] == 'has_suspended_expelled_by_school'){
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_suspended_expelled_by_school_1').attr('checked', true);
                                        $('#Row_Has_Suspended_Expelled_by_School').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_suspended_expelled_by_school_2').attr('checked', true);
                                        $('#Row_Has_Suspended_Expelled_by_School').hide();
                                    }
                                }

                                if (data[i][0] == 'child_associated_with_awareness'){
                                    if (data[i][1] == 'yes'){
                                        $('#id_child_associated_with_awareness_1').attr('checked', true);
                                        $('#Row_Child_Associated_with_Awareness').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_child_associated_with_awareness_2').attr('checked', true);
                                        $('#Row_Child_Associated_with_Awareness').hide();
                                    }
                                }

                                if (data[i][0] == 'member_of_environment_protection'){
                                    if (data[i][1] == 'yes'){
                                        $('#id_member_of_environment_protection_1').attr('checked', true);
                                        $('#Row_Member_of_Environment_Protection').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_member_of_environment_protection_2').attr('checked', true);
                                        $('#Row_Member_of_Environment_Protection').hide();
                                    }
                                    if (data[i][1] == false){
                                        $('#Row_Member_of_Environment_Protection').hide();
                                    }
                                }

                                if (data[i][0] == 'leadership_positions_in_school'){
                                    if (data[i][1] == false){
                                        $('#Row_Leadership_Positions_in_School').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_leadership_positions_in_school_1').attr('checked', true);
                                        $('#Row_Leadership_Positions_in_School').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_leadership_positions_in_school_2').attr('checked', true);
                                        $('#Row_Leadership_Positions_in_School').hide();
                                    }
                                }

                                if (data[i][0] == 'special_education_programme'){
                                    if (data[i][1] == false){
                                        $('#Row_Special_Education_Programme').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_special_education_programme_1').attr('checked', true);
                                        $('#Row_Special_Education_Programme').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_special_education_programme_2').attr('checked', true);
                                        $('#Row_Special_Education_Programme').hide();
                                    }
                                }

                                if (data[i][0] == 'special_learning_disability'){
                                    if (data[i][1] == false){
                                        $('#Row_Special_Learning_Disability').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_special_learning_disability_1').attr('checked', true);
                                        $('#Row_Special_Learning_Disability').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_special_learning_disability_2').attr('checked', true);
                                        $('#Row_Special_Learning_Disability').hide();
                                    }
                                }

                                if (data[i][0] == 'has_other_than_english_languages'){
                                    if (data[i][1] == false){
                                        $('#Row_Has_Other_than_English_Languages').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_other_than_english_languages_1').attr('checked', true);
                                        $('#Row_Has_Other_than_English_Languages').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_other_than_english_languages_2').attr('checked', true);
                                        $('#Row_Has_Other_than_English_Languages').hide();
                                    }
                                }
                            }
                        }
                        if(Page_Code == '4')
                        {
                            for (i=0;i<size;i++)
                            {
                                if (data[i][0] == 'has_play_any_musical_instrument'){
                                    if (data[i][1] == false){
                                        $('#Row_Has_Play_any_Musical_Instrument').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_play_any_musical_instrument_1').attr('checked', true);
                                        $('#Row_Has_Play_any_Musical_Instrument').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_play_any_musical_instrument_2').attr('checked', true);
                                        $('#Row_Has_Play_any_Musical_Instrument').hide();
                                    }
                                }

                                if (data[i][0] == 'has_formal_training_in_music'){
                                    if (data[i][1] == false){
                                        $('#Row_Has_Formal_Training_in_Music').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_formal_training_in_music_1').attr('checked', true);
                                        $('#Row_Has_Formal_Training_in_Music').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_formal_training_in_music_2').attr('checked', true);
                                        $('#Row_Has_Formal_Training_in_Music').hide();
                                    }
                                }

                                if (data[i][0] == 'has_training_or_interest_art'){
                                    if (data[i][1] == false){
                                        $('#Row_Has_Training_or_Interest_Art').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_training_or_interest_art_1').attr('checked', true);
                                        $('#Row_Has_Training_or_Interest_Art').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_training_or_interest_art_2').attr('checked', true);
                                        $('#Row_Has_Training_or_Interest_Art').hide();
                                    }
                                }

                                if (data[i][0] == 'inter_school_competitions'){
                                    if (data[i][1] == false){
                                        $('#Row_Inter_School_Competitions').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_inter_school_competitions_1').attr('checked', true);
                                        $('#Row_Inter_School_Competitions').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_inter_school_competitions_2').attr('checked', true);
                                        $('#Row_Inter_School_Competitions').hide();
                                    }
                                }

                                if (data[i][0] == 'social_emotional_behavioural_difficulties'){
                                    if (data[i][1] == false){
                                        $('#Row_Social_Emotional_Behavioural_Difficulties').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_social_emotional_behavioural_difficulties_1').attr('checked', true);
                                        $('#Row_Social_Emotional_Behavioural_Difficulties').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_social_emotional_behavioural_difficulties_2').attr('checked', true);
                                        $('#Row_Social_Emotional_Behavioural_Difficulties').hide();
                                    }
                                }

                                if (data[i][0] == 'has_use_bus_facility'){
                                    if (data[i][1] == false){
                                        $('#Row_Has_Use_Bus_Facility').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_has_use_bus_facility_1').attr('checked', true);
                                        $('#Row_Has_Use_Bus_Facility').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_has_use_bus_facility_2').attr('checked', true);
                                        $('#Row_Has_Use_Bus_Facility').hide();
                                    }
                                }
                            }
                        }
                        if(Page_Code == '5'){
                            for (i=0;i<size;i++)
                            {
                                if (data[i][0] == 'can_child_indicate_his_toilet_needs'){
                                    if (data[i][1] == false){
                                        $('#Row_Can_Child_Indicate_his_Toilet_Needs').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_can_child_indicate_his_toilet_needs_1').attr('checked', true);
                                        $('#Row_Can_Child_Indicate_his_Toilet_Needs').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_can_child_indicate_his_toilet_needs_1').attr('checked', true);
                                        $('#Row_Can_Child_Indicate_his_Toilet_Needs').hide();
                                    }
                                }

                                if (data[i][0] == 'child_like_to_watch_tv_programmes'){
                                    if (data[i][1] == false){
                                        $('#Row_Child_Like_to_Watch_TV_Programmes').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_child_like_to_watch_tv_programmes_1').attr('checked', true);
                                        $('#Row_Child_Like_to_Watch_TV_Programmes').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_child_like_to_watch_tv_programmes_2').attr('checked', true);
                                        $('#Row_Child_Like_to_Watch_TV_Programmes').hide();
                                    }
                                }

                                if (data[i][0] == 'child_have_any_health_problem'){
                                    if (data[i][1] == false){
                                        $('#Row_Child_Have_Any_Health_Problem').hide();
                                    }
                                    if (data[i][1] == 'yes'){
                                        $('#id_child_have_any_health_problem_1').attr('checked', true);
                                        $('#Row_Child_Have_Any_Health_Problem').show();
                                    }
                                    if (data[i][1] == 'no'){
                                        $('#id_child_have_any_health_problem_2').attr('checked', true);
                                        $('#Row_Child_Have_Any_Health_Problem').hide();
                                    }
                                }
                                if (data[i][0] == 'under_medication'){
                                    if (data[i][1] == true){
                                        $('#id_under_medication_1').attr('checked', true);
                                        $('#Row_Under_Medication').show();
                                    }
                                    else if (data[i][1] == false){
                                        $('#id_under_medication_2').attr('checked', true);
                                        $('#Row_Under_Medication').hide();
                                    }
                                }

                            }
                        }

                    }
                    else
                    {}
                },
                error: function(){
                },
            });
        }
    }
});



//openerp.edsys_paperless_registrations = function (instance) {
//$(document).ready(function() {
//    s_id = $('#Student_Id').val();
//    openerp.jsonRpc("/student/verification/getvalue", 'call', {'student_ids': '4726'})
//        .then(function (data) {
//
//        })
//
//})
//s_id = $('#Student_Id').val();
//openerp.edsys_paperless_registrations = function (instance) {
//    console.log('---->>>>>')
//    }
//$(document).ready(function(require) {
//    "use strict";
//    var Model = require('openert');
//    var res_partner_obj = new Model("res.partner")
//    console.log("aaaaaaa"+res_partner_obj)
//    new Model("res.partner").call("browse",[s_id]).then(function(content){
//    });
//});