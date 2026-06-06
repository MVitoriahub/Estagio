from django.shortcuts import render, get_object_or_404, redirect
from django.forms import inlineformset_factory
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


def listar(request):
    produtos = Produto.objects.prefetch_related('variacoes').all()
    return render(request, 'produto/listar.html', {'produtos': produtos})


def visualizar(request, pk):
    produto   = get_object_or_404(Produto, pk=pk)
    variacoes = produto.variacoes.all()
    return render(request, 'produto/visualizar.html', {
        'produto'  : produto,
        'variacoes': variacoes,
    })


def criar(request):
    if request.method == 'POST':
        form    = ProdutoForm(request.POST)
        formset = VariacaoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            produto          = form.save()
            formset.instance = produto
            variacoes        = formset.save()

            # Para cada variação salva, cria entrada no estoque automaticamente
            for variacao in variacoes:
                if variacao.quantidade and variacao.quantidade > 0:
                    quantidade_inicial = variacao.quantidade
                    # Zera antes para o save() do Estoque não duplicar
                    ProdutoVariacao.objects.filter(pk=variacao.pk).update(quantidade=0)
                    variacao.refresh_from_db()
                    Estoque.objects.create(
                        variacao=variacao,
                        tipo='entrada',
                        quantidade=quantidade_inicial,
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
        form    = ProdutoForm(request.POST, instance=produto)
        formset = VariacaoEditFormSet(request.POST, instance=produto)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('produto:listar')
    else:
        form    = ProdutoForm(instance=produto)
        formset = VariacaoEditFormSet(instance=produto)

    return render(request, 'produto/editar.html', {
        'form'   : form,
        'formset': formset,
        'produto': produto,
    })


def excluir(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        return redirect('produto:listar')
    return render(request, 'produto/excluir.html', {'produto': produto})