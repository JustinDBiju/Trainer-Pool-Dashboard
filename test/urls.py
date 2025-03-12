from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from crm.views import feedback_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('crm/', include('crm.urls')),
    path('feedback/', feedback_list, name='feedback'),
    path('', RedirectView.as_view(url='crm/login/')),  # Redirect root URL to login page
]