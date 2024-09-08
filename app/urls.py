
from django.contrib import admin
from django.urls import path
from wallify.views import homepage
from wallify.views import about
from wallify import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', homepage, name='homepage'),
    path('about/', about, name='about'),
    path('signin/',views.signin, name='signin'),
    path('signout/',views.signout, name='signout'),
    path('signup/',views.signup, name='signup'),
    path('profile/',views.profile, name='profile'),
    path('profile/<str:username>/', views.profile, name='profile_other'),  # For viewing other users' profiles
    # path('profile/<str:username>/', views.profile, name='profile'),
    path('profile_picture/<int:user_id>/', views.serve_profile_picture, name='serve_profile_picture'),
    path('profile-picture/<str:username>/', views.get_profile_picture, name='get_profile_picture'),
    path('gallery/',views.gallery, name='gallery'),
    # path('search/',views.search, name='search'),
    path('upload_image/', views.upload_image, name='upload_image'),
    # path('update_pfp/', views.update_pfp, name='update_pfp')
     path('delete_favorite_image/', views.delete_favorite_image, name='delete_favorite_image'),
    path('generate-image/', views.generate_image, name='generate_image'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL , document_root = settings.STATIC_ROOT)