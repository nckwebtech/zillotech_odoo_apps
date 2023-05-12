from odoo import models, fields, _
from odoo.exceptions import RedirectWarning
from odoo.tools.misc import formatLang, format_date

INV_LINES_PER_STUB = 9


class ResCompanyData(models.Model):
    _inherit = 'res.company'

    account_check_template_id = fields.Many2one('check.config.template', string='Check Template')
    check_template_boolean = fields.Boolean(string='Checks')


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def do_print_checks(self):
        if self.company_id.check_template_boolean:
            check_layout = self.company_id.account_check_template_id.check_printing_layout_template
        else:
            check_layout = self.company_id.account_check_printing_layout
        redirect_action = self.env.ref('account.action_account_config')
        if not check_layout or check_layout == 'disabled':
            msg = _(
                "You have to choose a check layout. For this, go in Invoicing/Accounting Settings, search for 'Checks layout' and set one.")
            raise RedirectWarning(msg, redirect_action.id, _('Go to the configuration panel'))
        report_action = self.env.ref(check_layout, False)

        if not report_action:
            msg = _(
                "Something went wrong with Check Layout, please select another layout in Invoicing/Accounting Settings and try again.")
            raise RedirectWarning(msg, redirect_action.id, _('Go to the configuration panel'))
        self.write({'is_move_sent': True})
        return report_action.report_action(self)

    def _check_build_page_info(self, i, p):
        if self.company_id.account_check_template_id.check_printing_details_multi:
            page_multi_details = self.company_id.account_check_template_id.check_printing_details_multi
            return {
                'sequence_number': self.check_number,
                'manual_sequencing': self.journal_id.check_manual_sequencing,
                'date': format_date(self.env, self.date),
                'partner_id': self.partner_id,
                'partner_name': self.partner_id.name,
                'currency': self.currency_id,
                'state': self.state,
                'amount': formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID',
                'amount_in_word': self._check_fill_line(self.check_amount_in_words) if i == 0 else 'VOID',
                'memo': self.ref,
                'detailed_cropped': not page_multi_details and len(
                    self.move_id._get_reconciled_invoices()) > INV_LINES_PER_STUB,
                'detailed_lines': p,
            }
        else:
            multi_stub = self.company_id.account_check_printing_multi_stub
            return {
                'sequence_number': self.check_number,
                'manual_sequencing': self.journal_id.check_manual_sequencing,
                'date': format_date(self.env, self.date),
                'partner_id': self.partner_id,
                'partner_name': self.partner_id.name,
                'currency': self.currency_id,
                'state': self.state,
                'amount': formatLang(self.env, self.amount, currency_obj=self.currency_id) if i == 0 else 'VOID',
                'amount_in_word': self._check_fill_line(self.check_amount_in_words) if i == 0 else 'VOID',
                'memo': self.ref,
                'detailed_cropped': not multi_stub and len(
                    self.move_id._get_reconciled_invoices()) > INV_LINES_PER_STUB,
                'detailed_lines': p,
            }

    def _pages_data_check(self):
        pages = self._check_get_pages()
        return pages
