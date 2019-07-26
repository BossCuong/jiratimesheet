odoo.define('jira_timesheet.grid_controller', function (require) {
    'use strict';
    var GridController = require('web_grid.GridController')
    var utils = require('web.utils');

    GridController.include({
        events : _.extend({}, GridController.prototype.events, {
            'click .o_grid_input' : '_actionTest',
        }),
        _actionUpdate : function(e){
            alert("hello")
            console.log("aaaaa")
        },
        _actionTest : function(e){

                var self = this;
                var $target = $(e.target);
                var cell_path = $target.parent().attr('data-path').split('.');
                var row_path = cell_path.slice(0, -3).concat(['rows'], cell_path.slice(-2, -1));
                var state = this.model.get();
                var cell = utils.into(state, cell_path);
                var row = utils.into(state, row_path);
                console.log(row)
                var groupFields = state.groupBy.slice(_.isArray(state) ? 1 : 0);
                var label = _.map(groupFields, function (g) {
                    return row.values[g][1] || _t('Undefined');
                }).join(': ');
                console.log(this)
                // pass group by, section and col fields as default in context
                var cols_path = cell_path.slice(0, -3).concat(['cols'], cell_path.slice(-1));
                var col = utils.into(state, cols_path);
                var column_value = col.values[state.colField][0] ? col.values[state.colField][0].split("/")[0] : false;
                var ctx = _.extend({}, this.context);

                //set default value

                ctx['default_Task'] = label;
                ctx['default_Project'] = this.initialState[row_path[0]].__label[1];
                ctx['default_task_ID'] = row.values.task_id[0];
                ctx['default_project_ID'] = this.initialState[row_path[0]].__label[0];
                ctx['default_Date'] = column_value;

                this.do_action({
                    name: 'TimesheetsCustomize',
                    type: 'ir.actions.act_window',
                    res_model: 'customize.transient',
                    views: [[false, 'form']],
                    target : "new",
                    'context' : ctx
                });
            }
    })
})