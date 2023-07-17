odoo.define('rikai_workflow.reload_department', function (require) {
    "use strict";
    var core = require('web.core');
    var ListController = require('web.ListController');
    ListController.include({
        reload_department: function () {
            var self = this;
            var domain = [];
            var fields = [];
            return this._rpc({
                model: 'rikai.workflow.config.department',
                method: 'reload_department',
                args: [domain, fields]
            }).then(function (result) {
                self.do_action(result);
            });
        },
        renderButtons: function ($node) {
            this._super.apply(this, arguments);
            if (!this.noLeaf && this.hasButtons) {
                this.$buttons.on('click', '#reload_department', this.reload_department.bind(this));
            }
        }

    });
});