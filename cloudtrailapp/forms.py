from django import forms


class DateRangeForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    UserName = forms.CharField(max_length=50, required=False)
    EventName = forms.CharField(max_length=50, required=False)
    ResourceType = forms.CharField(max_length=50, required=False)
    ResourceName = forms.CharField(max_length=50, required=False)
    RequestParameters = forms.CharField(max_length=2000, required=False)
