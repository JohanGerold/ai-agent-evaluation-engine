from django.urls import path

from app.foundation import views

urlpatterns = [path("health/live", views.live), path("health/ready", views.ready)]
handler400 = "app.foundation.views.bad_request"
handler403 = "app.foundation.views.permission_denied"
handler404 = "app.foundation.views.not_found"
handler500 = "app.foundation.views.server_error"
