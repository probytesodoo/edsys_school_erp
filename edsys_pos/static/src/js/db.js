function edsys_pos_db(instance, module){
    
   /* The PosDB holds reference to data that is either
     * - static: does not change between pos reloads
     * - persistent : must stay between reloads ( orders )
    */
	var pos_base = instance.point_of_sale; 
    module.PosDB = pos_base.PosDB.include({

        /*init: function(options){
            this._super();
        }*/
    
    
    	//Adding new function
    	_partner_search_string : function(partner){
    		var str =  partner.name;
            if(partner.ean13){
                str += '|' + partner.ean13;
            }
            if(partner.student_id){
                str += '|' + partner.student_id;
            }
            if(partner.parents1_id[0]){
                str += '|' + partner.parents1_id[0];
            }
            if(partner.parents1_id[1]){
                str += '|' + partner.parents1_id[1];
            }
            if(partner.address){
                str += '|' + partner.address;
            }
            if(partner.phone){
                str += '|' + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += '|' + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += '|' + partner.email;
            }
            str = '' + partner.id + ':' + str.replace(':','') + '\n';
            return str;
    	}
    
    
    
    
    });
}