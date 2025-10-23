from odoo import models, api, fields
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import requests
import datetime
from odoo.http import request
from odoo import api, fields, models, _
from datetime import date, timedelta
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError



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
            data[query.phonenumber_map] = partner.phone
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
            if not partner.phone:
                raise ValidationError("Please update the phone number before proceeding!")

            if km_due or month_due and partner.phone:
                partner = vehicle.x_customer_id
                print('started a sending a msg to partner !!!!')
                print(vehicle.x_customer_id)
                print(partner)
                print(vehicle)
                x_avg_km = vehicle.x_avg_km
                message = (
                    f"Dear {partner.name}, Phone Number {partner.phone}, your vehicle ({vehicle.x_vehicle_number_id or partner_id.name}) "
                    f"has run {vehicle.x_avg_km} KM. It's time for a tyre service check!"
                )
                print('x_avg_km', x_avg_km)

                # Post message to chatter
                if c_data is not False and partner and '%partner_name%' in c_data:
                    c_data = c_data.replace("%partner_name%", partner.name)
                # print('c_data', c_data)
                # print('partner', partner.phone)
                # if c_data is not False and '%partner_phone%' in c_data:
                #     c_data = c_data.replace("%partner_phone%", partner.phone)

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
                        'number': partner.phone,
                        'number_field_name': 'phone',
                        'partner_id': partner.id,
                        'vehicle_id': vehicle.id,
                        'template_id': template_id.id,
                        'title': template_id.name,
                        'content': c_data,
                        'recipient_single_number_itf': partner.phone,
                        'vehicle_number': vehicle.x_vehicle_number_id,
                        'is_vehicle': 1,
                    })
                else:
                    aretx_sms_composer = self.env['aretx.sms.composer'].create({
                        'res_model': 'vehicle.master.model',  # self.partner_id.id,
                        'res_id': vehicle,  # self.partner_id.id,
                        'number': partner.phone,
                        'number_field_name': 'phone',
                        'partner_id': partner.id,
                        'template_id': template_id.id,
                        'title': template_id.name,
                        'content': c_data,
                        # 'recipient_single_number_itf': partner.phone,
                    })
                query = self.env['custom.sms.setting'].browse(1)
                print('query', query)
                query.ensure_one()
                clean_phone = partner.phone.replace("+91", "").strip()
                clean_phone = partner.phone.replace("+91", "").replace(" ", "").strip()

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


class AccountMove(models.Model):
    _inherit = 'account.move'

    last_reminder_date = fields.Date(string="Last Reminder Date")
    reminder_count = fields.Integer(string="Reminder Count", default=0, readonly=True)

    @api.model
    def _cron_send_payment_reminder(self, account_type=2):
        """Send automatic payment reminders for overdue invoices"""
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
            if invoice.last_reminder_date and (today - invoice.last_reminder_date).days < 3:
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
                'reminder_count': invoice.reminder_count + 1
            })
            print('invoice', invoice)
            template_id = self.env['custom.sms.templates'].browse(2)

            if invoice:
                aretx_sms_composer = self.env['aretx.sms.composer'].create({
                    'res_model': 'account.move',  # self.partner_id.id,
                    'log_date': datetime.datetime.now().strftime("%d%B%Y"),
                    'res_id': invoice.id,  # self.partner_id.id,
                    'number': partner.phone,
                    'number_field_name': 'phone',
                    'partner_id': partner.id,
                    # 'vehicle_id': vehicle.id,
                    'template_id': template_id.id,
                    'title': template_id.name,
                    'content': body,
                    'recipient_single_number_itf': partner.phone,
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
            clean_phone = partner.phone.replace("+91", "").strip()
            clean_phone = partner.phone.replace("+91", "").replace(" ", "").strip()

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
