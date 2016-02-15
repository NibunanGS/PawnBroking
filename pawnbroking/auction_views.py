'''
Created on Jun 22, 2014

@author: nibunan
'''
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponse
from mybusiness.formats.en import formats
from pawnbroking.models import Pledge, Customer
import simplejson as json
import time
from datetime import datetime
from django.template import loader
from django.template.context import Context
from django.template.loader import get_template
import StringIO
from cgi import escape
from xhtml2pdf import pisa
from django.utils.datastructures import SortedDict
from reportlab.platypus import frames

@login_required
def get_pledges_for_auction(request):
    from_date_str = dict(request.GET.iterlists())['from_date'][0]
    from_date = __parse_str_to_date(from_date_str)
    
    to_date_str = dict(request.GET.iterlists())['to_date'][0]
    to_date = __parse_str_to_date(to_date_str)
    
    pledge_responses = []
    if from_date < to_date:
        pledges = Pledge.objects.filter(status='Open', loan_date__range=(from_date, to_date)).order_by('loan_date', 'id')
        
        cust_id_vs_pledges = dict()
        dateformat = formats.DATE_INPUT_FORMATS[0]
        for i, p in enumerate(pledges):
            pledge_responses.append({'pledge_no':p.pledge_no, 'loan_date':p.loan_date.strftime(dateformat), 'principle':p.principle, 'name':p.name.name,
                                    'father_or_husband_name':p.father_or_husband_name.name, 'town':p.town.name, 'address':p.customer.address,
                                    'cust_id':p.customer.id})
            cust_id_vs_pledges.setdefault(p.customer.id, list()).append({'pledge_no':p.pledge_no, 'loan_date':p.loan_date.strftime(dateformat), 'principle':p.principle, "net_weight":p.net_weight,'index': i})
        
        for pledge_response in pledge_responses:
            pledge_response['pledges'] = cust_id_vs_pledges[pledge_response['cust_id']]
            pledge_response['related'] = pledge_response['pledges'].__len__() - 1  
    
    response = {'no_of_customers':cust_id_vs_pledges.__len__(), 'pledges':pledge_responses}
    return HttpResponse(json.dumps(response))

def __parse_str_to_date(date_str):
    for f in formats.DATE_INPUT_FORMATS:
        try:
            strptime = time.strptime(date_str, f)
            return datetime.fromtimestamp(time.mktime(strptime))
        except ValueError:
            continue
    else:
        raise ValueError('Unable to parse the given date', date_str)

@login_required
def save_customer_address(request):
    cust_id_str = request.POST.get('cust_id')
    cust_id = int(cust_id_str)
    
    address_to_be_saved = request.POST.get('address')
    
    customer = Customer.objects.get(id = cust_id)
    customer.address = address_to_be_saved
    customer.save()
    
    return HttpResponse(json.dumps({'aSDSC':"Success"}))

@login_required
def generate_auction_notice(request):
    from_date_str = request.POST.get('from_date')
    from_date = __parse_str_to_date(from_date_str)
    
    to_date_str = request.POST.get('to_date')
    to_date = __parse_str_to_date(to_date_str)
    
    grace_date_str = request.POST.get('grace_date')
    
    cust_and_pledges = __get_cust_and_pledges(from_date, to_date);
    return __render_to_pdf('default_notice_letter.html', 
                           {'cust_and_pledges': cust_and_pledges,
                            'notice_date': time.strftime(formats.DATE_INPUT_FORMATS[0]),
                            'grace_date':grace_date_str,
                            })
    
def __get_cust_and_pledges(from_date, to_date):
    pledges = Pledge.objects.filter(status='Open', loan_date__range=(from_date, to_date)).order_by('loan_date', 'id')
    
    cust_vs_pledges = SortedDict()
    dateformat = formats.DATE_INPUT_FORMATS[0]
    for p in pledges:
        cust_vs_pledges.setdefault(p.customer, list()).append({'pledge_no':p.pledge_no, 'loan_date':p.loan_date.strftime(dateformat), 'principle':p.principle})
    
    return cust_vs_pledges
    
def __render_to_pdf(template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    
#   To get around the ReportLabs border issue in 3.1.8  
    frames.ShowBoundaryValue.__nonzero__ = frames.ShowBoundaryValue.__bool__

    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("utf-8")), result)
    
    if not pdf.err:
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Notices_'+datetime.now().strftime(formats.DATE_INPUT_FORMATS[0])+'.pdf"'
        return response
    
    return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))
    
