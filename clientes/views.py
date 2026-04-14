from django.shortcuts import render, get_object_or_404, redirect
from .models import Cliente

def listar_clientes(request):
    busca = request.GET.get('q', '')
    clientes = Cliente.objects.all()

    if busca:
        clientes = clientes.filter(nome__icontains=busca)

    return render(request, 'clientes/listar.html', {'clientes': clientes})

def criar_cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        contato = request.POST.get('contato')

        Cliente.objects.create(
            nome=nome,
            cpf=cpf,
            contato=contato
        )

        return redirect('listar_clientes')

    return render(request, 'clientes/criar.html')

def visualizar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    return render(request, 'clientes/visualizar.html', {'cliente': cliente})

def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        cliente.nome = request.POST.get('nome')
        cliente.cpf = request.POST.get('cpf')
        cliente.contato = request.POST.get('contato')
        cliente.save()

        return redirect('listar_clientes')

    return render(request, 'clientes/editar.html', {'cliente': cliente})

def excluir_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)

    if request.method == 'POST':
        cliente.delete()
        return redirect('listar_clientes')

    return render(request, 'clientes/excluir.html', {'cliente': cliente})