$(document).ready(function () {

/*    window.onclick = function(event) {
		alert('1111111111');
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }*/

    $('#re_reg_cheque_all_yes').change(function(){
        var isRadioChecked = this.checked
        if (isRadioChecked == true){
           $('.re_reg_cheque_child_yes').attr("checked", true);
           $('.re_reg_cheque_child_no').attr("checked", false);
        }
        else{
           $('.re_reg_cheque_child_yes').attr("checked", false);
        }
    });

    $('#re_reg_cheque_all_no').change(function(){
        var isRadioChecked = this.checked
        if (isRadioChecked == true){
           $('.re_reg_cheque_child_no').attr("checked", true);
           $('.re_reg_cheque_child_yes').attr("checked", false);
        }
        else{
           $('.re_reg_cheque_child_no').attr("checked", false);
        }
    });

    $( "#re_reg_submit_btn_new" ).unbind('click').click(function() {
    	var count = 0
        var check_count = 0 
        var table_obj = $("#table_re_reg");
        var status = true
        var re_reg_cheque_all_yes = document.getElementById("re_reg_cheque_all_yes").checked;
        var re_reg_cheque_child_no = document.getElementById("re_reg_cheque_all_no").checked;
        var child_length = document.getElementById("child_length").value
        if((re_reg_cheque_all_yes == false) && (re_reg_cheque_child_no == false)){
        	status = false
        }
        
        var name = ''
        
        var message = ''
        table_obj.find('tr').each(function (rowIndex, r) {
                $(this).find('td').each(function (colIndex, c) {
                    if (colIndex == 4){
                        element1 = c.firstChild;
                        element2 = element1.nextElementSibling;
                        element3 = element2.childNodes;
                        radio_yes = element3[1].childNodes[1]
                        radio_no = element3[3].childNodes[0]
                        if((radio_yes.checked == false) && (radio_no.checked == false)){
                        	count = count + 1
                        }
                        if((radio_yes.checked == true) || (radio_no.checked == true)){
                        	check_count = check_count + 1
                        }	
                    }
                });
            });
        if ( check_count != child_length){
        	window.alert('Please select YES/NO');
        	return false
        }
        if ( (status == false) && (count == child_length )){
        	window.alert('Please select something to continue');
        	return false
        }
        if (check_count == child_length )
        {
	        table_obj.find('tr').each(function (rowIndex, r) {
	            $(this).find('td').each(function (colIndex, c) {
	                if (colIndex == 1){
	                    name = $(this).find('span').text();
	                }
	                if (colIndex == 4){
	                    element1 = c.firstChild;
	                    element2 = element1.nextElementSibling;
	                    element3 = element2.childNodes;
	                    radio_yes = element3[1].childNodes[1]
	                    radio_no = element3[3].childNodes[0]
	                    	
	                    if (radio_yes.checked == true){
	                        message += '<p> You have confirmed Re-Registration for ' + name + '</p>'
	                    }
	                    else if ((radio_no.checked == false) && (radio_yes.checked == false)){
	                        message += '<p> You have <b> not given any response</b> for ' + name + '</p>'
	                    }
	                    else if (radio_no.checked == true){
	                        message += '<p> You have <b> not </b> confirmed Re-Registration for ' + name + '</p>'
	                    }
	                }
	            });
	        });
	        $("#dialog_message").find('p').remove();
	        $("#dialog_message").append(message);
	        var modal = document.getElementById('myModal');
	        modal.style.display = "block";
	        var cancle_button = $('#re_reg_dilog_cancle');
	        cancle_button.click(function(){
	            modal.style.display = "none";
	            return false
	        });
        }
        return false
    });
});
