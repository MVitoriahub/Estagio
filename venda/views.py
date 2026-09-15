from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from produto.models import Produto, ProdutoVariacao
from .models import Venda, ItemVenda
from .forms import AdicionarItemForm, FinalizarVendaForm


def listar(request):
    vendas = Venda.objects.prefetch_related('itens__variacao__produto').filter(
        status='finalizada'
    )
    return render(request, 'venda/listar.html', {'vendas': vendas})


def nova(request):
    venda_id = request.session.get('venda_aberta_id')
    venda    = None
    if venda_id:
        try:
            venda = Venda.objects.get(pk=venda_id, status='aberta')
        except Venda.DoesNotExist:
            venda = None

    if not venda:
        venda = Venda.objects.create(status='aberta')
        request.session['venda_aberta_id'] = venda.pk

    form = AdicionarItemForm(request.POST or None)

    if request.method == 'POST' and 'adicionar' in request.POST:
        if form.is_valid():
            variacao   = form.cleaned_data['variacao']
            quantidade = form.cleaned_data['quantidade']

            item_existente = venda.itens.filter(variacao=variacao).first()
            if item_existente:
                item_existente.quantidade += quantidade
                item_existente.save()
            else:
                ItemVenda.objects.create(
                    venda          = venda,
                    variacao       = variacao,
                    quantidade     = quantidade,
                    valor_unitario = variacao.preco_venda,
                )
            messages.success(request, 'Item adicionado ao carrinho.')
            return redirect('venda:nova')

    itens = venda.itens.select_related('variacao__produto').all()
    return render(request, 'venda/nova.html', {
        'form' : form,
        'venda': venda,
        'itens': itens,
    })


def remover_item(request, item_pk):
    item = get_object_or_404(ItemVenda, pk=item_pk)
    item.delete()
    messages.success(request, 'Item removido.')
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER')
    return redirect(next_url) if next_url else redirect('venda:nova')


def editar_item(request, item_pk):
    item = get_object_or_404(ItemVenda, pk=item_pk)
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or 'venda:listar'

    if request.method == 'POST':
        variacao_id = request.POST.get('variacao')
        quantidade  = request.POST.get('quantidade')
        try:
            variacao   = ProdutoVariacao.objects.get(pk=variacao_id, produto=item.variacao.produto)
            quantidade = int(quantidade)
            if quantidade < 1:
                raise ValueError

            saldo_disponivel = variacao.quantidade
            if variacao_id == str(item.variacao_id):
                saldo_disponivel += item.quantidade

            if quantidade > saldo_disponivel:
                messages.error(request, f'Saldo insuficiente. Disponível: {saldo_disponivel} unidades.')
            else:
                item.variacao       = variacao
                item.valor_unitario = variacao.preco_venda
                item.quantidade     = quantidade
                item.save()
                messages.success(request, 'Item atualizado.')
        except (ProdutoVariacao.DoesNotExist, ValueError, TypeError):
            messages.error(request, 'Dados inválidos.')

    return redirect(next_url)


def finalizar(request):
    venda_id = request.session.get('venda_aberta_id')
    venda    = get_object_or_404(Venda, pk=venda_id, status='aberta')

    if not venda.itens.exists():
        messages.error(request, 'Adicione ao menos um item antes de finalizar.')
        return redirect('venda:nova')

    form = FinalizarVendaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        venda.finalizar(
            cliente         = form.cleaned_data['cliente'],
            forma_pagamento = form.cleaned_data['forma_pagamento'],
        )
        del request.session['venda_aberta_id']
        messages.success(request, f'Venda #{venda.pk} finalizada com sucesso!')
        return redirect('venda:listar')

    itens = venda.itens.select_related('variacao__produto').all()
    return render(request, 'venda/finalizar.html', {
        'form' : form,
        'venda': venda,
        'itens': itens,
    })


def excluir(request, pk):
    venda = get_object_or_404(Venda, pk=pk)
    if request.method == 'POST':
        venda.cancelar()
        messages.success(request, f'Venda #{venda.pk} cancelada.')
        return redirect('venda:listar')
    itens = venda.itens.select_related('variacao__produto').all()
    return render(request, 'venda/excluir.html', {
        'venda': venda,
        'itens': itens,
    })


def visualizar(request, pk):
    venda = get_object_or_404(Venda, pk=pk, status='finalizada')
    itens = venda.itens.select_related('variacao__produto').all()
    return render(request, 'venda/visualizar.html', {
        'venda': venda,
        'itens': itens,
    })


def editar(request, pk):
    venda = get_object_or_404(Venda, pk=pk, status='finalizada')
    form  = AdicionarItemForm(request.POST or None)
    form_venda = FinalizarVendaForm(request.POST or None, initial={
        'cliente': venda.cliente,
        'forma_pagamento': venda.forma_pagamento,
    })

    if request.method == 'POST' and 'adicionar' in request.POST:
        if form.is_valid():
            variacao   = form.cleaned_data['variacao']
            quantidade = form.cleaned_data['quantidade']
            item_existente = venda.itens.filter(variacao=variacao).first()
            if item_existente:
                item_existente.quantidade += quantidade
                item_existente.save()
            else:
                ItemVenda.objects.create(
                    venda          = venda,
                    variacao       = variacao,
                    quantidade     = quantidade,
                    valor_unitario = variacao.preco_venda,
                )
            return redirect('venda:editar', pk=pk)

    if request.method == 'POST' and 'salvar_venda' in request.POST:
        if form_venda.is_valid():
            venda.cliente         = form_venda.cleaned_data['cliente']
            venda.forma_pagamento = form_venda.cleaned_data['forma_pagamento']
            venda.save()
            messages.success(request, 'Dados da venda atualizados.')
            return redirect('venda:listar')

    itens = venda.itens.select_related('variacao__produto').all()
    return render(request, 'venda/editar.html', {
        'form'      : form,
        'form_venda': form_venda,
        'venda'     : venda,
        'itens'     : itens,
    })


def variacoes_por_produto(request):
    """Retorna as variações disponíveis de um produto em JSON (para o select dinâmico).
    Se 'incluir_id' for passado, a variação atual do item também é incluída,
    mesmo que já esteja com estoque zerado — necessário para o modal de editar item."""
    produto_id = request.GET.get('produto_id')
    incluir_id = request.GET.get('incluir_id')

    variacoes_qs = ProdutoVariacao.objects.filter(produto_id=produto_id, quantidade__gt=0)
    if incluir_id:
        variacoes_qs = variacoes_qs | ProdutoVariacao.objects.filter(pk=incluir_id, produto_id=produto_id)

    variacoes = variacoes_qs.distinct().values('id', 'tamanho', 'quantidade')
    return JsonResponse({'variacoes': list(variacoes)})