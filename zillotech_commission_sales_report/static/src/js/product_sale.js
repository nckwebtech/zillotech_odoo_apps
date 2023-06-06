odoo.define('zillotech_commission_sales_report.product_sale', function (require) {
    'use strict';
    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var field_utils = require('web.field_utils');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var utils = require('web.utils');
    var QWeb = core.qweb;
    var framework = require('web.framework');
    var _t = core._t;

    var datepicker = require('web.datepicker');
    var time = require('web.time');


    window.click_num = 0;

    var CommissionSales = AbstractAction.extend({
    template: 'CommissionReportTemp',
        events: {
            'click .parent-line': 'journal_line_click',
            'click .child_col1': 'journal_line_click',
            'click #pdf': 'print_pdf',
            'click #xlsx': 'print_xlsx',
            'click .gl-line': 'show_drop_down',
            'click .view-account-move': 'view_acc_move',

        },

        init: function(parent, action) {
                this._super(parent, action);
                this.currency=action.currency;
                this.product_report_lines = action.product_report_lines;
                this.wizard_id = action.context.wizard | null;
                this.params = action.params;

                this.originalAction = JSON.parse(action._originalAction);
                console.log('_originalAction',this.originalAction);

            },


          start: function() {
            var self = this;
            self.initial_render = true;
            rpc.query({
                model: 'account.commission.sales',
                method: 'create',
                args: [{

                }]
            }).then(function(t_res) {
                self.wizard_id = t_res;

                self.load_data(self.initial_render);
            })
        },







        load_data: function (initial_render = true) {

            var self = this;


                self.$(".categ").empty();''
                try{
                    var self = this;
                    var params = this.originalAction;


                    self._rpc({
                        model: 'account.commission.sales',
                        method: 'view_report',
                        args: [[this.wizard_id], params],
                    }).then(function(datas) {
                    _.each(datas['product_report_lines'][0], function(rep_lines) {
                            rep_lines['direction_amount'] = self.format_currency(datas['currency'],rep_lines['direction_amount']);
                             });

                             if (initial_render) {
                            self.$('.filter_view_tb').html(QWeb.render('CommissionReportFilterView',
                            {wizard_data: datas['wizard_data'],}));

                            }


                            var child=[];

                        self.$('.table_view_tb').html(QWeb.render('CommissionSaleTable', {
                                            product_report_lines : datas['product_report_lines'],
                                            move_lines :datas['product_report_lines'][2],
                                            currency : datas['currency'],
                                        }));


                });

                    }
                catch (el) {
                    window.location.href
                    }
            },
            format_currency: function(currency, amount) {
                if (typeof(amount) != 'number') {
                    amount = parseFloat(amount);
                }
                var formatted_value = (parseInt(amount)).toLocaleString(currency[2],{
                    minimumFractionDigits: 2
                })
                return formatted_value
            },


        print_pdf: function(e) {
            e.preventDefault();
            var self = this;
            var params = this.originalAction;
            self._rpc({
                model: 'account.commission.sales',
                method: 'view_report',
                args: [
                    [self.wizard_id], params
                ],
            }).then(function(data) {
                console.log('cool', data);
                var action = {
                    'type': 'ir.actions.report',
                    'report_type': 'qweb-pdf',
                    'report_name': 'zillotech_commission_sales_report.commission_sales',
                    'report_file': 'zillotech_commission_sales_report.commission_sales',
                    'data': {
                        'report_data': data
                    },
                    'context': {
                        'active_model': 'account.commission.sales',
                        'landscape': 1,
                        'commission_sales_pdf_report': true
                    },
                    'display_name': 'Commission Sales',
                };
                return self.do_action(action);
            });
        },
//
        print_xlsx: function() {
            var self = this;
            var params = this.originalAction;
            self._rpc({
                model: 'account.commission.sales',
                method: 'view_report',
                args: [
                    [self.wizard_id], params
                ],
            }).then(function(data) {
                console.log('data', data);
                var action = {
                    'data': {
                         'model': 'account.commission.sales',
                         'output_format': 'xlsx',
                         'report_data': JSON.stringify(data['product_report_lines']),
                         'wizard_data' : JSON.stringify(data['wizard_data']),
                         'report_name': 'Commission Sales',
                         'dfr_data': JSON.stringify(data),
                    },
                };

                  self.downloadXlsx(action);
            });
        },

        downloadXlsx: function (action){
        framework.blockUI();
            session.get_file({
                url: '/dynamic_xlsx_commission_reports',
                data: action.data,
                complete: framework.unblockUI,
                error: (error) => this.call('crash_manager', 'rpc_error', error),
            });
        },

        create_lines_with_style: function(rec, attr, datas) {
            var temp_str = "";
            var style_name = "border-bottom: 1px solid #e6e6e6;";
            var attr_name = attr + " style="+style_name;



            temp_str += "<td  class='child_col1' "+attr_name+" >"+rec['code'] +rec['name'] +"</td>";
            if(datas.currency[1]=='after'){
            temp_str += "<td  class='child_col2' "+attr_name+" >"+rec['debit'].toFixed(2)+datas.currency[0]+"</td>";
            temp_str += "<td  class='child_col3' "+attr_name+" >"+rec['credit'].toFixed(2) +datas.currency[0]+ "</td>";

            }
            else{
            temp_str += "<td  class='child_col2' "+attr_name+" >"+datas.currency[0]+rec['debit'].toFixed(2) + "</td>";
            temp_str += "<td  class='child_col3' "+attr_name+">"+datas.currency[0]+rec['credit'].toFixed(2) + "</td>";

            }
            return temp_str;
        },


        journal_line_click: function (el){
            click_num++;
            var self = this;
            var line = $(el.target).parent().data('id');

            return self.do_action({
                type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: 'account.move',
                    views: [
                        [false, 'form']
                    ],
                    res_id: line,
                    target: 'current',
            });

        },

        show_drop_down: function(event) {
            event.preventDefault();
            var self = this;
            var params = {};
            var account_id = $(event.currentTarget).data('account-id');

            var product_id = $(event.currentTarget)[0].cells[0].innerText;
            var offset = 0;
            var td = $(event.currentTarget).next('tr').find('td');
            if (td.length == 1) {

                    self._rpc({
                        model: 'account.commission.sales',
                        method: 'view_report',
                        args: [
                            [self.wizard_id], params
                        ],
                    }).then(function(data) {


                    for (var i = 0; i < data['product_report_lines'][0].length; i++) {
                    if (account_id == data['product_report_lines'][0][i]['partner_id'] ){
                    $(event.currentTarget).next('tr').find('td .gl-table-div').remove();
                    $(event.currentTarget).next('tr').find('td ul').after(
                        QWeb.render('SubSectionalCommissionInvoice', {
                            account_data: data['product_report_lines'][0][i]['child_lines'],
                            total_data : data['product_report_lines'][0][i]['total_lines'],
                        }))
                    $(event.currentTarget).next('tr').find('td ul li:first a').css({
                        'background-color': '#00ede8',
                        'font-weight': 'bold',
                    });
                     }
                    }

                    });


            }
        },

        view_acc_move: function(event) {
            event.preventDefault();
            var self = this;
            var context = {};
            var show_acc_move = function(res_model, res_id, view_id) {
                var action = {
                    type: 'ir.actions.act_window',
                    view_type: 'form',
                    view_mode: 'form',
                    res_model: res_model,
                    views: [
                        [view_id || false, 'form']
                    ],
                    res_id: res_id,
                    target: 'current',
                    context: context,
                };
                return self.do_action(action);
            };
            rpc.query({
                    model: 'account.move',
                    method: 'search_read',
                    domain: [
                        ['id', '=', $(event.currentTarget).data('move-id')]
                    ],
                    fields: ['id'],
                    limit: 1,
                })
                .then(function(record) {
                    if (record.length > 0) {
                        show_acc_move('account.move', record[0].id);
                    } else {
                        show_acc_move('account.move', $(event.currentTarget).data('move-id'));
                    }
                });
        },


    });
    core.action_registry.add("p_c", CommissionSales);
    return CommissionSales;
});