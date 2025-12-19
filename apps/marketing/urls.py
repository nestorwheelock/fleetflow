from django.urls import path
from . import views

app_name = 'marketing'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('features/', views.FeaturesView.as_view(), name='features'),
    path('search/', views.RentalSearchView.as_view(), name='rental-search'),
    path('api/lead/', views.LeadCaptureView.as_view(), name='lead-capture'),
    path('api/referral/', views.ReferralView.as_view(), name='referral'),
]
