from odoo import models, fields


class USCheckConfig(models.Model):
    _name = 'check.config.template'
    _description = 'Check Configuration Template'
    _rec_name = 'template_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    template_name = fields.Char('Template Name', required=True)

    check_printing_layout_template = fields.Selection(selection=[('disabled', 'None'),
                                                                 ('zillotech_us_check_print.action_print_check_top',
                                                                  'Print Check (Top)'),
                                                                 (
                                                                     'zillotech_us_check_print'
                                                                     '.action_print_check_middle',
                                                                     'Print Check (Middle)'),
                                                                 (
                                                                     'zillotech_us_check_print'
                                                                     '.action_print_check_bottom',
                                                                     'Print Check (Bottom)'),
                                                                 ], string='Choose Check Template', default='disabled',
                                                      ondelete={
                                                          'zillotech_us_check_print.action_print_check_top': 'set '
                                                                                                       'default',
                                                          'zillotech_us_check_print.action_print_check_middle': 'set default',
                                                          'zillotech_us_check_print.action_print_check_bottom': 'set default',
                                                      })

    check_printing_details_multi = fields.Boolean(
        string='Check Details on Multi-Pages')
    check_printing_top_margin = fields.Float(
        string='Top Margin of Check',
        default=0.25)
    check_printing_left_margin = fields.Float(
        string='Left Margin of Check',
        default=0.25)

    # Customized margin css
    css_top_date_top = fields.Float('Top Margin of Date')
    css_top_date_left = fields.Float('Left Margin of Date')
    css_check_top_payee_name_top = fields.Float('Top Margin of Payee Name')
    css_check_top_payee_name_left = fields.Float('Left Margin of Payee Name')
    css_check_top_amount_top = fields.Float('Top Margin of Top Amount')
    css_check_top_amount_left = fields.Float('Left Margin of Top Amount')
    css_check_top_amount_in_word_top = fields.Float('Top Margin of Top Amount in Word')
    css_check_top_amount_in_word_left = fields.Float('Left Margin of Top Amount in Word')
    css_check_top_payee_addr_top = fields.Float('Top Margin of Payee Address')
    css_check_top_payee_addr_left = fields.Float('Left Margin of Payee Address')
    css_check_top_memo_top = fields.Float('Top Margin of Top Memo')
    css_check_top_memo_left = fields.Float('Left Margin of Top Memo')


class ResConfigSettingsData(models.TransientModel):
    _inherit = 'res.config.settings'

    check_template_boolean = fields.Boolean(related='company_id.check_template_boolean', string='Checks',
                                            readonly=False)
    check_template_id = fields.Many2one('check.config.template', string='Check Template',
                                        related='company_id.account_check_template_id',
                                        readonly=False)
