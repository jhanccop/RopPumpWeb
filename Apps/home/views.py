from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib import messages

from django.views.generic import CreateView
from .models import infoRequests

from .forms import infoRequestsForm


# Create your views here.

class InitView(CreateView):
    model = infoRequests
    form_class = infoRequestsForm
    template_name = "home/home.html"
    success_url = reverse_lazy('home_app:home')

    def form_valid(self, form):
        """
        Método para procesar el formulario válido
        """
        # Puedes agregar lógica adicional si lo necesitas
        messages.success(self.request, 'Tu contacto ha sido registrado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Método para manejar formularios inválidos
        """
        messages.error(self.request, 'Hubo un error al procesar tu solicitud. Por favor, revisa los campos.')
        return super().form_invalid(form)

class LoginView(TemplateView):
    template_name = "home/login.html"

class DevicesView(TemplateView):
    template_name = "home/dispositivos.html"
   