from django.urls import path
from .views import (ESLoginView, ESLogoutView, ProfileEditView,
                    PassportEditView, RegisterView, RegisterDoneView,
                    ProfileDeleteView,
                    profile, index, other_page, user_activate,
                    rubric_ess, es_detail, profile_es_detail, profile_es_add,
                    profile_es_edit, profile_es_delete)


app_name = 'main'
urlpatterns = [
    path('accounts/activate/<str:sign>/', user_activate, name='activate'),
    path('accounts/register/done', RegisterDoneView.as_view(),
         name='register_done'),
    path('accounts/register/', RegisterView.as_view(),
         name='register'),
    path('accounts/login/', ESLoginView.as_view(), name='login'),
    path('accounts/logout/', ESLogoutView.as_view(), name='logout'),
    path('accounts/password/edit/', PassportEditView.as_view(),
         name='password_edit'),
    path('accounts/profile/delete/', ProfileDeleteView.as_view(),
         name='profile_delete'),
    path('accounts/profile/edit', ProfileEditView.as_view(),
         name='profile_edit'),
    path('accounts/profile/edit/<int:pk>/', profile_es_edit,
         name='profile_es_edit'),
    path('accounts/profile/delete/<int:pk>/', profile_es_delete,
         name='profile_es_delete'),
    path('accounts/profile/add/', profile_es_add, name='profile_es_add'),
    path('accounts/profile/<int:pk>/', profile_es_detail,
         name='profile_es_detail'),
    path('accounts/profile/', profile, name='profile'),
    path('<int:rubric_pk>/<int:pk>/', es_detail, name='rubric_ess'),
    path('<int:pk>/', rubric_ess, name='rubric_ess'),
    path('<str:page>/', other_page, name='other'),
    path('', index, name='index'),
]