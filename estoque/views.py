from decimal import Decimal

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError

from produto.models import Produto, ProdutoVariacao
from .models import Estoque
from .forms import EstoqueForm, NovaVariacaoForm


def _avisar_margem(request, variacao_pk):
    """Compara a margem atual com o lucro (%) do produto e avisa se estiver abaixo.
    Não altera nenhum valor, só informa."""
    v = ProdutoVariacao.todos.select_related('produto').get(pk=variacao_pk)
    if not v.valor_bruto or v.preco_venda is None:
        return

    if v.preco_venda <= v.valor_bruto:
        messages.error(
            request,
            f'ATENÇÃO: o preço de venda (R$ {v.preco_venda}) está igual ou abaixo do custo médio '
            f'(R$ {v.valor_bruto}). Cada venda deste item dá prejuízo.'
        )
        return

    alvo   = v.produto.lucro
    margem = v.margem_percentual
    if margem is not None and margem < alvo:
        sugerido = (v.valor_bruto * (Decimal('1') + alvo / Decimal('100'))).quantize(Decimal('0.01'))
        messages.warning(
            request,
            f'Margem abaixo do alvo: {margem}% (alvo do produto: {alvo}%). '
            f'Para voltar ao alvo, o preço de venda seria R$ {sugerido}. O preço atual não foi alterado.'
        )


def listar(request):
    variacoes = ProdutoVariacao.objects.select_related('produto').prefetch_related('movimentacoes').all()
    return render(request, 'estoque/listar.html', {'variacoes': variacoes})


def movimentacoes(request, pk):
    variacao      = get_object_or_404(ProdutoVariacao, pk=pk)
    movimentacoes = variacao.movimentacoes.all()
    return render(request, 'estoque/movimentacoes.html', {
        'variacao'     : variacao,
        'movimentacoes': movimentacoes,
    })


def registrar(request, pk):
    variacao = get_object_or_404(ProdutoVariacao, pk=pk)
    if request.method == 'POST':
        form = EstoqueForm(request.POST, variacao=variacao)
        if form.is_valid():
            movimentacao          = form.save(commit=False)
            movimentacao.variacao = variacao
            try:
                movimentacao.save()
                messages.success(request, 'Movimentação registrada com sucesso.')
                return redirect('estoque:movimentacoes', pk=pk)
            except ValidationError as e:
                messages.error(request, ' '.join(e.messages))
    else:
        form = EstoqueForm(variacao=variacao)

    return render(request, 'estoque/registrar.html', {
        'form'    : form,
        'variacao': variacao,
    })


def nova_variacao(request, produto_pk):
    produto = get_object_or_404(Produto, pk=produto_pk)
    if request.method == 'POST':
        form = NovaVariacaoForm(request.POST)
        if form.is_valid():
            tamanho    = form.cleaned_data['tamanho']
            quantidade = form.cleaned_data['quantidade']
            custo      = form.cleaned_data['valor_bruto']
            novo_preco = form.cleaned_data.get('preco_venda')

            existente = ProdutoVariacao.objects.filter(produto=produto, tamanho=tamanho).first()

            if existente:
                # Tamanho já existe: soma as peças, recalcula o custo médio
                # e, se informado, atualiza o preço de venda.
                if quantidade <= 0 and not novo_preco:
                    messages.error(
                        request,
                        f'O tamanho {tamanho} já existe. Informe uma quantidade maior que zero ou um novo preço de venda.'
                    )
                else:
                    try:
                        if quantidade > 0:
                            Estoque.objects.create(
                                variacao       = existente,
                                tipo           = 'entrada',
                                quantidade     = quantidade,
                                custo_unitario = custo,
                                observacao     = 'Nova remessa via Adicionar variação',
                            )
                        if novo_preco:
                            ProdutoVariacao.todos.filter(pk=existente.pk).update(preco_venda=novo_preco)

                        partes = []
                        if quantidade > 0:
                            partes.append(f'{quantidade} peça(s) adicionada(s) e custo médio atualizado')
                        if novo_preco:
                            partes.append('preço de venda atualizado')
                        else:
                            partes.append('preço de venda mantido')
                        messages.success(request, f'Tamanho {tamanho}: ' + ', '.join(partes) + '.')
                        _avisar_margem(request, existente.pk)
                        return redirect('estoque:listar')
                    except ValidationError as e:
                        messages.error(request, ' '.join(e.messages))
            else:
                # Tamanho novo: cria a variação com quantidade 0 para o Estoque.save() somar corretamente
                variacao = ProdutoVariacao.objects.create(
                    produto     = produto,
                    tamanho     = tamanho,
                    quantidade  = 0,
                    valor_bruto = custo,
                    preco_venda = novo_preco,  # None = calcula pelo lucro do produto
                )
                if quantidade > 0:
                    Estoque.objects.create(
                        variacao       = variacao,
                        tipo           = 'entrada',
                        quantidade     = quantidade,
                        custo_unitario = custo,
                        observacao     = 'Variação adicionada via estoque',
                    )
                messages.success(request, f'Variação {variacao.tamanho} adicionada com sucesso.')
                _avisar_margem(request, variacao.pk)
                return redirect('estoque:listar')
    else:
        form = NovaVariacaoForm()

    return render(request, 'estoque/nova_variacao.html', {
        'form'   : form,
        'produto': produto,
    })