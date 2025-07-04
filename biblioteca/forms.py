from django import forms
from .models import Livro, Autor

class LivroForm(forms.ModelForm):
    autores = forms.ModelMultipleChoiceField(
        queryset=Autor.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='Autores',
        help_text='Selecione um ou mais autores já cadastrados.'
    )

    class Meta:
        model = Livro
        fields = ['titulo', 'genero', 'quantidade', 'capa', 'autores']

    def clean_autores_texto(self):
        autores = self.cleaned_data['autores_texto']
        nomes = [nome.strip() for nome in autores.split(',') if nome.strip()]
        if not nomes:
            raise forms.ValidationError("Informe pelo menos um autor.")
        return nomes


class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nome', 'biografia']
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome'].strip()
        if Autor.objects.exclude(pk=self.instance.pk).filter(nome__iexact=nome).exists():
            raise forms.ValidationError("Já existe um autor com este nome.")
        return nome
