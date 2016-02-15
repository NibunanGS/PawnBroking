'''
Created on Oct 1, 2013

@author: nibunan
'''
import autocomplete_light
from pawnbroking.models import PersonName, City, Ornament, Pledge

autocomplete_light.register(PersonName, search_fields=['^name'], autocomplete_js_attributes={'placeholder': ''})
autocomplete_light.register(City, search_fields=['^name'], autocomplete_js_attributes={'placeholder': ''})
autocomplete_light.register(Ornament, search_fields=['^name'], autocomplete_js_attributes={'placeholder': ''})
autocomplete_light.register(Pledge, search_fields=['^pledge_no'], autocomplete_js_attributes={'placeholder': 'Pledge_No'})