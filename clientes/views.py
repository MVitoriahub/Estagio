from django.shortcuts import get_object_or_404, redirect, render
from .models import Cliente
from .forms import ClienteForm


def listar_clientes(request):
    busca    = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()

    if busca:
        clientes = clientes.filter(nome__icontains=busca)

    return render(request, 'clientes/listar.html', {
        'clientes': clientes,
        'busca'   : busca,
    })


def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('clientes:listar_clientes')
    else:
        form = ClienteForm()

    return render(request, 'clientes/criar.html', {'form': form})


def visualizar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    return render(request, 'clientes/visualizar.html', {'cliente': cliente})


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('clientes:listar_clientes')
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'clientes/editar.html', {
        'form'   : form,
        'cliente': cliente,
    })


def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    if request.method == 'POST':
        cliente.delete()  # soft delete
        return redirect('clientes:listar_clientes')

    return render(request, 'clientes/excluir.html', {'cliente': cliente})