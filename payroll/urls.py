from django.urls import path

from . import views

urlpatterns = [
    path("schedules/create/", views.create_schedule),
    path("schedules/", views.list_schedules),
    path("schedules/<int:schedule_id>/toggle/", views.toggle_schedule),
    path("runs/", views.list_runs),
    path("runs/create/", views.create_run),
    path("runs/createInstant/", views.create_run),
    path("runs/<int:run_id>/commit/", views.commit_run),
    path("runs/<int:run_id>/claims/", views.list_run_claims),
    path("runs/<int:run_id>/tx/createPayroll/", views.tx_create_payroll),
    path("runs/<int:run_id>/tx/fundPlan/", views.tx_fund_plan),
    path("runs/<int:run_id>/open/", views.open_run),
    path("claims/<int:payroll_id>/<str:wallet>/", views.get_claim),
    path("runs/<int:run_id>/recordTx/", views.record_run_tx),
    path("claims/<int:run_id>/<int:index>/recordTx/", views.record_claim_tx),
]
