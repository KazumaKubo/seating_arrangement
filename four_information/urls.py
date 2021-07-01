from django.urls import path
from .views import Main, DisplaySeat, seat_arrange, save_seat_history, SeatHistoryView, PrintSeat, \
    DisplayPrioritySeat, DisplayStudentWeight

urlpatterns = [
    path('', Main.as_view(), name="Main"),
    path('result/', DisplaySeat.as_view(), name='Result'),
    path('loading/', seat_arrange, name='Arrange'),
    path('save-db/', save_seat_history, name='SaveDB'),
    path('history/<int:pk>', SeatHistoryView.as_view(), name='SeatHistory'),
    path('print/<int:pk>', PrintSeat.as_view(), name='PrintSeat'),
    path('priority-seat/', DisplayPrioritySeat.as_view(), name='Priority'),
    path('weight/', DisplayStudentWeight.as_view(), name='Weight')
]
