from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Q

from biblioteca.models import Livro, Autor, Reserva, Emprestimo
from .forms import LivroForm, AutorForm

from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Count, Prefetch

class LivroCreateView(generic.View):  # removi LoginRequiredMixin para deixar aberto a todos
    def get(self, request):
        form = LivroForm()
        return render(request, 'livros/livro_form.html', {'form': form})

    def post(self, request):
        form = LivroForm(request.POST, request.FILES)
        if form.is_valid():
            livro = form.save(commit=False)
            livro.save()

            # autores_texto deve ser uma lista de nomes separados (ex: no form, transforme a string em lista)
            nomes_autores = form.cleaned_data.get('autores_texto', [])
            autores_objs = []
            for nome in nomes_autores:
                nome = nome.strip()
                if nome:
                    autor, created = Autor.objects.get_or_create(nome=nome)
                    autores_objs.append(autor)

            livro.autores.set(autores_objs)
            livro.save()

            messages.success(request, 'Livro cadastrado com sucesso!')
            return redirect('livro-lista')

        return render(request, 'livros/livro_form.html', {'form': form})


class LivroListView(generic.ListView):
    model = Livro
    template_name = 'livros/lista.html'
    context_object_name = 'livros'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        queryset = Livro.objects.all().prefetch_related('autores')
        if query:
            queryset = queryset.filter(
                Q(titulo__icontains=query) |
                Q(autores__nome__icontains=query) |
                Q(genero__icontains=query)
            ).distinct()
        return queryset


class LivroDetailView(generic.DetailView):
    model = Livro
    template_name = 'livros/detalhe.html'
    context_object_name = 'livro'


class ReservaCreateView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        usuario = request.user

        reserva = Reserva(livro=livro, usuario=usuario)
        try:
            reserva.save()
            messages.success(request, f'Reserva do livro "{livro.titulo}" feita com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao reservar: {str(e)}')

        return redirect('livro-detalhe', pk=pk)


class ReservaListView(LoginRequiredMixin, generic.ListView):
    model = Reserva
    template_name = 'reservas/lista.html'
    context_object_name = 'reservas'

    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user, ativa=True).select_related('livro')


class ReservaCancelView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        reserva = get_object_or_404(
            Reserva, pk=pk, usuario=request.user, ativa=True
        )
        reserva.cancelar()
        messages.success(
            request,
            f'Reserva do livro “{reserva.livro.titulo}” cancelada com sucesso.'
        )
        return redirect('reserva-lista')

class EmprestimoListView(LoginRequiredMixin, generic.ListView):
    model = Emprestimo
    template_name = 'emprestimos/lista.html'
    context_object_name = 'emprestimos'

    def get_queryset(self):
        return Emprestimo.objects.filter(usuario=self.request.user, devolvido=False).select_related('livro')


class EmprestimoCreateView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        livro = get_object_or_404(Livro, pk=pk)
        usuario = request.user
        emprestimo = Emprestimo(livro=livro, usuario=usuario)
        try:
            emprestimo.save()
            messages.success(request, f'Empréstimo do livro "{livro.titulo}" realizado com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao emprestar: {str(e)}')
        return redirect('livro-detalhe', pk=pk)


class EmprestimoDevolverView(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        emprestimo = get_object_or_404(Emprestimo, pk=pk, usuario=request.user, devolvido=False)
        emprestimo.devolver()
        messages.success(request, f'Livro "{emprestimo.livro.titulo}" devolvido com sucesso!')
        return redirect('emprestimo-lista')

# ----------------------------
# Permissão: apenas admins
# ----------------------------
class SomenteAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.tipo == 'admin'


# ----------------------------
# Autores - Visualização
# ----------------------------
class AutorListView(generic.ListView):
    model = Autor
    template_name = 'autores/lista.html'  # ou o nome correto
    context_object_name = 'autores'
    paginate_by = 12  # ou o número que estiver usando

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(nome__icontains=q)
        return queryset

class AutorDetailView(generic.DetailView):
    model = Autor
    template_name = 'autores/detalhe.html'  # Ajustado para seu caminho
    context_object_name = 'autor'

    def get_queryset(self):
        return Autor.objects.prefetch_related(
            Prefetch('livros', queryset=Livro.objects.all())
        )

# ----------------------------
# Autores - CRUD (admin apenas)
# ----------------------------
class AutorCreateView(SomenteAdminMixin, generic.CreateView):
    model = Autor
    form_class = AutorForm
    template_name = 'autores/form.html'
    success_url = reverse_lazy('autor-lista')


class AutorUpdateView(SomenteAdminMixin, generic.UpdateView):
    model = Autor
    form_class = AutorForm
    template_name = 'autores/form.html'
    success_url = reverse_lazy('autor-lista')


class AutorDeleteView(SomenteAdminMixin, generic.DeleteView):
    model = Autor
    template_name = 'autores/confirmar_exclusao.html'
    success_url = reverse_lazy('autor-lista')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            return super().delete(request, *args, **kwargs)
        except Exception as e:
            messages.error(request, f'Erro ao excluir: {str(e)}')
            return redirect('autor-lista')