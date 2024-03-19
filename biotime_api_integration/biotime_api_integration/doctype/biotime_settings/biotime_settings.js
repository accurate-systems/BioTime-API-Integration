// Copyright (c) 2024, BioTime and contributors
// For license information, please see license.txt

frappe.ui.form.on("BioTime Settings", {
    refresh: function(frm) {
        frm.add_custom_button(__("Check Connection"), function() {
            frm.events.check_connection(frm);
        });
        frm.add_custom_button(__("Sync Transactions"), function() {
            frm.events.sync_transactions(frm);
        });
    },
	check_connection(frm) {
        frappe.call({
            method: "check_connection",
            doc: frm.doc,
            freeze: true,
            callback: function(r) {
                if (r.message) {
                    frappe.msgprint("Connection Successful");
                    
                }
            }
        });
	},
    sync_transactions(frm) {
        frappe.call({
            method: "sync_transactions",
            doc: frm.doc,
            freeze: true,
            callback: function(r) {
                frappe.msgprint("Sync Successful");
                frm.refresh();
            }
        });
    }
});


