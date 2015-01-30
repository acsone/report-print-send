# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Guewen Baconnier
#    Copyright 2014 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, exceptions, _


class Report(models.Model):
    _inherit = 'report'

    def _can_send_report(self, cr, uid, ids, behaviour, printer, document,
                         context=None):
        """Predicate that decide if report can be sent to printer

        If you want to prevent `get_pdf` to send report you can set
        the `must_skip_sent_to_printer` key to True in the context
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        if context.get('must_skip_sent_to_printer'):
            return False
        if behaviour['action'] == 'server' and printer and document:
            return True
        return False

    def print_document(self, cr, uid, ids, report_name, html=None,
                       data=None, context=None):
        """ Print a document, do not return the document file """
        document = self.get_pdf(cr, uid, ids, report_name,
                                html=html, data=data, context=context)
        report = self._get_report_from_name(cr, uid, report_name)
        behaviour = report.behaviour()[report.id]
        printer = behaviour['printer']
        if not printer:
            raise exceptions.Warning(
                _('No printer configured to print this report.')
            )
        return printer.print_document(report, document, report.report_type)

    def get_pdf(self, cr, uid, ids, report_name, html=None,
                data=None, context=None):
        """ Generate a PDF and returns it.

        If the action configured on the report is server, it prints the
        generated document as well.
        """
        if context is None:
            context = self.pool['res.users'].context_get(cr, uid)
        document = super(Report, self).get_pdf(cr, uid, ids, report_name,
                                               html=html, data=data,
                                               context=context)
        report = self._get_report_from_name(cr, uid, report_name)
        behaviour = report.behaviour()[report.id]
        printer = behaviour['printer']
        can_send_report = self._can_send_report(cr, uid, ids,
                                                behaviour, printer, document,
                                                context=context)
        if can_send_report:
            sent = printer.print_document(report, document, report.report_type)
            context['must_skip_sent_to_printer'] = True
            return sent
        return document
