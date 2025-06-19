"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# myproject/urls.py
# myproject/urls.py
from django.contrib import admin
from django.urls import path
from EldenRingInsider import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.item_list, name='item_list'),  # Root path for the item list
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('builds/', views.builds_view, name='builds'),
    path('get_items/', views.get_items, name='get_items'),
    path('save_item_to_build/', views.save_item_to_build, name='save_item_to_build'),
    path('items/<int:item_id>/json/', views.item_json_view, name='item_json'), # For preview items on builds

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

