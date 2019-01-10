odoo.edsys_pos = function(instance) {

    var module = instance.edsys_pos; // Create namespace of edsys_pos for your own classes

    var pos_base = instance.point_of_sale; // Namespace of point_of_sale module that holds classes of the POS

    edsys_pos_db(instance,module);         // import db.js

    edsys_pos_models(instance,module);     // import models.js

    //pos_template_screens(instance,module);    // import screens.js

    //pos_template_widgets(instance,module);    // import widgets.js

};
