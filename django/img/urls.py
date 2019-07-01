from django.urls import path
from img.views import *

# comon_prefix: 'img/'
app_name = 'img'
urlpatterns = [
    path('upload_image/', upload_image, name='upload_image'),
    path('list/<int:img_id>/', ImageListView.as_view(), name='list_image'),
]
