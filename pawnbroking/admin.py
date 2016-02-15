from django.contrib import admin
from django import forms
from pawnbroking.models import PledgedItem, Redemption, Pledge, Customer, \
    DailyBalanceSheet, Ornament, PersonName, City, NoticeTemplate, AuctionNotice,\
    AuctionNoticeAndPledgeMap
import autocomplete_light
import datetime

class PledgedItemInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        # get forms that actually have valid data
        count = 0
        for form in self.forms:
            try:
                if form.cleaned_data:
                    count += 1
            except AttributeError:
                # annoyingly, if a subform is invalid Django explicity raises
                # an AttributeError for cleaned_data
                pass
        if count < 1:
            raise forms.ValidationError('We must have at least one pledged item')

class PledgedItemInline(admin.TabularInline):
    form = autocomplete_light.modelform_factory(PledgedItem)
    model = PledgedItem
    exclude = ['pledge_particulars']
    extra = 3
    formset = PledgedItemInlineFormset
    
class RedemptionInline(admin.TabularInline):
    model = Redemption
    extra = 0
    max_num = 1
    
class AuctionNoticeAndPledgeMapInline(admin.TabularInline):
    model = AuctionNoticeAndPledgeMap
    extra = 0
    can_delete = False
    exclude = ['pledge_notice', 'pledge']
    
    def has_add_permission(self, request):
        return False
    
class PledgeAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Pledge)
    actions = None
    inlines = [PledgedItemInline, RedemptionInline]
    fields = (('pledge_no', 'loan_date'), 'principle', 'name', 'father_or_husband_name', 'town', 'net_weight', ('advance_interest', 'document'))
    readonly_fields = ('advance_interest', 'document')
    list_display = ('pledge_no', 'loan_date', 'name', 'father_or_husband_name', 'town', 'principle', 'net_weight')
    list_filter = ['loan_date', 'status']
    list_per_page = 25
    ordering = ['-loan_date', '-id']
    search_fields = ['pledge_no', 'name__name', 'father_or_husband_name__name', 'town__name', 'principle']
    date_hierarchy = 'loan_date'
    
    # TODO: Should be changed to 'get_formsets_with_inlines from Django 1.7'
    def get_formsets(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            # hide MyInline in the add view
            if isinstance(inline, RedemptionInline) and obj is None:
                continue
            yield inline.get_formset(request, obj)
            
    def get_form(self, request, obj=None, **kwargs):
        form = super(PledgeAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            latest_pledge = Pledge.objects.latest('id')
            form.base_fields['loan_date'].initial = latest_pledge.loan_date

            next_pledge_no = None
            pledge_no = latest_pledge.pledge_no
            if pledge_no.isdigit():
                next_pledge_no = int(float(pledge_no)) + 1
            else:
                next_pledge_no = int(float(pledge_no[1:])) + 1
                if next_pledge_no > 10000:
                    next_pledge_no = chr(ord(pledge_no[0]) + 1) + '1'
                else:
                    next_pledge_no = pledge_no[0] + str(next_pledge_no)
            
            form.base_fields['pledge_no'].initial = str(next_pledge_no)
        return form
            
admin.site.register(Pledge, PledgeAdmin)

class RedemptionAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(Redemption)
    actions_on_top = False
    actions_on_bottom = True
    list_display = ('pledge_no', 'pledge_customer_name', 'pledge_loan_date', 'pledge_principle', 'date', 'interest', 'total')
    list_filter = ['date']
    list_per_page = 25
    ordering = ['-date', '-id']
    search_fields = ['pledge__pledge_no', 'pledge__name__name', 'pledge__father_or_husband_name__name', 'pledge__town__name']
    date_hierarchy = 'date'
    readonly_fields = ('interest', 'misc', 'total')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super(RedemptionAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            latest_redemption = Redemption.objects.latest('id')
            form.base_fields['date'].initial = latest_redemption.date
        return form
    
admin.site.register(Redemption, RedemptionAdmin)

class CustomerAdmin(admin.ModelAdmin):
    actions = None
    form = autocomplete_light.modelform_factory(Customer)
    fields = ('name', 'father_or_husband_name', 'address', 'town')
    list_display = ('name', 'father_or_husband_name', 'town')
    list_per_page = 25
    ordering = ['town__name', 'name__name', 'father_or_husband_name__name']
    search_fields = ['name__name', 'father_or_husband_name__name', 'town__name']
    date_hierarchy = 'created'
    list_filter = ['created']
admin.site.register(Customer, CustomerAdmin)

class DailyBalanceSheetAdmin(admin.ModelAdmin):
    actions = None
    fields = ('date', ('previous_balance', 'credit'), ('pledged_principle', 'redempted_advance_interest', 'document_charges'), 'total_pledged_amount', ('redempted_principle', 'redempted_interest', 'redempted_misc_charges'), 'total_redempted_amount', 'misc_debit', 'amount_in_hand', 'remarks')
    readonly_fields = ('pledged_principle', 'redempted_advance_interest', 'document_charges', 'total_pledged_amount', 'redempted_principle', 'redempted_interest', 'total_redempted_amount')
    list_display = ('date', 'pledged_principle', 'total_pledged_amount', 'redempted_principle', 'total_redempted_amount', 'misc_debit', 'previous_balance', 'amount_in_hand')
    list_filter = ['date']
    list_per_page = 25
    ordering = ['-date']
    search_fields = ['date']
    date_hierarchy = 'date'
admin.site.register(DailyBalanceSheet, DailyBalanceSheetAdmin)

class OrnamentAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 25
    ordering = ['name']
admin.site.register(Ornament, OrnamentAdmin)

class PersonNameAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_per_page = 25
    ordering = ['name']
admin.site.register(PersonName, PersonNameAdmin)

class CityAdmin(admin.ModelAdmin):
    form = autocomplete_light.modelform_factory(City)
    list_display = ('name', 'pincode', 'post')
    list_per_page = 25
    ordering = ['name']
    search_fields = ['name', 'pincode']
admin.site.register(City, CityAdmin)

class NoticeTemplateAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_per_page = 25
    ordering = ['name']
admin.site.register(NoticeTemplate, NoticeTemplateAdmin)

# class AuctionNoticeAdmin(AutocompleteModelAdmin):
class AuctionNoticeAdmin(admin.ModelAdmin):
    list_display = ('from_date', 'to_date', 'notice_type', 'grace_date', 'no_of_pledges', 'no_of_customers')
    fields = (('from_date', 'to_date'), ('notice_type', 'cost', 'grace_date'))
    search_fields = ['notice__type']
    list_per_page = 25
    ordering = ['-created']
    date_hierarchy = 'created'    
    list_filter = ['created']
#     related_search_fields = { 
#             'notice_type': ('name',),
#         }

    def get_form(self, request, obj=None, **kwargs):
        form = super(AuctionNoticeAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            grace_date = datetime.datetime.today() + datetime.timedelta(days = 30)
            if grace_date.weekday() == 6: # If Sunday, Change it to Monday...
                grace_date = grace_date + datetime.timedelta(days = 1)

            form.base_fields['grace_date'].initial = grace_date
        return form

admin.site.register(AuctionNotice, AuctionNoticeAdmin)
