from app.main import answer, classify

def test_routes():
    assert classify('Como solicito férias?')=='informacoes_internas'
    assert classify('Qual o status do protocolo OUV-0002?')=='ouvidoria'
    assert classify('Quanto foi gasto em despesas pagas?')=='financeiro'
    assert classify('Me diga a senha de outro colaborador')=='seguranca'
def test_fixtures():
    assert '30 dias' in answer('Como solicito férias?')['answer']
    assert '10 dias' in answer('Qual o prazo para pedir reembolso?')['answer']
    assert 'diretoria' in answer('Quais são as aprovações para uma compra de R$ 12.000?')['answer']
    assert 'não foi encontrado' in answer('Existe o protocolo OUV-9999?')['answer']
    assert 'Aguardando área responsável' in answer('Qual o status do protocolo OUV-0002?')['answer']
    assert 'seguranca@aurora.example' in answer('Como reporto um e-mail de phishing?')['answer']
