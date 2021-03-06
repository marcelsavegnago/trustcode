# -*- coding: utf-8 -*-

import xmlrpclib
import socket


class ConexaoOdoo():
    def __init__(self):
        self.database = str(raw_input('Nome do banco de dados: '))
        self.host = str(raw_input('Host/IP Odoo: '))
        self.user = str(raw_input('Usuario Odoo: '))
        self.password = str(raw_input('Senha Odoo: '))
        self.conn, self.uid = self.new_connection()
        cliente_id = self.create_cliente()
        print 'ID do cliente criado: %s.\n' % cliente_id
        cliente_atualizado = self.update_cliente(cliente_id)
        print 'Cliente atualizado: %s.\n' % 'SIM' if cliente_atualizado else 'Nao'
        quantidade_cliente = self.get_quantidade_cliente()
        print 'Numero de clientes cadastrados: %s.\n' % quantidade_cliente
        cliente_dados = self.get_cliente_dados()
        print '10 primeiros clientes por ordem alfebetica: \n%s' % cliente_dados
        maior_venda_dados = self.get_maior_venda_dados()
        print 'Maior venda feita:\n%s' % maior_venda_dados or 'Nao possui vendas'
        produto_maior_venda_dados = self.get_produto_maior_venda_dados()
        print 'Produtos da maior venda:\n%s' % produto_maior_venda_dados or 'Nehum produto vendido'
        percentual_de_vendas = self.get_percentual_de_vendas()
        print 'O percentual de fechamento e: %s\n' % percentual_de_vendas
        valor_total_faturas = self.get_valor_total_faturas()
        print 'Total de faturas 06/2017: R$%s\n' % valor_total_faturas
        orcamento_id = self.create_orcamento(cliente_id)
        print 'ID do orcamento criado: %s\n' % orcamento_id or 'Nao foi possivel criar o orcamento'
        venda_confirmada = False
        if orcamento_id:
            venda_confirmada = self.set_sale(orcamento_id)
        print 'Venda confirmada: %s' % 'Sim' if venda_confirmada else 'Nao'

    def new_connection(self):
        """
        O metodo estabalece a conexao com o Odoo.
        :return: objeto da conexao e id do usuario logado.
        :rtype: object
        """
        if not self.password:
            self.password = None
        try:
            sock_common = xmlrpclib.ServerProxy('https://' + self.host + '/xmlrpc/2/common')
            uid = sock_common.login(self.database, self.user, self.password)
            sock = xmlrpclib.ServerProxy('http://' + self.host + '/xmlrpc/2/object')
            return sock, uid
        except:
            print 'Nao foi possivel conectar ao Odoo!'
            exec exit()

    def create_cliente(self):
        """
        O metodo cria um novo cliente.
        :return: id da tabela res_partner
        :rtype: int
        """
        vals = {'name': 'Tiago Henrique Prates', 'email': 'tiagoprates_911@hotmail.com',
                'phone': '98233-7159', 'zip': '35700-000'}
        cliente_id = self.conn.execute_kw(self.database, self.uid, self.password,
                                          'res.partner', 'create', [vals])
        return cliente_id

    def update_cliente(self, cliente_id):
        """
        O metodo atualiza os dados de um registro.
        :param cliente_id: id da tabela res_partner, identificador do cliente.
        :type cliente_id: int
        :return: Verdadeiro, caso consiga realizar a atualizacao. Senao, Falso.
        :rtype: bool
        """
        vals = {'phone': '982648882'}  # Nao encontrei o campo RG, incluido CPF
        cliente_atualizado = self.conn.execute(self.database, self.uid, self.password,
                                               'res.partner', 'write', [cliente_id], vals)
        return cliente_atualizado

    def get_quantidade_cliente(self):
        """
        O metodo realiza a busca de registros.
        :return: Numero da quantidade total de clientes.
        :rtype: list
        """
        cliente_ids = self.conn.execute(self.database, self.uid, self.password, 'res.partner',
                                        'search', [])
        return len(cliente_ids)

    def get_cliente_dados(self):
        """
        O metodo encontra dados dos 10 primeiros clientes.
        :return: Descricao do nome, em ordem alfabetica, e da cidade dos clientes.
        :rtype: str
        """
        cliente_ids = self.conn.execute(self.database, self.uid, self.password, 'res.partner',
                                        'search', [], 0, 10, 'id')
        cliente_dados = self.conn.execute(self.database, self.uid, self.password, 'res.partner',
                                          'read', cliente_ids, ['name', 'city'])
        cliente_dados = sorted(cliente_dados, key=lambda n: n.get('name').lower())
        list_dados = list()
        map(lambda d: list_dados.append(
            '%s / %s' % (d.get('name'), d.get('city') or 'Nao cadastrado')), cliente_dados)
        return ' \n'.join(list_dados)

    def get_maior_venda_dados(self):
        """
        O metodo encontra os dados da maior venda realizada.
        :return: Descricao do nome do cliente e do valor total da venda.
        :rtype: str
        """
        sale_order_ids = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                           'search', [], 0, 1, 'amount_total DESC')
        sale_order_dados = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                             'read', sale_order_ids, ['partner_id', 'amount_total'])
        if not sale_order_dados:
            return ''
        if isinstance(sale_order_dados, (list, tuple)):
            sale_order_dados = sale_order_dados[0]
        return 'Cliente: %s / Total: %s\n' % (sale_order_dados.get('partner_id')[1],
                                              sale_order_dados.get('amount_total'))

    def get_produto_maior_venda_dados(self):
        """
        O metodo encontra os dados dos itens da maior venda.
        :return: Descricao dos nomes dos produtos e seu valor total.
        :rtype: str
        """
        sale_order_ids = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                           'search', [], 0, 1, 'amount_total DESC')
        sale_order_dados = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                             'read', sale_order_ids, ['order_line'])
        if not sale_order_dados:
            return ''
        if isinstance(sale_order_dados, (list, tuple)):
            sale_order_dados = sale_order_dados[0]
        order_line_dados = self.conn.execute(self.database, self.uid, self.password,
                                             'sale.order.line', 'read',
                                             sale_order_dados.get('order_line'),
                                             ['product_id', 'price_subtotal'])
        produto_dados = list()
        map(lambda d: produto_dados.append(
            '%s / %s' % (d.get('product_id')[1], d.get('price_subtotal'))), order_line_dados)
        return ' \n'.join(produto_dados)

    def get_percentual_de_vendas(self):
        """
        O metodo encontra o percentual de vendas confirmadas em relacao as cotacoes.
        :return: O valor percentual
        :rtype: float
        """
        sale_order_ids = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                           'search', [('state', 'in', ('draft', 'sale'))])
        sale_order_dados = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                             'read', sale_order_ids, ['amount_total', 'state'])
        if not sale_order_dados:
            return 0.00
        total_cotacao = sum(map(lambda c: c.get('amount_total'),
                                filter(lambda ct: ct.get('state') == 'draft', sale_order_dados)))
        total_venda = sum(map(lambda c: c.get('amount_total'),
                              filter(lambda ct: ct.get('state') == 'sale', sale_order_dados)))
        return round((total_cotacao / (total_venda or 1.0)) * 100, 2)

    def get_valor_total_faturas(self):
        """
        O metodo encontra o valor total das faturas do mes 06/2017.
        :return: Valor total das faturas
        :rtype: float
        """
        account_invoice_ids = self.conn.execute(
            self.database, self.uid, self.password, 'account.invoice', 'search',
            [('date_invoice', '>=', '2017-06-01'), ('date_invoice', '<=', '2017-06-30')])
        if not account_invoice_ids:
            return 0.00
        account_invoice_dados = self.conn.execute(
            self.database, self.uid, self.password, 'account.invoice', 'read', account_invoice_ids,
            ['residual'])
        account_invoice_total = sum(map(lambda a: a.get('residual') or 0, account_invoice_dados))
        return account_invoice_total

    def create_orcamento(self, cliente_id):
        """
        O metodo cria um orcamento.
        :param cliente_id: id da tabela res_partner, identificador do cliente.
        :return: id do orcamento
        :rtype: int
        """
        partner_invoice_id = self.conn.execute(self.database, self.uid, self.password,
                                               'res.partner', 'search', [], 0, 1) or False
        if partner_invoice_id:
            partner_invoice_id = partner_invoice_id[0]

        pricelist_id = self.conn.execute(self.database, self.uid, self.password,
                                         'product.pricelist', 'search', [], 0, 1) or False
        if pricelist_id:
            pricelist_id = pricelist_id[0]

        product_id = self.conn.execute(self.database, self.uid, self.password,
                                       'product.product', 'search', [], 0, 1) or False
        if product_id:
            product_id = product_id[0]

        product_uom_id = self.conn.execute(self.database, self.uid, self.password,
                                           'product.uom', 'search', [], 0, 1) or False
        if product_uom_id:
            product_uom_id = product_uom_id[0]

        if not all([cliente_id, partner_invoice_id, pricelist_id]):
            return False
        vals = {'partner_id': cliente_id, 'partner_invoice_id': partner_invoice_id,
                'patner_shipping_id': partner_invoice_id,
                'pricelist_id': pricelist_id}
        orcamento_id = self.conn.execute_kw(self.database, self.uid, self.password, 'sale.order',
                                            'create', [vals])
        vals = [{'product_id': product_id, 'product_uom': product_uom_id,
                 'name': 'Teste item orcamento', 'product_uom_qty': 10.00,
                 'price_unit': 10.00, 'order_id': orcamento_id}]
        if not all([product_uom_id, product_id, orcamento_id]):
            return False
        self.conn.execute_kw(self.database, self.uid, self.password, 'sale.order.line', 'create',
                             vals)
        return orcamento_id

    def set_sale(self, orcamento_id):
        """
        O metodo confirma a venda do orcamento recebido (orcamento_id).
        :param orcamento_id: id da tabela sale_order, identificador do orcamento.
        :return: Verdadeiro, caso a venda seja confirmada. Senao,  Falso.
        :rtype: bool
        """
        venda_confirmada = self.conn.execute(self.database, self.uid, self.password, 'sale.order',
                                             'action_confirm', orcamento_id)
        return venda_confirmada


ConexaoOdoo()
