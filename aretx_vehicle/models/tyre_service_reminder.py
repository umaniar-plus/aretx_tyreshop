from odoo import models, api, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import datetime
from odoo.http import request
from odoo import api, fields, models, _, tools
from datetime import date, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import logging
from datetime import date

_logger = logging.getLogger(__name__)


class TyreServiceReminder(models.Model):
    _name = 'tyre.service.reminder'
    _description = 'Tyre Service Reminder Cron'

    @api.model
    def _cron_tyre_service_reminder1(self, account_type=2):
        message = "hi test from Odoo via Green API"

        GREEN_API_URL = "https://api.green-api.com/waInstance7107346943/sendMessage/814baecb2a9447248923cd769ed527bfd1664438ce864ee49f"

        payload = {
            "chatId": "917405292322@c.us",  # 👈 your number in proper format
            "message": message
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(GREEN_API_URL, json=payload, headers=headers)

        print("response.status_code", response.status_code)
        print("response.text", response.text)

        return False

        template_id = self.env['custom.sms.templates'].browse(1)
        c_data = template_id.description
        if vehicle_id is not False and vehicle_id.x_vehicle_number_id is not False and c_data is not False and '%vehicle%' in c_data:
            c_data = c_data.replace("%vehicle%", vehicle_id.x_vehicle_number_id)

        if c_data is not False and '%customer%' in c_data:
            c_data = c_data.replace("%customer%", customer.name)

        if c_data is not False and '%bill_amount%' in c_data:
            c_data = c_data.replace("%bill_amount%", str(account_move.amount_total))

        # create entry in aretx_sms_composer
        if vehicle_id:
            aretx_sms_composer = self.env['aretx.sms.composer'].create({
                'res_model': 'account.move',  # self.partner_id.id,
                'res_id': account_move_id,  # self.partner_id.id,
                'number': phone,
                'number_field_name': 'phone',
                'partner_id': customer_id,
                'vehicle_id': vehicle_id.id,
                'template_id': template_id.id,
                'title': template_id.name,
                'content': c_data,
                'recipient_single_number_itf': phone,
                'vehicle_number': vehicle_id.x_vehicle_number_id,
                'is_vehicle': 1,
            })
        else:
            aretx_sms_composer = self.env['aretx.sms.composer'].create({
                'res_model': 'account.move',  # self.partner_id.id,
                'res_id': account_move_id,  # self.partner_id.id,
                'number': phone,
                'number_field_name': 'phone',
                'partner_id': customer_id,
                'template_id': template_id.id,
                'title': template_id.name,
                'content': c_data,
                'recipient_single_number_itf': phone,
            })
        query = self.env['custom.sms.setting'].browse(1)
        print('query', query)
        query.ensure_one()
        if query:
            data = {}
            data[query.userid_map] = query.userid
            data[query.userid_password_map] = query.userpassword
            data[query.account_type_map] = account_type
            data[query.phonenumber_map] = partner.mobile
            # data[query.phonenumber_map] = '7405292322'
            data[query.msg_map] = c_data
            data[query.gsm_map] = query.gsm_sendername
            print('query.send_url', query.send_url)
            print('data', data)
            return False
            response = requests.get(query.send_url, data)
            print('response', response)
            # response = requests.get(query.balance_url, headers=REQUEST_CUSTOM_HEADER, data=request_data)
            error = ["Invalid Template", "Authentication Fail", "Invalid Sender ID",
                     'Error :- Object reference not set to an instance of an object.', "No Data Found"]
            if response.status_code == 200 and response.text not in error:
                # save msg_id in sms_delivery_report table
                vals_list = {}
                vals_list['msg_id'] = response.text
                vals_list['log_date'] = datetime.datetime.now().strftime("%d %B %Y")

                vals_list['delivery_status'] = 0  # datetime.datetime.now().strftime("%d%m%y")
                aretx_sms_composer.write(vals_list)
                # return True
            else:
                aretx_sms_composer.write({'error_log_status': response.status_code, 'error_log_text': response.text})
                # return True

    @api.model
    def _cron_tyre_service_reminder(self, account_type=2):
        """Send reminder messages per vehicle based on configuration."""
        ir_config = self.env['ir.config_parameter'].sudo()
        km_limit = int(ir_config.get_param('tyreshop.tyre_message_km', default=5000))
        month_limit = int(ir_config.get_param('tyreshop.tyre_message_months', default=3))

        print('system settings')
        print(km_limit, month_limit)

        today = fields.Date.today()
        Vehicle = self.env['vehicle.master.model'].sudo()
        print('today date', today)
        print('Vehicle', Vehicle)

        vehicles = Vehicle.search([('x_avg_km', '>', 0)])
        print('vehicles', vehicles)
        template_id = self.env['custom.sms.templates'].browse(1)

        for vehicle in vehicles:
            # Get last date properly
            c_data = template_id.description
            print('c_data', c_data)
            last_date = vehicle.last_message_date
            # print('last_date', last_date)
            if not last_date and vehicle.create_date:
                # Convert datetime to date
                last_date = vehicle.create_date.date()
            elif not last_date:
                last_date = today
            print('last_date', last_date)
            days_since_last = (today - last_date).days
            print('days_since_last', days_since_last)
            months_since_last = days_since_last / 30.0
            print('months_since_last', months_since_last)
            monthly_avg = vehicle.x_avg_km  # Assuming this is "average km per month"
            print('monthly_avg', monthly_avg)
            expected_km = monthly_avg * months_since_last
            print('expected_km', expected_km)
            # Safe subtraction (both are datetime.date)
            days_diff = (today - last_date).days
            print('days_diff', days_diff)
            month_days = month_limit * 30
            print('month_days', month_days)
            km_due = vehicle.x_avg_km >= km_limit
            print('expected_km')
            print(expected_km)
            print('km_limit')
            print(km_limit)
            km_due = expected_km >= km_limit
            print('km_due')
            print(km_due)
            month_due = days_diff >= month_days
            month_due = months_since_last >= month_limit
            print('month_due')
            print(month_due)
            partner = vehicle.x_customer_id
            print(partner.mobile)
            if not partner.mobile:
                raise ValidationError("Please update the mobile number before proceeding!")

            if km_due or month_due and partner.mobile:
                partner = vehicle.x_customer_id
                print('started a sending a msg to partner !!!!')
                print(vehicle.x_customer_id)
                print(partner)
                print(vehicle)
                x_avg_km = vehicle.x_avg_km
                message = (
                    f"Dear {partner.name}, Mobile Number {partner.mobile}, your vehicle ({vehicle.x_vehicle_number_id or partner_id.name}) "
                    f"has run {vehicle.x_avg_km} KM. It's time for a tyre service check!"
                )
                print('x_avg_km', x_avg_km)

                # Post message to chatter
                if c_data is not False and partner and '%partner_name%' in c_data:
                    c_data = c_data.replace("%partner_name%", partner.name)
                # print('c_data', c_data)
                # print('partner', partner.mobile)
                # if c_data is not False and '%partner_phone%' in c_data:
                #     c_data = c_data.replace("%partner_phone%", partner.mobile)

                if c_data is not False and '%vehicle_x_vehicle_number_id%' in c_data:
                    c_data = c_data.replace("%vehicle_x_vehicle_number_id%", vehicle.x_vehicle_number_id)
                print('c_data', c_data)
                if c_data is not False and '%vehicle_x_avg_km%' in c_data:
                    c_data = c_data.replace("%vehicle_x_avg_km%", str(x_avg_km))
                print('c_data', c_data)

                partner.message_post(body=message)
                # Reset values
                vehicle.last_message_date = today
                # create entry in aretx_sms_composer
                if vehicle:
                    aretx_sms_composer = self.env['aretx.sms.composer'].create({
                        'res_model': 'vehicle.master.model',  # self.partner_id.id,
                        'res_id': vehicle.id,  # self.partner_id.id,
                        'number': partner.mobile,
                        'number_field_name': 'phone',
                        'partner_id': partner.id,
                        'vehicle_id': vehicle.id,
                        'template_id': template_id.id,
                        'title': template_id.name,
                        'content': c_data,
                        'recipient_single_number_itf': partner.mobile,
                        'vehicle_number': vehicle.x_vehicle_number_id,
                        'is_vehicle': 1,
                    })
                else:
                    aretx_sms_composer = self.env['aretx.sms.composer'].create({
                        'res_model': 'vehicle.master.model',  # self.partner_id.id,
                        'res_id': vehicle,  # self.partner_id.id,
                        'number': partner.mobile,
                        'number_field_name': 'phone',
                        'partner_id': partner.id,
                        'template_id': template_id.id,
                        'title': template_id.name,
                        'content': c_data,
                        # 'recipient_single_number_itf': partner.mobile,
                    })
                query = self.env['custom.sms.setting'].browse(1)
                print('query', query)
                query.ensure_one()
                clean_phone = partner.mobile.replace("+91", "").strip()
                clean_phone = partner.mobile.replace("+91", "").replace(" ", "").strip()

                print(clean_phone)
                if query:
                    data = {}
                    data[query.userid_map] = query.userid
                    data[query.userid_password_map] = query.userpassword
                    data[query.account_type_map] = account_type
                    data[query.phonenumber_map] = clean_phone
                    data[query.msg_map] = c_data
                    data[query.gsm_map] = query.gsm_sendername
                    print('data', data)

                    response = requests.get(query.send_url, data)
                    print('sms sent to partner.')
                    print('response', response)
                    # response = requests.get(query.balance_url, headers=REQUEST_CUSTOM_HEADER, data=request_data)
                    error = ["Invalid Template", "Authentication Fail", "Invalid Sender ID",
                             'Error :- Object reference not set to an instance of an object.', "No Data Found"]
                    if response.status_code == 200 and response.text not in error:
                        # save msg_id in sms_delivery_report table
                        vals_list = {}
                        vals_list['msg_id'] = response.text
                        vals_list['log_date'] = datetime.datetime.now().strftime("%d %B %Y")

                        vals_list['delivery_status'] = 0  # datetime.datetime.now().strftime("%d%m%y")
                        print('vals_list', vals_list)
                        aretx_sms_composer.write(vals_list)
                        # return True
                    else:
                        aretx_sms_composer.write(
                            {'error_log_status': response.status_code, 'error_log_text': response.text})
                        # return True

    @api.model
    def send_whatsapp_service_reminder(self, template, vehicle):
        provider = template.provider_id
        if not provider:
            raise UserError("No WhatsApp provider configured.")
        channel = provider.get_channel_whatsapp(vehicle.x_customer_id, self.env.user)
        print('channel', channel)
        # return False
        if not channel:
            raise UserError("No WhatsApp channel created.")
        # Render template
        body = template.body_html or template.body
        body = body.replace("{{1}}", str(vehicle.x_customer_id.name))
        body = body.replace("{{2}}", str(vehicle.x_vehicle_number_id))
        body = body.replace("{{3}}", str(vehicle.x_avg_km))

        print('body', body)
        print('vehicle.x_customer_id.id', vehicle.x_customer_id.id)
        msg_vals = {
            'body': tools.html2plaintext(body) if body else '',
            'author_id': self.env.user.partner_id.id,
            'model': 'vehicle.master.model',
            'res_id': vehicle.id,
            'message_type': 'wa_msgs',
            'isWaMsgs': True,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'partner_ids': [(4, vehicle.x_customer_id.id)],
        }
        print('msg_vals', msg_vals)

        msg = self.env['mail.message'].sudo().create(msg_vals)
        print('msg', msg)

        if channel and msg:
            channel._notify_thread(msg, msg_vals)
        else:
            _logger.warning("Skipped sending WhatsApp message — missing channel or msg record.")

    @api.model
    def _cron_tyre_service_wa_reminder(self):
        """Send reminder messages per vehicle based on configuration."""
        ir_config = self.env['ir.config_parameter'].sudo()
        km_limit = int(ir_config.get_param('tyreshop.tyre_message_km', default=5000))
        month_limit = int(ir_config.get_param('tyreshop.tyre_message_months', default=3))
        reminder_message_payment_days = int(ir_config.get_param('tyreshop.reminder_message_payment_days', default=3))

        print('system settings')
        print(km_limit, month_limit, reminder_message_payment_days)

        today = fields.Date.today()
        Vehicle = self.env['vehicle.master.model'].sudo()
        vehicles = Vehicle.search([('x_avg_km', '>', 0)])
        template = self.env['wa.template'].search([
            ('name', '=', 'reminder_service')
        ], limit=1)

        for vehicle in vehicles:
            # Get last date properly
            # c_data = template_id.description
            last_date = vehicle.last_wa_message_date
            # print('last_date', last_date)
            if not last_date and vehicle.create_date:
                # Convert datetime to date
                last_date = vehicle.create_date.date()
            elif not last_date:
                last_date = today
            days_since_last = (today - last_date).days
            months_since_last = days_since_last / 30.0
            monthly_avg = vehicle.x_avg_km  # Assuming this is "average km per month"
            expected_km = monthly_avg * months_since_last
            # Safe subtraction (both are datetime.date)
            days_diff = (today - last_date).days
            month_days = month_limit * 30
            km_due = vehicle.x_avg_km >= km_limit
            km_due = expected_km >= km_limit
            month_due = days_diff >= month_days
            month_due = months_since_last >= month_limit
            print('month_due')
            print(month_due)
            print('km_due')
            print(km_due)
            partner = vehicle.x_customer_id
            print('partner.mobile')
            print(partner.mobile)
            if not partner.mobile:
                raise ValidationError("Please update the mobile number before proceeding!")

            if km_due or month_due and partner.mobile:
                partner = vehicle.x_customer_id
                print('started a sending a msg to partner !!!!')
                print(vehicle.x_customer_id)
                print(partner)
                print(vehicle)
                x_avg_km = vehicle.x_avg_km
                message = (
                    f"Dear {partner.name}, Mobile Number {partner.mobile}, your vehicle ({vehicle.x_vehicle_number_id or partner_id.name}) "
                    f"has run {vehicle.x_avg_km} KM. It's time for a tyre service check!"
                )
                print('x_avg_km', x_avg_km)
                # vehicle_cron = self.env['tyre.service.reminder'].browse()
                partner.message_post(body=message)
                try:
                    # print('started debug 0', template)
                    # print('started debug 0', template.id)
                    # print('started  debug 1', vehicle)
                    # print('started debug 2', vehicle.id)
                    # print('vehicle_cron')
                    # # print(vehicle_cron)
                    # print('vehicle_cron')
                    self.send_whatsapp_service_reminder(template, vehicle)

                    vehicle.write({
                        'last_wa_message_date': today,
                    })

                    print("✅ WhatsApp reminder sent for vehicle service", vehicle.id)

                except Exception as e:
                    print("❌ ERROR:", e)
                    _logger.error("WhatsApp reminder failed for invoice %s: %s", vehicle.id, e)


class AccountMove(models.Model):
    _inherit = 'account.move'

    last_reminder_date = fields.Date(
        string="Last SMS Reminder Date",
        default=lambda self: fields.Date.today()
    )
    last_wa_message_date = fields.Date(
        string="Last Whatsapp Message Date",
        default=lambda self: fields.Date.today(),  # sets today's date at creation
    )

    reminder_count = fields.Integer(string="Reminder Count", default=0, readonly=True)

    @api.model
    def _cron_send_payment_reminder(self, account_type=2):
        """Send automatic payment reminders for overdue invoices"""
        ir_config = self.env['ir.config_parameter'].sudo()
        reminder_message_payment_days = int(ir_config.get_param('tyreshop.reminder_message_payment_days', default=3))
        today = date.today()
        # print('today', today)
        overdue_invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '!=', False),
            ('invoice_date_due', '<', today),
        ])
        print('overdue_invoices', overdue_invoices)
        for invoice in overdue_invoices:
            # Avoid spamming – send only once every 3 days
            last_reminder_date = invoice.last_reminder_date or date(1999, 1, 1)
            if last_reminder_date and (today - last_reminder_date).days < reminder_message_payment_days:
                print('ran')
                continue
            print('come in')
            partner = invoice.partner_id
            print('partner', partner)
            email_to = partner.email
            print('email_to', email_to)
            if not email_to:
                continue

            # Compose email
            subject = _("Payment Reminder for Invoice %s") % (invoice.name)
            body = f"""
            <p>Dear {partner.name},</p>
            <p>This is a kind reminder that invoice <b>{invoice.name}</b> 
            with an amount of <b>{invoice.amount_total} {invoice.currency_id.name}</b> 
            was due on <b>{invoice.invoice_date_due}</b>.</p>
            <p>Please make the payment at your earliest convenience.</p>
            <p>Thank you,<br/>
            {invoice.company_id.name}</p>
            """
            body1 = "Dear %partner.name%, This is a kind reminder that invoice %invoice.name% with an amount of %inv.amount% was due on %data%.Please make the payment at your earliest convenience.Thank you"

            # Send mail
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'email_from': invoice.company_id.email or self.env.user.email,
            }
            # print('mail_values', mail_values)
            # send Email
            # self.env['mail.mail'].create(mail_values).send()
            # create chatter acitivity
            partner.message_post(body=body)

            # Update reminder fields
            invoice.write({
                'last_reminder_date': today,
                'last_wa_message_date': today,
                'reminder_count': invoice.reminder_count + 1
            })
            print('invoice', invoice)
            template_id = self.env['custom.sms.templates'].browse(2)

            if invoice:
                aretx_sms_composer = self.env['aretx.sms.composer'].create({
                    'res_model': 'account.move',  # self.partner_id.id,
                    'log_date': datetime.datetime.now().strftime("%d%B%Y"),
                    'res_id': invoice.id,  # self.partner_id.id,
                    'number': partner.mobile,
                    'number_field_name': 'phone',
                    'partner_id': partner.id,
                    # 'vehicle_id': vehicle.id,
                    'template_id': template_id.id,
                    'title': template_id.name,
                    'content': body,
                    'recipient_single_number_itf': partner.mobile,
                    # 'vehicle_number': vehicle.x_vehicle_number_id,
                    'is_vehicle': 1,
                })
            else:
                continue
                # Send Message

            query = self.env['custom.sms.setting'].browse(1)
            c_data = template_id.description
            # Post message to chatter
            if c_data is not False and partner and '%partner.name%' in c_data:
                c_data = c_data.replace("%partner.name%", partner.name)
            if c_data is not False and '%invoice.name%' in c_data:
                c_data = c_data.replace("%invoice.name%", invoice.name)
            if c_data is not False and '%inv.amount%' in c_data:
                c_data = c_data.replace("%inv.amount%", str(invoice.amount_total))
            if c_data is not False and '%data%' in c_data:
                c_data = c_data.replace("%data%", str(invoice.invoice_date_due))

            print('c_data', c_data)

            print('query', query)
            query.ensure_one()
            clean_phone = partner.mobile.replace("+91", "").strip()
            clean_phone = partner.mobile.replace("+91", "").replace(" ", "").strip()

            print(clean_phone)
            if query:
                data = {}
                data[query.userid_map] = query.userid
                data[query.userid_password_map] = query.userpassword
                data[query.account_type_map] = account_type
                data[query.phonenumber_map] = clean_phone
                data[query.msg_map] = c_data
                data[query.gsm_map] = query.gsm_sendername
                print('data', data)

                response = requests.get(query.send_url, data)
                print('sms sent to partner.')
                print('response', response)
                print('response', response.text)
                # response = requests.get(query.balance_url, headers=REQUEST_CUSTOM_HEADER, data=request_data)
                error = ["Invalid Template", "Authentication Fail", "Invalid Sender ID",
                         'Error :- Object reference not set to an instance of an object.', "No Data Found"]
                if response.status_code == 200 and response.text not in error:
                    # save msg_id in sms_delivery_report table
                    vals_list = {}
                    vals_list['msg_id'] = response.text
                    print('datetime.datetime.now')
                    print(datetime.datetime.now().strftime("%d%m%y"))
                    print('datetime.datetime.now')
                    vals_list['log_date'] = datetime.datetime.now().strftime("%d %B %Y")
                    vals_list['delivery_status'] = 0  # datetime.datetime.now().strftime("%d%m%y")
                    # print('vals_list', vals_list)
                    aretx_sms_composer.write(vals_list)
                    # return True
                else:
                    aretx_sms_composer.write(
                        {'error_log_status': response.status_code, 'error_log_text': response.text})
                    # return True

    def send_whatsapp_payment_reminder(self, template, invoice):
        self.ensure_one()

        provider = template.provider_id
        print('provider',provider)
        return False
        if not provider:
            raise UserError("No WhatsApp provider configured.")

        channel = provider.get_channel_whatsapp(invoice.partner_id, self.env.user)

        if not channel:
            raise UserError("No WhatsApp channel created.")

        # Render template
        body = template.body_html or template.body
        body = body.replace("{{1}}", invoice.partner_id.name or "")
        body = body.replace("{{2}}", invoice.name or "")
        body = body.replace("{{3}}", str(invoice.amount_residual))
        body = body.replace("{{4}}", str(invoice.invoice_date_due or ""))

        msg_vals = {
            'body': tools.html2plaintext(body),
            'author_id': self.env.user.partner_id.id,
            'model': 'account.move',
            'res_id': invoice.id,
            'message_type': 'wa_msgs',
            'isWaMsgs': True,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'partner_ids': [(4, invoice.partner_id.id)],
        }

        # 🔥 This is the missing part
        ctx = {
            'provider_id': template.provider_id.id,
            'template_send': True,
            'active_model': 'account.move',
            'active_model_id': invoice.id,
            'partner_id': invoice.partner_id.id,
        }

        msg = self.env['mail.message'].sudo().with_context(ctx).create(msg_vals)

        channel._notify_thread(msg, msg_vals)

    def send_whatsapp_payment_reminder2(self, template, invoice):
        self.ensure_one()
        # print('template',template)
        # print('template.provider_id',template.provider_id)
        provider = template.provider_id
        # print('provider', provider)
        if not provider:
            raise UserError("No WhatsApp provider configured.")
        channel = provider.get_channel_whatsapp(invoice.partner_id, self.env.user)
        print('channel', channel)
        if not channel:
            raise UserError("No WhatsApp channel created.")

        # Render template
        body = template.body_html or template.body
        body = body.replace("{{1}}", invoice.partner_id.name)
        body = body.replace("{{2}}", invoice.name)
        body = body.replace("{{3}}", str(invoice.amount_residual))
        body = body.replace("{{4}}", str(invoice.invoice_date_due))
        print('body', body)
        msg_vals = {
            'body': tools.html2plaintext(body) if body else '',
            'author_id': self.env.user.partner_id.id,
            'model': 'account.move',
            'res_id': invoice.id,
            'message_type': 'wa_msgs',
            'isWaMsgs': True,
            'subtype_id': self.env.ref('mail.mt_comment').id,
            'partner_ids': [(4, invoice.partner_id.id)],
        }
        _logger.info('msg_vals', msg_vals)
        _logger.info(msg_vals)
        print('msg_vals', msg_vals)

        msg = self.env['mail.message'].sudo().create(msg_vals)
        print('msg', msg)

        channel._notify_thread(msg, msg_vals)

    @api.model
    def _cron_send_payment_wa_reminder(self):
        ir_config = self.env['ir.config_parameter'].sudo()
        reminder_message_payment_days = int(ir_config.get_param('tyreshop.reminder_message_payment_days', default=3))
        today = date.today()
        overdue_invoices = self.search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            ('invoice_date_due', '<', today),
        ])
        # print('overdue_invoices.......', overdue_invoices)
        template = self.env['wa.template'].search([
            ('name', '=', 'reminder_payment')
        ], limit=1)

        for invoice in overdue_invoices:
            # print('invoice.......', invoice)
            # print('today', today)
            # print('invoice.last_reminder_date', invoice.last_reminder_date)
            # Skip if reminder was sent recently
            last_reminder_date = invoice.last_wa_message_date or date(1999, 1, 1)
            print('last_reminder_date', last_reminder_date)
            if last_reminder_date and (today - last_reminder_date).days < reminder_message_payment_days:
                continue

            try:
                print('started invoice', invoice)
                invoice.send_whatsapp_payment_reminder(template, invoice)

                invoice.write({
                    # 'last_reminder_date': today,
                    'last_wa_message_date': today,
                    'reminder_count': invoice.reminder_count + 1
                })

                print("✅ WhatsApp reminder sent for invoice", invoice.id)

            except Exception as e:
                print("❌ ERROR:", e)
                _logger.error("WhatsApp reminder failed for invoice %s: %s", invoice.id, e)
