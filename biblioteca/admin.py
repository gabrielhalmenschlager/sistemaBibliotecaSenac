from django.contrib import admin
from django.core.exceptions import ValidationError
from .models import Usuario, Autor, Livro, Reserva, Emprestimo

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'tipo', 'is_staff', 'is_active')
    list_filter = ('tipo', 'is_staff', 'is_active')
    search_fields = ('username', 'email')

@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

    def has_add_permission(self, request):
        return request.user.is_authenticated and request.user.tipo == 'admin'

    def has_change_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.tipo == 'admin'

    def has_delete_permission(self, request, obj=None):
        return request.user.is_authenticated and request.user.tipo == 'admin'

    def delete_model(self, request, obj):
        if obj.livro_set.exists():
            raise ValidationError("Não é possível excluir um autor associado a um livro.")
        super().delete_model(request, obj)

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'genero', 'quantidade', 'data_cadastro', 'lista_autores')
    search_fields = ('titulo', 'autores__nome')
    list_filter = ('genero',)
    filter_horizontal = ('autores',)

    def lista_autores(self, obj):
        return ", ".join(autor.nome for autor in obj.autores.all())
    lista_autores.short_description = 'Autores'

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('livro', 'usuario', 'data_reserva', 'ativa')
    list_filter = ('ativa',)
    search_fields = ('livro__titulo', 'usuario__username')

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('livro', 'usuario', 'data_emprestimo', 'data_devolucao', 'devolvido')
    list_filter = ('devolvido',)
    search_fields = ('livro__titulo', 'usuario__username')
