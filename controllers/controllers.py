# -*- coding: utf-8 -*-
from odoo import http
from ..services.api import Jira
from odoo.http import request
from odoo import fields
from ..services.utils import to_UTCtime
import datetime
import pytz
from ..services.datahandler import DataHandler

from odoo.addons.web.controllers.main import Home
class HomeExtend(Home):


    @http.route('/web/login',type='http', auth="none", sitemap=False)
    def web_login(self, redirect=None, **kw):
        if request.httprequest.method == 'POST':

            JiraAPI = Jira()

            credentials = {
                'username' : request.params['login'],
                'password' : request.params['password']
            }

            httpResponse = JiraAPI.authentication(credentials)

            if httpResponse.status_code == 200:
                userDB = request.env['res.users'].sudo().with_context(active_test=False)

                currentUser = userDB.search([('login', '=', request.params['login'])])

                user_data_on_jira = JiraAPI.get_user(request.params['login'])

                user_timezone = user_data_on_jira["timeZone"]

                user_display_name = user_data_on_jira["displayName"]

                #If user not exist,creat one
                if not currentUser:
                    user = {
                        'name' : user_display_name,
                        'login' : request.params['login'],
                        'active': True,
                        'employee' : True,
                        'employee_ids': [(0, 0, {'name': user_display_name})],
                    }
                    currentUser = request.env.ref('base.default_user').sudo().copy(user)

                # Always update jira password each login time
                currentUser.sudo().write({'password': request.params['password'],
                                          'authorization': JiraAPI.getToken(),
                                          'tz': user_timezone})

                dataHandler = DataHandler(request.params['login'])

                dataHandler.sync_data_from_jira()

                request.env.cr.commit()

        response = super().web_login(redirect, **kw)

        return response

