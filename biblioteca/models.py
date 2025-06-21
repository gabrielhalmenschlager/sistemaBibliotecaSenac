from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError

# ----------------------------
# Usuário
# ----------------------------
class Usuario(AbstractUser):
    TIPOS = [
        ('aluno', 'Aluno'),
        ('admin', 'Administrador'),
    ]
    tipo = models.CharField(max_length=10, choices=TIPOS, default='aluno')
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username

# ----------------------------
# Autor
# ----------------------------
class Autor(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    biografia = models.TextField(blank=True)

    def __str__(self):
        return self.nome

    def delete(self, *args, **kwargs):
        if self.livro_set.exists():
            raise ProtectedError("Não é possível excluir um autor associado a um livro.", self)
        super().delete(*args, **kwargs)

# ----------------------------
# Livro
# ----------------------------
class Livro(models.Model):
    GENEROS = [
        ('Ficção', 'Ficção'),
        ('Não Ficção', 'Não Ficção'),
        ('Infantil', 'Infantil'),
        ('Acadêmico', 'Acadêmico'),
    ]

    titulo = models.CharField(max_length=200, unique=True)
    genero = models.CharField(max_length=20, choices=GENEROS)
    quantidade = models.PositiveIntegerField(default=1)
    autores = models.ManyToManyField(Autor)
    capa = models.ImageField(upload_to='capas/', blank=True, null=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    def is_disponivel(self):
        return self.quantidade > 0

    def clean(self):
        if self.quantidade < 0:
            raise ValidationError("A quantidade não pode ser negativa.")
        if self.capa:
            if not self.capa.name.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                raise ValidationError("Formato da capa inválido. Use JPG, PNG ou GIF.")
            if self.capa.size > 5 * 1024 * 1024:
                raise ValidationError("A imagem da capa deve ter no máximo 5MB.")

# ----------------------------
# Reserva
# ----------------------------
class Reserva(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_reserva = models.DateTimeField(auto_now_add=True)
    ativa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.usuario} reservou {self.livro}"

    def clean(self):
        if not self.livro.is_disponivel():
            raise ValidationError("Livro indisponível para reserva.")
        
        reservas_ativas = Reserva.objects.filter(usuario=self.usuario, ativa=True)
        if reservas_ativas.count() >= 3:
            raise ValidationError("Você já possui 3 reservas ativas.")
        
        if Reserva.objects.filter(usuario=self.usuario, livro=self.livro, ativa=True).exists():
            raise ValidationError("Você já reservou esse livro.")

    def save(self, *args, **kwargs):
        self.clean()  # chama validações manuais
        super().save(*args, **kwargs)
        self.livro.quantidade -= 1
        self.livro.save()

    def cancelar(self):
        if self.ativa:
            self.ativa = False
            self.save()
            self.livro.quantidade += 1
            self.livro.save()

# ----------------------------
# Empréstimo
# ----------------------------
class Emprestimo(models.Model):
    livro = models.ForeignKey(Livro, on_delete=models.CASCADE)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    data_emprestimo = models.DateTimeField(auto_now_add=True)
    data_devolucao = models.DateTimeField()
    devolvido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario} emprestou {self.livro}"

    def clean(self):
        emprestimos_ativos = Emprestimo.objects.filter(usuario=self.usuario, devolvido=False)
        if emprestimos_ativos.count() >= 3:
            raise ValidationError("Você já possui 3 empréstimos ativos.")
        
        if not self.livro.is_disponivel():
            raise ValidationError("Livro indisponível para empréstimo.")

    def save(self, *args, **kwargs):
        if not self.id:  # novo empréstimo
            self.clean()
            self.data_devolucao = timezone.now() + timezone.timedelta(days=7)
            self.livro.quantidade -= 1
            self.livro.save()

            # Desativa reserva se existir
            Reserva.objects.filter(usuario=self.usuario, livro=self.livro, ativa=True).update(ativa=False)

        super().save(*args, **kwargs)

    def devolver(self):
        if not self.devolvido:
            self.devolvido = True
            self.save()
            self.livro.quantidade += 1
            self.livro.save()

    @property
    def esta_atrasado(self):
        return not self.devolvido and self.data_devolucao < timezone.now()
