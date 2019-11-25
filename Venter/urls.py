from django.urls import path
from Venter.views import FileViewSet, ModelKMView, WCView, ModelSMView
from django.views.generic import TemplateView

urlpatterns = [
    # ex: /venter/
    path('', TemplateView.as_view(template_name='Venter/home.html'), name='home'),
    # ex: /venter/home/
    path('home/', TemplateView.as_view(template_name='Venter/home.html'), name='home'),
    # ex: /venter/file
    path('file', FileViewSet.as_view({
        'get': 'list'
    })),
    # ex: /venter/file/XYZ
    path('file/<organisation>', FileViewSet.as_view({
        'get': 'retrieve'
    })),
    # ex: /venter/modelKM
    path('modelKM', ModelKMView.as_view()),

    # ex: /venter/modelWC
    path('modelWC', WCView.as_view()),

    # ex: /venter/modelSM
    path('modelSM', ModelSMView.as_view()),
]
