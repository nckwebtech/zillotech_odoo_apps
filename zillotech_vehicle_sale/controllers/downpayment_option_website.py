from odoo.addons.website_sale.controllers.main import WebsiteSale
import json
from odoo import http, fields
from odoo.http import request
from odoo.tools.json import scriptsafe as json_scriptsafe


class WebsiteDownPayment(WebsiteSale):

    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        order = request.website.sale_get_order()
        down_payment_amount = float()
        if order:
            for product in order.order_line:
                if product.product_id.down_payment_amount > 1:
                    down_payment_amount += float(product.product_id.down_payment_amount * product.product_uom_qty)
            order.down_payment_amount = down_payment_amount
            load_data = json.loads(order.tax_totals_json)
            order.balance_amount = load_data['amount_total'] - order.down_payment_amount
        return super(WebsiteDownPayment, self).shop_payment()

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
                         **kw):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=1)
            else:
                return {}

        pcav = kw.get('product_custom_attribute_values')
        nvav = kw.get('no_variant_attribute_values')
        value = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=json_scriptsafe.loads(pcav) if pcav else None,
            no_variant_attribute_values=json_scriptsafe.loads(nvav) if nvav else None
        )
        print(value, '22')

        if not order.cart_quantity:
            request.website.sale_reset()
            return value

        order = request.website.sale_get_order()
        value['cart_quantity'] = order.cart_quantity

        if not display:
            return value
        if order:
            order.down_payment_amount = False
            order.balance_amount = False
        value['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template("website_sale.cart_lines", {
            'website_sale_order': order,
            'date': fields.Date.today(),
            'suggested_products': order._cart_accessories()
        })
        value['website_sale.short_cart_summary'] = request.env['ir.ui.view']._render_template(
            "website_sale.short_cart_summary", {
                'website_sale_order': order,
            })
        return value

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        """ End of checkout process controller. Confirmation is basically seing
        the status of a sale.order. State at this point :

         - should not have any context / session info: clean them
         - take a sale.order id, because we request a sale.order and are not
           session dependant anymore
        """
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            if order:
                if order.down_payment_amount:
                    order.action_confirm()
                    if order.down_payment_amount:
                        request.env['sale.advance.payment.inv'].with_context(active_model='sale.order',
                                                                             active_ids=order.ids).create(
                            {'advance_payment_method': 'fixed',
                             'fixed_amount': order.down_payment_amount}).create_invoices()

                return request.render("website_sale.confirmation", {
                    'order': order,
                    'order_tracking_info': self.order_2_return_dict(order),
                })
            else:
                return request.redirect('/shop')

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        order = request.website.sale_get_order()
        if order:
            order.down_payment_amount = False
            order.balance_amount = False
        return super(WebsiteDownPayment, self).cart()

    @http.route(['/shop/print_catalog'], type='http', auth="user", website=True, sitemap=False)
    def print_catalog(self, product_id):
        r = request.env.ref('zillotech_vehicle_sale.action_inventory_product_report')
        pdf = r.sudo()._render_qweb_pdf([int(product_id)])[0]
        pdf_headers = [('Content-Type', 'application/pdf'),
                       ('Content-Length', len(pdf)), ]
        return request.make_response(pdf, headers=pdf_headers)
