from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.dashboard.views import DashboardSummaryView
from apps.equipment.views import EquipmentViewSet
from apps.labs.views import LaboratoryViewSet
from apps.loans.views import LoanViewSet
from apps.reservations.views import ReservationViewSet
from apps.users.views import CurrentUserView, LoginView, LogoutView, RegisterView

router = DefaultRouter()
router.register("laboratorios", LaboratoryViewSet, basename="laboratorios")
router.register("equipos", EquipmentViewSet, basename="equipos")
router.register("reservas", ReservationViewSet, basename="reservas")
router.register("prestamos", LoanViewSet, basename="prestamos")

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/auth/login/", LoginView.as_view(), name="auth-login"),
    path("api/auth/registro/", RegisterView.as_view(), name="auth-register"),
    path("api/auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("api/auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("api/auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("api/dashboard/summary/", DashboardSummaryView.as_view(), name="dashboard-summary"),
    path("api/", include(router.urls)),
]
