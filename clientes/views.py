from django.shortcuts import get_object_or_404, redirect, render

from .models import Cliente


def listar_clientes(request):
    busca = request.GET.get('q', '').strip()
    clientes = Cliente.objects.all()

    if busca:
        clientes = clientes.filter(nome__icontains=busca)

    context = {
        'clientes': clientes,
        'busca': busca,
    }
    return render(request, 'clientes/listar.html', context)


def criar_cliente(request):
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        cpf = request.POST.get('cpf', '').strip()
        contato = request.POST.get('contato', '').strip()
        rua = request.POST.get('rua', '').strip()
        numero = request.POST.get('numero', '').strip()
        bairro = request.POST.get('bairro', '').strip()
        cidade = request.POST.get('cidade', '').strip()

        Cliente.objects.create(
            nome=nome,
            cpf=cpf,
            contato=contato,
            rua=rua,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
        )

        return redirect('clientes:listar_clientes')

    return render(request, 'clientes/criar.html')


def visualizar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    context = {
        'cliente': cliente,
    }
    return render(request, 'clientes/visualizar.html', context)


def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        cliente.nome = request.POST.get('nome', '').strip()
        cliente.cpf = request.POST.get('cpf', '').strip()
        cliente.contato = request.POST.get('contato', '').strip()
        cliente.rua = request.POST.get('rua', '').strip()
        cliente.numero = request.POST.get('numero', '').strip()
        cliente.bairro = request.POST.get('bairro', '').strip()
        cliente.cidade = request.POST.get('cidade', '').strip()
        cliente.save()

        return redirect('clientes:listar_clientes')

    context = {
        'cliente': cliente,
    }
    return render(request, 'clientes/editar.html', context)


def excluir_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)

    if request.method == 'POST':
        cliente.delete()
        return redirect('clientes:listar_clientes')

    context = {
        'cliente': cliente,
    }
    return render(request, 'clientes/excluir.html', context)