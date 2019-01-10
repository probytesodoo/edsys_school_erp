
$(document).ready(function () {
	
	
	$('input:radio[name=uae_visa]').change(function(){
        if ($(this).val() == 'no'){
            $("#visa_details").hide();
            $("#visa_type").attr( "required", false );
            $("#visa_number").attr( "required", false );
            $("#visa_issue_date").attr( "required", false );
            $("#visa_expiry_date").attr( "required", false );
            $("#sponsor_name").attr( "required", false );
            $("#sponsor_address").attr( "required", false );
            $("#visa_copy").attr( "required", false );
            $("#visa_div").hide();
            
        }
        else {
        	$("#visa_details").show();
        	$("#visa_type").attr( "required", true );
            $("#visa_number").attr( "required", true );
            $("#visa_issue_date").attr( "required", true );
            $("#visa_expiry_date").attr( "required", true );
            $("#sponsor_name").attr( "required", true );
            $("#sponsor_address").attr( "required", true );
            $("#visa_copy").attr( "required", true );
            $("#visa_div").show();
            
        }
    });
	
	$('input:radio[name=khda_moe_approval]').change(function(){
        if ($(this).val() == 'no'){
            $("#khda_doc").hide();
            $("#document_name").attr( "required", false );
            $("#attested_doc").attr( "required", false );
        }
        else {
        	$("#khda_doc").show();
            $("#document_name").attr( "required", true );
            $("#attested_doc").attr( "required", true );
        }
    });
	
	$('input:radio[name=labour_card_exist]').change(function(){
        if ($(this).val() == 'no'){
            $("#labour_card_details").hide();
            $("#labour_div").hide();
            $("#labour_card_details").attr( "required", false );
            $("#labour_card_copy").attr( "required", false );
        }
        else {
        	$("#labour_card_details").show();
        	$("#labour_div").show();
            $("#labour_card_details").attr( "required", true );
            $("#labour_card_copy").attr( "required", true );
            
        }
    });
	
	
	$('input:radio[name=emirates_id_exist]').change(function(){
        if ($(this).val() == 'no'){
            $("#emirates_id_card_details").hide();
            $("#emirates_div").hide();
            $("#emirates_id_card_details").attr( "required", false );
            $("#emirates_id_copy").attr( "required", false );
        }
        else {
        	$("#emirates_id_card_details").show();
        	$("#emirates_div").show();
            $("#emirates_id_card_details").attr( "required", true );
            $("#emirates_id_copy").attr( "required", true );
            
        }
    });
	
	
	$("#marital").change(function () {
        if ($(this).val() == 'other'){
            $("#specify_marital_status").show();
            $("#please_specify").attr( "required", true );
        }
        else {
        	$("#specify_marital_status").hide();
            $("#please_specify").attr( "required", false );
        }
    });
	
	$("#certificate_name1").change(function () {
		var certificate_name1 = document.getElementById("certificate_name1").value;
        if (certificate_name1 == '-Degree-'){
            $("#certificates_copy1").attr( "required", false );
        }
        else {
            $("#certificates_copy1").attr( "required", true );;
        }
    });
	
	$("#certificate_name2").change(function () {
		var certificate_name2 = document.getElementById("certificate_name2").value;
        if (certificate_name2 == '-Degree-'){
            $("#certificates_copy2").attr( "required", false );
        }
        else {
            $("#certificates_copy2").attr( "required", true );;
        }
    });
	
	$("#certificate_name3").change(function () {
		var certificate_name3 = document.getElementById("certificate_name3").value;
        if (certificate_name3 == '-Degree-'){
            $("#certificates_copy3").attr( "required", false );
        }
        else {
            $("#certificates_copy3").attr( "required", true );;
        }
    });
	
	$("#certificate_name4").change(function () {
		var certificate_name4 = document.getElementById("certificate_name4").value;
        if (certificate_name4 == '-Degree-'){
            $("#certificates_copy4").attr( "required", false );
        }
        else {
            $("#certificates_copy4").attr( "required", true );;
        }
    });
	
	$("#birthday").change(function () {
	    var birthday = document.getElementById("birthday").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (birthday.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("birthday").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (birthday.substring(2, 3) !== '/' || birthday.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("birthday").value = "";
	        return false; 
	    } 
	    day = birthday.substring(0, 2) ; // because months in JS start from 0 
	    month = birthday.substring(3, 5) - 0; 
	    year = birthday.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("birthday").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("birthday").value = "";
	        return false; 
	    }
	});
	
	$("#passport_issue_date").change(function () {
	    var passport_issue_date = document.getElementById("passport_issue_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (passport_issue_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_issue_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (passport_issue_date.substring(2, 3) !== '/' || passport_issue_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_issue_date").value = "";
	        return false; 
	    } 
	    day = passport_issue_date.substring(0, 2) ; // because months in JS start from 0 
	    month = passport_issue_date.substring(3, 5) - 0; 
	    year = passport_issue_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_issue_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_issue_date").value = "";
	        return false; 
	    }
	});
	
	$("#passport_expiry_date").change(function () {
	    var passport_expiry_date = document.getElementById("passport_expiry_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (passport_expiry_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_expiry_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (passport_expiry_date.substring(2, 3) !== '/' || passport_expiry_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_expiry_date").value = "";
	        return false; 
	    } 
	    day = passport_expiry_date.substring(0, 2) ; // because months in JS start from 0 
	    month = passport_expiry_date.substring(3, 5) - 0; 
	    year = passport_expiry_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_expiry_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("passport_expiry_date").value = "";
	        return false; 
	    }
	});
	
	$("#visa_issue_date").change(function () {
	    var visa_issue_date = document.getElementById("visa_issue_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (visa_issue_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_issue_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (visa_issue_date.substring(2, 3) !== '/' || visa_issue_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_issue_date").value = "";
	        return false; 
	    } 
	    day = visa_issue_date.substring(0, 2) ; // because months in JS start from 0 
	    month = visa_issue_date.substring(3, 5) - 0; 
	    year = visa_issue_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_issue_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_issue_date").value = "";
	        return false; 
	    }
	});
	
	$("#visa_expiry_date").change(function () {
	    var visa_expiry_date = document.getElementById("visa_expiry_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (visa_expiry_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_expiry_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (visa_expiry_date.substring(2, 3) !== '/' || visa_expiry_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_expiry_date").value = "";
	        return false; 
	    } 
	    day = visa_expiry_date.substring(0, 2) ; // because months in JS start from 0 
	    month = visa_expiry_date.substring(3, 5) - 0; 
	    year = visa_expiry_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_expiry_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("visa_expiry_date").value = "";
	        return false; 
	    }
	});
	

	$("#permit_expiry_date").change(function () {
	    var permit_expiry_date = document.getElementById("permit_expiry_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (permit_expiry_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("permit_expiry_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (permit_expiry_date.substring(2, 3) !== '/' || permit_expiry_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("permit_expiry_date").value = "";
	        return false; 
	    } 
	    day = permit_expiry_date.substring(0, 2) ; // because months in JS start from 0 
	    month = permit_expiry_date.substring(3, 5) - 0; 
	    year = permit_expiry_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("permit_expiry_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("permit_expiry_date").value = "";
	        return false; 
	    }
	});
	
	$("#emirates_expiry_date").change(function () {
	    var emirates_expiry_date = document.getElementById("emirates_expiry_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (emirates_expiry_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("emirates_expiry_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (emirates_expiry_date.substring(2, 3) !== '/' || emirates_expiry_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("emirates_expiry_date").value = "";
	        return false; 
	    } 
	    day = emirates_expiry_date.substring(0, 2) ; // because months in JS start from 0 
	    month = emirates_expiry_date.substring(3, 5) - 0; 
	    year = emirates_expiry_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("emirates_expiry_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("emirates_expiry_date").value = "";
	        return false; 
	    }
	});
	
	
	$("#date_of_birth_dependent1").change(function () {
	    var date_of_birth_dependent1 = document.getElementById("date_of_birth_dependent1").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (date_of_birth_dependent1.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent1").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (date_of_birth_dependent1.substring(2, 3) !== '/' || date_of_birth_dependent1.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent1").value = "";
	        return false; 
	    } 
	    day = date_of_birth_dependent1.substring(0, 2) ; // because months in JS start from 0 
	    month = date_of_birth_dependent1.substring(3, 5) - 0; 
	    year = date_of_birth_dependent1.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent1").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent1").value = "";
	        return false; 
	    }
	});
	
	$("#date_of_birth_dependent2").change(function () {
	    var date_of_birth_dependent2 = document.getElementById("date_of_birth_dependent2").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (date_of_birth_dependent2.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent1").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (date_of_birth_dependent2.substring(2, 3) !== '/' || date_of_birth_dependent2.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent2").value = "";
	        return false; 
	    } 
	    day = date_of_birth_dependent2.substring(0, 2) ; // because months in JS start from 0 
	    month = date_of_birth_dependent2.substring(3, 5) - 0; 
	    year = date_of_birth_dependent2.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent2").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent2").value = "";
	        return false; 
	    }
	});
	
	$("#date_of_birth_dependent3").change(function () {
	    var date_of_birth_dependent3 = document.getElementById("date_of_birth_dependent3").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (date_of_birth_dependent3.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent3").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (date_of_birth_dependent3.substring(2, 3) !== '/' || date_of_birth_dependent3.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent3").value = "";
	        return false; 
	    } 
	    day = date_of_birth_dependent3.substring(0, 2) ; // because months in JS start from 0 
	    month = date_of_birth_dependent3.substring(3, 5) - 0; 
	    year = date_of_birth_dependent3.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent3").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent3").value = "";
	        return false; 
	    }
	});
	
	$("#date_of_birth_dependent4").change(function () {
	    var date_of_birth_dependent4 = document.getElementById("date_of_birth_dependent4").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (date_of_birth_dependent4.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent4").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (date_of_birth_dependent4.substring(2, 3) !== '/' || date_of_birth_dependent4.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent4").value = "";
	        return false; 
	    } 
	    day	 = date_of_birth_dependent4.substring(0, 2) ; // because months in JS start from 0 
	    month = date_of_birth_dependent4.substring(3, 5) - 0; 
	    year = date_of_birth_dependent4.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent4").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_birth_dependent4").value = "";
	        return false; 
	    }
	});
	
	$("#document_issue_date").change(function () {
	    var document_issue_date = document.getElementById("document_issue_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (document_issue_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_issue_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (document_issue_date.substring(2, 3) !== '/' || document_issue_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_issue_date").value = "";
	        return false; 
	    } 
	    day = document_issue_date.substring(0, 2) ; // because months in JS start from 0 
	    month = document_issue_date.substring(3, 5) - 0; 
	    year = document_issue_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_issue_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_issue_date").value = "";
	        return false; 
	    }
	});
	
	
	$("#document_expiry_date").change(function () {
	    var document_expiry_date = document.getElementById("document_expiry_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (document_expiry_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_expiry_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (document_expiry_date.substring(2, 3) !== '/' || document_expiry_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_expiry_date").value = "";
	        return false; 
	    } 
	    day = document_expiry_date.substring(0, 2) ; // because months in JS start from 0 
	    month = document_expiry_date.substring(3, 5) - 0; 
	    year = document_expiry_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_expiry_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("document_expiry_date").value = "";
	        return false; 
	    }
	});
	
	$("#date_of_interview").change(function () {
	    var date_of_interview = document.getElementById("date_of_interview").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (date_of_interview.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
//	    	document.getElementById("date_of_interview").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (date_of_interview.substring(2, 3) !== '/' || date_of_interview.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_interview").value = "";
	        return false; 
	    } 
	    day = date_of_interview.substring(0, 2) ; // because months in JS start from 0 
	    month = date_of_interview.substring(3, 5) - 0; 
	    year = date_of_interview.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_interview").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("date_of_interview").value = "";
	        return false; 
	    }
	});
	
	
	$("#offer_letter_sent_date").change(function () {
	    var offer_letter_sent_date = document.getElementById("offer_letter_sent_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (offer_letter_sent_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("offer_letter_sent_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (offer_letter_sent_date.substring(2, 3) !== '/' || offer_letter_sent_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("offer_letter_sent_date").value = "";
	        return false; 
	    } 
	    day = offer_letter_sent_date.substring(0, 2) ; // because months in JS start from 0 
	    month = offer_letter_sent_date.substring(3, 5) - 0; 
	    year = offer_letter_sent_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("offer_letter_sent_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("offer_letter_sent_date").value = "";
	        return false; 
	    }
	});
	
	$("#joining_date").change(function () {
	    var joining_date = document.getElementById("joining_date").value;
	    var objDate,  // date object initialized from the ExpiryDate string 
        mSeconds, // ExpiryDate in milliseconds 
        day,      // day 
        month,    // month 
        year;     // year 
	    // date length should be 10 characters (no more no less) 
	    if (joining_date.length !== 10) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("joining_date").value = "";
	        return false; 
	    } 
	    // third and sixth character should be '/' 
	    if (joining_date.substring(2, 3) !== '/' || joining_date.substring(5, 6) !== '/') { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("joining_date").value = "";
	        return false; 
	    } 
	    day = joining_date.substring(0, 2) ; // because months in JS start from 0 
	    month = joining_date.substring(3, 5) - 0; 
	    year = joining_date.substring(6, 10) - 0; 
	    if (year < 1000 || year > 3000) { 
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("joining_date").value = "";
	        return false; 
	    } 
	    if (month > 12){
	    	window.alert("Expected date format is dd/mm/yyyy");
	    	document.getElementById("joining_date").value = "";
	        return false; 
	    }
	});
	
	
	/*$("#isd_contact_number").change(function () {
	    var contact_number = document.getElementById("isd_contact_number").value;
	 
	    if(contact_number.value == "") {
	        window.alert("Error: ISD number must not be null.");
	        document.getElementById("isd_contact_number").value = "";
	        number.focus();
	        return false;
	    }

	    if(contact_number.length > 4) {
	        window.alert("ISD number must be less than 5 digits.");
	        document.getElementById("isd_contact_number").value = "";
	        number.focus();
	        return false;
	    }
	    
	    if(contact_number.length < 3) {
	        window.alert("ISD number must be more than 2 digits.");
	        document.getElementById("isd_contact_number").value = "";
	        number.focus();
	        return false;
	    }
	});*/
	
	/*$("#contact_number").change(function () {
	    var contact_number = document.getElementById("contact_number").value;
	 
	    if(contact_number.value == "") {
	        window.alert("Error: Cell number must not be null.");
	        document.getElementById("contact_number").value = "";
	        number.focus();
	        return false;
	    }

	    if(contact_number1.length < 9) {
	        window.alert("Phone number should be more than 9 digit.");
	        document.getElementById("contact_number").value = "";
	        number.focus();
	        return false;
	    }
	});*/
	
	$("#email_id").change(function () {
		var email_id = document.getElementById("email_id").value;
		var reg = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;

        if (reg.test(email_id) == false) 
        {
            alert('Invalid Email Address');
            document.getElementById("email_id").value = "";
            return false;
        }

        return true;
	});
	
	$("#isd_contact_number1").change(function () {
		alert("ll")
	    var isd_contact_number1 = document.getElementById("isd_contact_number1").value;
	    alert(value);
	    
	    if (isNaN(parseInt(isd_contact_number1)))
	    	{
			    	window.alert("ISD number must be greater than 2 digit.");
			    	document.getElementById("isd_contact_number1").value = "";
			    	return false
	    	}
	    if ( isd_contact_number1.length > 4 ) 
	    {
	    	window.alert("ISD number must be less than or equal to 4 digit.");
	    	document.getElementById("isd_contact_number1").value = "";
	    	return false
	    }
	    if ( isd_contact_number1.length < 3 ) 
	    {
	    	window.alert("ISD number must be greater than 2 digit.");
	    	document.getElementById("isd_contact_number1").value = "";
	    	return false
	    }
    	else
    	{
    		if ( (isd_contact_number1.match(pattern)) ||  (isd_contact_number1.match(pattern1)) )
    		{
		    	return true
		    }
		    else
		    {
		    	window.alert("ISD number not valid.");
		    	document.getElementById("isd_contact_number1").value = "";
		    	return false
		    }
		}
	});
	
	$("#isd_contact_number2").change(function () {
	    var isd_contact_number2 = document.getElementById("isd_contact_number2").value;
	    
	    if (isNaN(parseInt(isd_contact_number2)))
	    	{
			    	window.alert("ISD number must be greater than 2 digit.");
			    	document.getElementById("isd_contact_number2").value = "";
			    	return false
	    	}
	    if ( isd_contact_number2.length > 4 ) 
	    {
	    	window.alert("ISD number must be less than or equal to 4 digit.");
	    	document.getElementById("isd_contact_number2").value = "";
	    	return false
	    }
	    if ( isd_contact_number2.length < 3 ) 
	    {
	    	window.alert("ISD number must be greater than 2 digit.");
	    	document.getElementById("isd_contact_number2").value = "";
	    	return false
	    }
    	else
    	{
    		if ( (isd_contact_number2.match(pattern)) ||  (isd_contact_number2.match(pattern1)) )
    		{
		    	return true
		    }
		    else
		    {
		    	window.alert("ISD number not valid.");
		    	document.getElementById("isd_contact_number2").value = "";
		    	return false
		    }
		}
	});
	
	$("#isd_contact_number3").change(function () {
	    var isd_contact_number3 = document.getElementById("isd_contact_number3").value;
	    
	    if (isNaN(parseInt(isd_contact_number3)))
	    	{
			    	window.alert("ISD number must be greater than 2 digit.");
			    	document.getElementById("isd_contact_number3").value = "";
			    	return false
	    	}
	    if ( isd_contact_number3.length > 4 ) 
	    {
	    	window.alert("ISD number must be less than or equal to 4 digit.");
	    	document.getElementById("isd_contact_number3").value = "";
	    	return false
	    }
	    if ( isd_contact_number3.length < 3 ) 
	    {
	    	window.alert("ISD number must be greater than 2 digit.");
	    	document.getElementById("isd_contact_number3").value = "";
	    	return false
	    }
    	else
    	{
    		if ( (isd_contact_number3.match(pattern)) ||  (isd_contact_number3.match(pattern1)) )
    		{
		    	return true
		    }
		    else
		    {
		    	window.alert("ISD number not valid.");
		    	document.getElementById("isd_contact_number3").value = "";
		    	return false
		    }
		}
	});
	
	
//	$("#isd_contact_number2").change(function () {
//	    var isd_contact_number2 = document.getElementById("isd_contact_number2").value;
//	    var pattern = /^\+?([0-9]{2}|[0-9]{3})$/; 
//	    if (isd_contact_number2.match(pattern)) {
//		    	if (isd_contact_number2.length < 3){
//		    		window.alert("ISD number must be greater than 2 digit.");
//			    	 document.getElementById("isd_contact_number2").value = "";
//			    	 return false
//		    	}
//		    	else{
//		    		return true
//		    	}
//	    	
//	    }
//	    else{
//	    	if (isd_contact_number2.length > 4){
//	    		window.alert("ISD number must be less than 4 digit.");
//		    	 document.getElementById("isd_contact_number2").value = "";
//		    	 return false
//		    }
//	    	if (isd_contact_number2.length < 3){
//	    		window.alert("ISD number must be greater than 2 digit.");
//		    	 document.getElementById("isd_contact_number2").value = "";
//		    	 return false
//	    	}
//	    	
//	    } 
//	});
//	
//	
//	$("#isd_contact_number3").change(function () {
//	    var isd_contact_number3 = document.getElementById("isd_contact_number3").value;
//	    var pattern = /^\+?([0-9]{2}|[0-9]{3})$/; 
//	    
//	    if (isd_contact_number3.match(pattern){
//	    	return true
//	    	
//	    }
//	    else
//    	{
//    	 window.alert("ISD number not valid");
//    	 document.getElementById("isd_contact_number3").value = "";
//    	 return false
//    	}
////	    if ( isd_contact_number3.length > 4 || isd_contact_number3.match(pattern) ){
////    		 
////	    }
////	    if ( isd_contact_number3.length < 3 || isd_contact_number3.match(pattern) ){
////    		window.alert("ISD number not valid");
////	    	 document.getElementById("isd_contact_number3").value = "";
////	    	 return false
////    	}
//	    	
//	});
	
	
	
	
	$("#contact_number1").change(function () {
		alert("ll")
	    var contact_number1 = document.getElementById("contact_number1").value;
	    alert(value);
	    if (isNaN(parseInt(contact_number1)))
    	{
	    	alert("Phone number should be in numbers.");  
            document.getElementById("contact_number1").value = "";
	        number.focus();
            return false;  
    	}
	    if (contact_number1.length < 9){  
            alert("Phone number should be more than 8 digits.");  
            document.getElementById("contact_number1").value = "";
	        number.focus();
            return false;  
        }
	    if (contact_number1.length > 10){  
            alert("Phone number should be less than 10 digits.");  
            document.getElementById("contact_number1").value = "";
	        number.focus();
            return false;  
        }
	    
          
       
	    
	    /*if(contact_number1.value == "") {
	        window.alert("Error: Cell number must not be null.");
	        document.getElementById("contact_number1").value = "";
	        number.focus();
	        return false;
	    }

	    if(contact_number1.length < 9) {
	        window.alert("Phone number should be more than 9 digit.");
	        document.getElementById("contact_number1").value = "";
	        number.focus();
	        return false;
	    }*/
	});
	
	$("#contact_number2").change(function () {
	    var contact_number2 = document.getElementById("contact_number2").value;
	    if (isNaN(parseInt(contact_number2)))
    	{
	    	alert("Phone number should be in numbers.");  
            document.getElementById("contact_number2").value = "";
	        number.focus();
            return false;  
    	}
	    if (contact_number2.length < 9){  
            alert("Phone number should be more than 8 digits.");  
            document.getElementById("contact_number2").value = "";
	        number.focus();
            return false;  
        }
	    if (contact_number2.length > 10){  
            alert("Phone number should be less than 10 digits.");  
            document.getElementById("contact_number2").value = "";
	        number.focus();
            return false;  
        }
	});
	
    $("#contact_number3").change(function () {
	    var contact_number3 = document.getElementById("contact_number3").value;
	    if (isNaN(parseInt(contact_number3)))
    	{
	    	alert("Phone number should be in numbers.");  
            document.getElementById("contact_number3").value = "";
	        number.focus();
            return false;  
    	}
	    if (contact_number3.length < 9){  
            alert("Phone number should be more than 8 digits.");  
            document.getElementById("contact_number3").value = "";
	        number.focus();
            return false;  
        }
	    if (contact_number3.length > 10){  
            alert("Phone number should be less than 10 digits.");  
            document.getElementById("contact_number3").value = "";
	        number.focus();
            return false;  
        }
	    
    });

	$('input:radio[name=is_medical_condition_suffering]').change(function(){
        if ($(this).val() == 'no'){
            $("#medical_details").hide();
            //$("#medical_details").attr( "required", false );
        }
        else {
        	$("#medical_details").show();
            $("#medical_condition").attr( "required", true );
        }
    });
	
	
	$('input:radio[name=is_permanent_address_same]').change(function(){
        if ($(this).val() == 'yes'){
        	current_street = $('#current_street').val();
        	current_street2 = $('#current_street2').val();
        	current_nearest_landmark = $('#current_nearest_landmark').val();
        	current_city = $('#current_city').val();
        	current_state_id = $('#current_state_id').val();
        	current_zip = $('#current_zip').val();
        	current_country_id = $('#current_country_id').val();
        	if (current_state_id == ''){
        		document.getElementById("permnent_state_id").style.display = "none";
        	}
        	else{
        		document.getElementById("permnent_state_id").style.display = "block";
        		$('#permnent_state_id').val(current_state_id); 
        	}
        	$('#permnent_street').val(current_street); 
        	$('#permnent_street2').val(current_street2); 
        	$('#permnent_nearest_landmark').val(current_nearest_landmark); 
        	$('#permnent_city').val(current_city); 
        	
        	$('#permnent_zip').val(current_zip); 
        	$('#permnent_country_id').val(current_country_id);
        	
        	//$("#permanent_address *").attr("disabled", "disabled").off('click');
           
        }
        else {
        	
        	$('#permnent_street').val(''); 
        	$('#permnent_street2').val(''); 
        	$('#permnent_nearest_landmark').val(''); 
        	$('#permnent_city').val(''); 
        	$('#permnent_state_id').val(''); 
        	$('#permnent_zip').val(''); 
        	$('#permnent_country_id').val(''); 
        	document.getElementById("permnent_state_id").style.display = "block";
        	$("#permanent_address *").removeAttr('disabled');
        	
        }
    });
	
	$("select[name='current_country_id']").change(function(){
		var $select = $("select[name='current_state_id']");
        $select.find("option:not(:first)").hide();
        document.getElementById("current_state_id").value = "";
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>1);
    });
	
	$("select[name='permnent_country_id']").change(function(){
		var $select = $("select[name='permnent_state_id']");
        $select.find("option:not(:first)").hide();
        var nb = $select.find("option[data-country_id="+($(this).val() || 0)+"]").show().size();
        $select.parent().toggle(nb>1);
    });
	
	
	$("#year1").change(function () {
	    var year1 = document.getElementById("year1").value;
		if (year1.length > 4)  {
	    	window.alert("Year is not proper. Please check");
	    	document.getElementById("year1").value = "";
	        return false;
	    }

		if (year1.length != 4)  {
        	window.alert("Year is not proper. Please check");
        	document.getElementById("year1").value = "";
            return false;
        }
	});
	
	$("#year2").change(function () {
	    var year2 = document.getElementById("year2").value;
		if (year2.length > 4)  {
	    	window.alert("Year is not proper. Please check");
	    	document.getElementById("year2").value = "";
	        return false;
	    }

		if (year2.length != 4)  {
        	window.alert("Year is not proper. Please check");
        	document.getElementById("year2").value = "";
            return false;
        }
	});
	$("#year3").change(function () {
	    var year3 = document.getElementById("year3").value;
		if (year3.length > 4)  {
	    	window.alert("Year is not proper. Please check");
	    	document.getElementById("year3").value = "";
	        return false;
	    }

		if (year3.length != 4)  {
        	window.alert("Year is not proper. Please check");
        	document.getElementById("year3").value = "";
            return false;
        }
	});
	$("#year4").change(function () {
	    var year4 = document.getElementById("year4").value;
		if (year4.length > 4)  {
	    	window.alert("Year is not proper. Please check");
	    	document.getElementById("year1").value = "";
	        return false;
	    }

		if (year4.length != 4)  {
        	window.alert("Year is not proper. Please check");
        	document.getElementById("year4").value = "";
            return false;
        }
	});
	
	
	$('#employement_form_submit').click(function(){
		var passport_issue_date = document.getElementById("passport_issue_date").value;
	    var passport_expiry_date = document.getElementById("passport_expiry_date").value;
	    
	    var passport_issue_date_obj = moment(passport_issue_date, 'DD/MM/YYYY', true).format();
	    var passport_expiry_date_obj = moment(passport_expiry_date, 'DD/MM/YYYY', true).format();
	    if (passport_expiry_date_obj < passport_issue_date_obj ){
	    	window.alert("Passport expiry date should be greater than passport issue date");
	        document.getElementById("passport_expiry_date").value = "";
	        return false
	    }
	    
	    var visa_issue_date = document.getElementById("visa_issue_date").value;
	    var visa_expiry_date = document.getElementById("visa_expiry_date").value;
	 
	    var visa_issue_date_obj = moment(visa_issue_date, 'DD/MM/YYYY', true).format();
	    var visa_expiry_date_obj = moment(visa_expiry_date, 'DD/MM/YYYY', true).format();
	    if (visa_expiry_date_obj < visa_issue_date_obj ){
	    	window.alert("Visa expiry date should be greater than visa issue date");
	        document.getElementById("visa_expiry_date").value = "";
	        return false
	    }
	    
	    
	    var document_issue_date = document.getElementById("document_issue_date").value;
	    var document_expiry_date = document.getElementById("document_expiry_date").value;
	 
	    var document_issue_date_obj = moment(document_issue_date, 'DD/MM/YYYY', true).format();
	    var document_expiry_date_obj = moment(document_expiry_date, 'DD/MM/YYYY', true).format();
	    if (document_expiry_date_obj < document_issue_date_obj ){
	    	window.alert("Document expiry date should be greater than document issue date");
	        document.getElementById("document_expiry_date").value = "";
	        return false
	    }
	    
	    var _validFileExtensions = [".jpg", ".jpeg", ".bmp", ".gif", ".png"];   
    	var fup = document.getElementById('passport_size_photo');
        var fileName = fup.value;
        if (fileName) {
        var ext = fileName.substring(fileName.lastIndexOf('.') + 1);
		    if(ext =="GIF" || ext=="gif" || ext =="jpg" || ext =="JPG" || ext =="jpeg" || ext =="JPEG" || ext =="bmp" || ext =="BMP" || ext =="png" || ext =="PNG")
		    {
		        return true;
		    }
		    else
		    {
		    	window.alert("Sorry, for Passport Size Photo allowed extensions are: " + _validFileExtensions.join(", "));
		    	document.getElementById("passport_size_photo").value = "";
		        return false;
		    }
        }
	    
	});
	
		$('#new_employement_form_submit_new_from').click(function(){
				
			    var date_of_interview = document.getElementById("date_of_interview").value;
			    var offer_letter_sent_date = document.getElementById("offer_letter_sent_date").value;
			    var joining_date = document.getElementById("joining_date").value;
			    
			    date_of_interview_day = date_of_interview.substring(0, 2) ; // because months in JS start from 0 
			    date_of_interview_month = date_of_interview.substring(3, 5); 
			    date_of_interview_year = date_of_interview.substring(6, 10) - 0; 
			    
			    var date_of_interview_obj = moment(date_of_interview, 'DD/MM/YYYY', true).format();
			    var offer_letter_sent_date_obj = moment(offer_letter_sent_date, 'DD/MM/YYYY', true).format();
			    var joining_date_obj = moment(joining_date, 'DD/MM/YYYY', true).format();
			    if (offer_letter_sent_date_obj < date_of_interview_obj ){
			    	window.alert("Offer letter date should be greater than date of interview");
			        document.getElementById("offer_letter_sent_date").value = "";
			    	return false
			    }
			    if (joining_date_obj < offer_letter_sent_date_obj ){
			    	window.alert("Joining date should be greater than offer letter sent date");
			        document.getElementById("joining_date").value = "";
			    	return false
			    }
			    
			});

	
});




	