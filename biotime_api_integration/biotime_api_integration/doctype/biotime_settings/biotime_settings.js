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
                } else {
                    frappe.msgprint({
                        title: __("Connection Failed"),
                        indicator: "red",
                        message: __("Unable to connect. Please check your settings and try again.")
                    });
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
                if (r.message && r.message.status === "success") {
                    frappe.msgprint("Sync Successful");
                } else {
                    frappe.msgprint({
                        title: __("Sync Failed"),
                        indicator: "red",
                        message: r.message.error || __("An error occurred during the sync process.")
                    });
                }
                frm.refresh();
            }
        });
    }
});


