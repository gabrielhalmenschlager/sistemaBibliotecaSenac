from django.urls import path
from biblioteca.views import (
    # Livros, reservas, empréstimos
    LivroListView, LivroDetailView, LivroCreateView,
    ReservaCreateView, ReservaListView, ReservaCancelView,
    EmprestimoListView, EmprestimoCreateView, EmprestimoDevolverView,

    # Autores
    AutorListView, AutorDetailView,
    AutorCreateView, AutorUpdateView, AutorDeleteView,
)

urlpatterns = [
    # ---------------- Livros ----------------
    path('', LivroListView.as_view(), name='livro-lista'),
    path('livro/novo/', LivroCreateView.as_view(), name='livro-criar'),
    path('livro/<int:pk>/', LivroDetailView.as_view(), name='livro-detalhe'),

    # Reservas
    path('livro/<int:pk>/reservar/', ReservaCreateView.as_view(), name='reserva-criar'),
    path('reservas/', ReservaListView.as_view(), name='reserva-lista'),
    path('reserva/<int:pk>/cancelar/', ReservaCancelView.as_view(), name='reserva-cancelar'),

    # Empréstimos
    path('emprestimos/', EmprestimoListView.as_view(), name='emprestimo-lista'),
    path('livro/<int:pk>/emprestar/', EmprestimoCreateView.as_view(), name='emprestimo-criar'),
    path('emprestimo/<int:pk>/devolver/', EmprestimoDevolverView.as_view(), name='emprestimo-devolver'),

    # ---------------- Autores ----------------
    path('autores/', AutorListView.as_view(),   name='autor-lista'),
    path('autor/novo/', AutorCreateView.as_view(),  name='autor-criar'),        # apenas admin
    path('autor/<int:pk>/', AutorDetailView.as_view(), name='autor-detalhe'),
    path('autor/<int:pk>/editar/', AutorUpdateView.as_view(), name='autor-editar'),   # apenas admin
    path('autor/<int:pk>/excluir/', AutorDeleteView.as_view(), name='autor-excluir'), # apenas admin
]
