from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from produto.models import Produto, ProdutoVariacao
from .models import Estoque
from .forms import EstoqueForm, NovaVariacaoForm   # vamos criar esse form


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
        form = EstoqueForm(request.POST)
        if form.is_valid():
            movimentacao          = form.save(commit=False)
            movimentacao.variacao = variacao
            try:
                movimentacao.save()
                messages.success(request, 'Movimentação registrada com sucesso.')
                return redirect('estoque:movimentacoes', pk=pk)
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = EstoqueForm()

    return render(request, 'estoque/registrar.html', {
        'form'    : form,
        'variacao': variacao,
    })


def nova_variacao(request, produto_pk):
    produto = get_object_or_404(Produto, pk=produto_pk)
    if request.method == 'POST':
        form = NovaVariacaoForm(request.POST)
        if form.is_valid():
            quantidade_inicial = form.cleaned_data['quantidade']
            # Cria a variação com quantidade 0 para o Estoque.save() somar corretamente
            variacao = ProdutoVariacao.objects.create(
                produto     = produto,
                tamanho     = form.cleaned_data['tamanho'],
                quantidade  = 0,
                valor_bruto = form.cleaned_data['valor_bruto'],
            )
            # Registra a entrada inicial no estoque
            if quantidade_inicial > 0:
                Estoque.objects.create(
                    variacao   = variacao,
                    tipo       = 'entrada',
                    quantidade = quantidade_inicial,
                    observacao = 'Variação adicionada via estoque',
                )
            messages.success(request, f'Variação {variacao.tamanho} adicionada com sucesso.')
            return redirect('estoque:listar')
    else:
        form = NovaVariacaoForm()

    return render(request, 'estoque/nova_variacao.html', {
        'form'   : form,
        'produto': produto,
    })