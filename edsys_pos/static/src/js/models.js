function edsys_pos_models(instance, module){
    //pos_base is instance.point_of_sale;

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var pos_base = instance.point_of_sale; 
    // Add a model to load at POS start
    pos_base.PosModel.prototype.models.push({
        model: 'res.partner',
        fields: ['name','student_id','parent1_id','student_section_id', 'batch_id', 'parents1_id', 'class_id'],
        domain: [['is_student','=',true]],
        loaded: function(self,partners){
        	self.partners = partners;
        	//self.db.add_partners(partners);
        }
    });

    // Update existing model loader
    var models = pos_base.PosModel.prototype.models;
    for(var i=0; i<models.length; i++){
        var model=models[i];
        if(model.model === 'res.partner'){
             model.fields.push('student_id');
             model.fields.push('parent1_id');
             model.fields.push('student_section_id');
             model.fields.push('batch_id');
             model.fields.push('parents1_id');
             model.fields.push('class_id');
        } 
    }
    module.Order = Backbone.Model.extend({
        initialize: function(attributes){
            Backbone.Model.prototype.initialize.apply(this, arguments);
            this.pos = attributes.pos; 
            this.sequence_number = this.pos.pos_session.sequence_number++;
            this.uid =     this.generateUniqueId();
            this.set({
                creationDate:   new Date(),
                orderLines:     new module.OrderlineCollection(),
                paymentLines:   new module.PaymentlineCollection(),
                name:           _t("Order ") + this.uid,
                client:         null,
            });
            this.selected_orderline   = undefined;
            this.selected_paymentline = undefined;
            this.screen_data = {};  // see ScreenSelector
            this.receipt_type = 'receipt';  // 'receipt' || 'invoice'
            this.temporary = attributes.temporary || false;
            return this;
        },

        getTotalTaxExcluded: function() {
            return round_pr((this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + orderLine.get_price_without_tax();
            }), 0), this.pos.currency.rounding);
        },
        
        getTotalTaxIncluded: function() {
            return this.getTotalTaxExcluded() + this.getTax();
        },
        getTaxDetails: function(){
            var details = {};
            var fulldetails = [];

            this.get('orderLines').each(function(line){
                var ldetails = line.get_tax_details();
                for(var id in ldetails){
                    if(ldetails.hasOwnProperty(id)){
                        details[id] = (details[id] || 0) + ldetails[id];
                    }
                }
            });
            
            for(var id in details){
                if(details.hasOwnProperty(id)){
                    fulldetails.push({amount: details[id], tax: this.pos.taxes_by_id[id], name: this.pos.taxes_by_id[id].name});
                }
            }

            return fulldetails;
        },
        getDiscountTotal: function() {
            return round_pr((this.get('orderLines')).reduce((function(sum, orderLine) {
                return sum + (orderLine.get_unit_price() * (orderLine.get_discount()/100) * orderLine.get_quantity());
            }), 0), this.pos.currency.rounding);
        },
        getTotalTaxIncluded: function() {
            return this.getTotalTaxExcluded() + this.getTax();
        },

        getChange: function() {
            return this.getPaidTotal() - this.getTotalTaxIncluded();
        },
        
    });




}
