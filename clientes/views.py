import re
from urllib.parse import urlencode

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import Cliente
from .forms import ClienteForm


# ---------------------------------------------------------------------------
# Configuração da listagem
# ---------------------------------------------------------------------------

# (chave na URL, rótulo, campo no banco, é texto?)
# Só as chaves desta lista são aceitas em ?ordem=  (evita ordenar por campo arbitrário).
COLUNAS = [
    ('id',       'ID',       'id',        False),
    ('nome',     'Nome',     'nome',      True),
    ('cpf',      'CPF',      'cpf',       False),
    ('contato',  'Contato',  'contato',   False),
    ('cidade',   'Cidade',   'cidade',    True),
    ('cadastro', 'Cadastro', 'criado_em', False),
]
CAMPO_POR_CHAVE = {chave: (campo, texto) for chave, _, campo, texto in COLUNAS}

TAMANHOS_PAGINA = (10, 25, 50)
ORDEM_PADRAO    = 'nome'
POR_PAGINA_PADRAO = 10

# dígitos e separadores comuns de CPF/telefone (ponto, hífen, parênteses, espaço, +)
BUSCA_NUMERICA = re.compile(r'[\s.\-()/+]*[0-9][0-9\s.\-()/+]*')


def _querystring(params, **extra):
    dados = {**params, **extra}
    return urlencode({k: v for k, v in dados.items() if v not in ('', None)})


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

def listar_clientes(request):
    get = request.GET

    # --- parâmetros (todos validados / normalizados) ---
    busca = get.get('q', '').strip()

    ordem = get.get('ordem', ORDEM_PADRAO)
    if ordem not in CAMPO_POR_CHAVE:
        ordem = ORDEM_PADRAO
    direcao = 'desc' if get.get('dir') == 'desc' else 'asc'

    try:
        por_pagina = int(get.get('por_pagina', POR_PAGINA_PADRAO))
    except (TypeError, ValueError):
        por_pagina = POR_PAGINA_PADRAO
    if por_pagina not in TAMANHOS_PAGINA:
        por_pagina = POR_PAGINA_PADRAO

    # --- consulta ---
    base     = Cliente.objects.all()
    clientes = base

    if busca:
        filtro = Q(nome__icontains=busca) | Q(contato__icontains=busca)
        # Só procura em CPF/contato quando o texto parece número ("103.288.529-05",
        # "(43) 9914"). Assim "Cliente 2" não casa com todo CPF que tenha um 2.
        if BUSCA_NUMERICA.fullmatch(busca):
            digitos = ''.join(c for c in busca if c.isdigit())
            filtro |= Q(cpf__contains=digitos) | Q(contato__contains=digitos)
        clientes = clientes.filter(filtro)

    campo, eh_texto = CAMPO_POR_CHAVE[ordem]
    expressao = Lower(campo) if eh_texto else F(campo)
    expressao = expressao.desc() if direcao == 'desc' else expressao.asc()
    clientes = clientes.order_by(expressao, 'id')  # 'id' desempata -> paginação estável

    paginator = Paginator(clientes, por_pagina)
    page_obj  = paginator.get_page(get.get('page'))  # página inválida -> 1 ou última

    # --- helpers de URL (mantêm busca/filtros/ordem ao navegar) ---
    params = {
        'q': busca,
        'ordem': ordem, 'dir': direcao, 'por_pagina': por_pagina,
    }

    colunas = []
    for chave, rotulo, _, eh_texto in COLUNAS:
        ativa = chave == ordem
        proxima = 'desc' if (ativa and direcao == 'asc') else 'asc'
        colunas.append({
            'chave': chave,
            'rotulo': rotulo,
            'url': '?' + _querystring(params, ordem=chave, dir=proxima, page=''),
            'aria': ('ascending' if direcao == 'asc' else 'descending') if ativa else 'none',
            'icone': ('bi-caret-up-fill' if direcao == 'asc' else 'bi-caret-down-fill') if ativa else 'bi-arrow-down-up',
            'dica': f'Ordenar por {rotulo} ({"decrescente" if proxima == "desc" else "crescente"})',
        })

    # Opções do <select> "Ordenar por" (usado no celular, onde o cabeçalho some)
    opcoes_ordem = []
    for chave, rotulo, _, eh_texto in COLUNAS:
        asc, desc = ('A–Z', 'Z–A') if eh_texto else ('crescente', 'decrescente')
        for sentido, texto in (('asc', asc), ('desc', desc)):
            valor = f'{chave}:{sentido}'
            opcoes_ordem.append({
                'valor': valor,
                'rotulo': f'{rotulo} ({texto})',
                'selecionado': valor == f'{ordem}:{direcao}',
            })

    paginas = []
    for n in paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1):
        if n == paginator.ELLIPSIS:
            paginas.append({'reticencias': True})
        else:
            paginas.append({
                'num': n,
                'atual': n == page_obj.number,
                'url': '?' + _querystring(params, page=n),
            })

    return render(request, 'clientes/listar.html', {
        'clientes'    : page_obj.object_list,
        'page_obj'    : page_obj,
        'paginas'     : paginas,
        'anterior_url': ('?' + _querystring(params, page=page_obj.previous_page_number())) if page_obj.has_previous() else None,
        'proxima_url' : ('?' + _querystring(params, page=page_obj.next_page_number())) if page_obj.has_next() else None,
        'total'       : paginator.count,          # resultados após filtros
        'total_geral' : base.count(),             # todos os clientes
        'inicio'      : page_obj.start_index(),
        'fim'         : page_obj.end_index(),
        'colunas'     : colunas,
        'opcoes_ordem': opcoes_ordem,
        'tamanhos'    : TAMANHOS_PAGINA,
        'por_pagina'  : por_pagina,
        'ordem'       : ordem,
        'direcao'     : direcao,
        'busca'       : busca,
        'tem_filtros' : bool(busca),
        'url_limpar'  : reverse('clientes:listar_clientes'),
    })


def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Se o CPF era de um cliente excluído, o form.save() reativa o registro antigo
            reativado = form._cliente_excluido is not None
            try:
                cliente = form.save()
            except IntegrityError:
                form.add_error('cpf', 'Já existe um cliente cadastrado com esse CPF.')
            else:
                if reativado:
                    messages.info(
                        request,
                        f'O CPF já pertencia a um cliente excluído. '
                        f'{cliente.nome} foi reativado com os dados informados e o histórico de vendas foi mantido.'
                    )
                else:
                    messages.success(request, f'Cliente {cliente.nome} cadastrado com sucesso.')
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
            try:
                form.save()
            except IntegrityError:
                form.add_error('cpf', 'Já existe um cliente cadastrado com esse CPF.')
            else:
                messages.success(request, f'Cliente {cliente.nome} atualizado com sucesso.')
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
        nome = cliente.nome
        cliente.delete()
        messages.success(request, f'Cliente {nome} excluído com sucesso.')
        return redirect('clientes:listar_clientes')

    return render(request, 'clientes/excluir.html', {'cliente': cliente})