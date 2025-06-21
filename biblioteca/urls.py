from django.urls import path
from biblioteca.views import (
    LivroListView, LivroDetailView, ReservaCreateView, ReservaListView, ReservaCancelView,
    EmprestimoListView, EmprestimoCreateView, EmprestimoDevolverView, LivroCreateView
)

urlpatterns = [
    path('', LivroListView.as_view(), name='livro-lista'),
    path('livro/novo/', LivroCreateView.as_view(), name='livro-criar'),
    path('livro/<int:pk>/', LivroDetailView.as_view(), name='livro-detalhe'),

    path('livro/<int:pk>/reservar/', ReservaCreateView.as_view(), name='reserva-criar'),
    path('reservas/', ReservaListView.as_view(), name='reserva-lista'),
    path('reserva/<int:pk>/cancelar/', ReservaCancelView.as_view(), name='reserva-cancelar'),

    path('emprestimos/', EmprestimoListView.as_view(), name='emprestimo-lista'),
    path('livro/<int:pk>/emprestar/', EmprestimoCreateView.as_view(), name='emprestimo-criar'),
    path('emprestimo/<int:pk>/devolver/', EmprestimoDevolverView.as_view(), name='emprestimo-devolver'),
]
