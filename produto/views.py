from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Produto, ProdutoVariacao
from .forms import ProdutoForm, ProdutoVariacaoForm, ProdutoVariacaoEditForm
from estoque.models import Estoque


VariacaoFormSet = inlineformset_factory(
    Produto,
    ProdutoVariacao,
    form=ProdutoVariacaoForm,
    extra=1,
    can_delete=True
)

VariacaoEditFormSet = inlineformset_factory(
    Produto,
    ProdutoVariacao,
    form=ProdutoVariacaoEditForm,
    extra=0,
    can_delete=False
)


CORES_CATEGORIA = {
    'blusa':              '#3b82f6',
    'calça':               '#8b5cf6',
    'shorts':              '#f97316',
    'bermuda':             '#f59e0b',
    'saia':                '#ec4899',
    'meia':                '#6b7280',
    'legging':             '#a855f7',
    'vestido':             '#10b981',
    'camisa':              '#06b6d4',
    'camiseta':            '#0ea5e9',
    'conjunto_feminino':   '#d946ef',
    'conjunto_masculino':  '#6366f1',
    'jaqueta':             '#78716c',
    'moletom':             '#737373',
    'body':                '#f43f5e',
    'colete':              '#84cc16',
    'calca_jeans':         '#1d4ed8',
    'calcado':             '#b45309',
    'acessorio':           '#eab308',
}


def listar(request):
    busca = request.GET.get('q', '').strip()

    produtos = Produto.objects.prefetch_related('variacoes').all()

    if busca:
        produtos = produtos.filter(
            Q(item__icontains=busca) |
            Q(marca__icontains=busca) |
            Q(colecao__icontains=busca)
        )

    paginator  = Paginator(produtos, 10)
    page_number = request.GET.get('page')
    pagina      = paginator.get_page(page_number)

    for produto in pagina:
        produto.cor_categoria = CORES_CATEGORIA.get(produto.categoria, '#6b7280')

    return render(request, 'produto/listar.html', {
        'produtos': pagina,
        'busca': busca,
    })


def visualizar(request, pk):
    produto   = get_object_or_404(Produto, pk=pk)
    variacoes = produto.variacoes.all()
    return render(request, 'produto/visualizar.html', {
        'produto'  : produto,
        'variacoes': variacoes,
        'estoque_total': sum(v.quantidade for v in variacoes),
    })


def criar(request):
    if request.method == 'POST':
        form    = ProdutoForm(request.POST)
        formset = VariacaoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            produto          = form.save()
            formset.instance = produto
            variacoes        = formset.save()

            for variacao in variacoes:
                if variacao.quantidade and variacao.quantidade > 0:
                    quantidade_inicial = variacao.quantidade
                    ProdutoVariacao.objects.filter(pk=variacao.pk).update(quantidade=0)
                    variacao.refresh_from_db()
                    Estoque.objects.create(
                        variacao=variacao,
                        tipo='entrada',
                        quantidade=quantidade_inicial,
                        custo_unitario=variacao.valor_bruto,
                        observacao='Estoque inicial do cadastro'
                    )

            return redirect('produto:listar')
    else:
        form    = ProdutoForm()
        formset = VariacaoFormSet()

    return render(request, 'produto/criar.html', {
        'form'   : form,
        'formset': formset,
    })


def editar(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            # Mudar o lucro (%) NÃO recalcula preços existentes.
            # O preço de venda é alterado apenas pelo Estoque.
            form.save()
            return redirect('produto:listar')
    else:
        form = ProdutoForm(instance=produto)

    return render(request, 'produto/editar.html', {
        'form'   : form,
        'produto': produto,
    })


def excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return redirect('produto:listar')
    return render(request, 'produto/excluir.html', {'produto': produto})