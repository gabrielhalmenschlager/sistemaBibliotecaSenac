from django import forms
from .models import Livro, Autor

class LivroForm(forms.ModelForm):
    autores_texto = forms.CharField(
        label='Autores (separados por vírgula)',
        required=True,
        help_text='Digite os nomes dos autores separados por vírgula.'
    )

    class Meta:
        model = Livro
        fields = ['titulo', 'genero', 'quantidade', 'capa']

    def clean_autores_texto(self):
        autores = self.cleaned_data['autores_texto']
        nomes = [nome.strip() for nome in autores.split(',') if nome.strip()]
        if not nomes:
            raise forms.ValidationError("Informe pelo menos um autor.")
        return nomes