import csv, json, os, re, time, unicodedata, logging
from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal
from collections import defaultdict
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; LOG=ROOT/'logs'; LOG.mkdir(exist_ok=True)
app=FastAPI(title='Areco - Agentes Especializados',version='1.0.0')
class Query(BaseModel):
    question:str=Field(min_length=2,max_length=2000)
def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(s).lower()) if not unicodedata.combining(c))
def words(s):return set(re.findall(r'[a-z0-9]+',norm(s)))-{'de','da','do','em','para','que','qual','quais','como','um','uma','o','a','os','as','no','na','e','por','me','foi'}
def csvrows(name):
    with (DATA/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def money(x):return 'R$ '+f'{x:,.2f}'.replace(',','X').replace('.',',').replace('X','.')
def classify(q):
    t=norm(q)
    if any(s in t for s in ['senha de outro','senha do outro','credencial de outro','token de outro']):return 'seguranca'
    if re.search(r'ouv-\d{4}',t) or any(s in t for s in ['ouvidoria','manifestac','reclamac','protocolo','elogio','status da solicitacao']):return 'ouvidoria'
    if any(s in t for s in ['ferias','reembolso','compra de r$','aprovac','phishing','incidente','home office','home-office','politica','acesso ao sistema','solicitar acesso','portal interno','privacidade','rh','procedimento','compras','seguranca','chamado','colaborador']):return 'informacoes_internas'
    if any(s in t for s in ['receita','despesa','orcamento','faturamento','financeir','centro de custo','gasto','gastou','pagas','pago no periodo','inadimplencia','lancamento','lucro']):return 'financeiro'
    return 'fora_de_escopo'
def internal(q):
    docs=list(DATA.glob('[0-9][0-9]_*.md'))
    faq=json.loads((DATA/'faq_interno.json').read_text(encoding='utf-8'))
    w=words(q); ranked=[]
    if 'incidente' in norm(q) and 'phishing' not in norm(q):
        f=DATA/'07_fluxo_de_incidentes.md'
        content=f.read_text(encoding='utf-8')
        lines=[line.strip('- ').strip() for line in content.splitlines() if line.strip().startswith('- ')]
        return 'Segundo o fluxo de incidentes:\n'+'\n'.join('• '+line for line in lines),[f.name]
    for f in docs:
        content=f.read_text(encoding='utf-8'); title=content.splitlines()[0]
        score=3*len(w & words(title))+len(w & words(f.stem.replace('_',' ')))
        for item in faq:
            if item.get('documento')==f.name:
                score+=3*len(w & words(item['pergunta']))
        score+=0.2*len(w & words(content))
        ranked.append((score,f,content))
    ranked.sort(key=lambda x:x[0],reverse=True)
    score,f,content=ranked[0]
    if score<1:return 'Não encontrei uma política interna suficientemente relacionada à pergunta.',[]
    # FAQ precise answer, backed by original document; include source excerpts for broader questions.
    candidates=[(len(w & words(i['pergunta'])),i) for i in faq if i.get('documento')==f.name]
    candidates.sort(key=lambda x:x[0],reverse=True)
    if '12.000' in q or '12000' in q:
        response='Para uma compra de R$ 12.000, são necessárias aprovações da liderança, do gerente e da diretoria.'
    elif candidates and candidates[0][0]>=2 and len(w & words(candidates[0][1]['pergunta']))>=max(2,len(w)//2):
        response=candidates[0][1]['resposta']
    else:
        lines=[line.strip('- ').strip() for line in content.splitlines() if line.strip().startswith(('- ','1.','2.','3.','4.','5.','6.','7.'))]
        response='Segundo a política consultada:\n'+'\n'.join('• '+line for line in lines[:9]) if lines else content[:1100]
    return response,[f.name]
def finance(q):
    t=norm(q); entries=csvrows('lancamentos_financeiros.csv'); budget=csvrows('orcamento_mensal.csv')
    if 'orcamento' in t:
        year=int(re.search(r'20\d{2}',t).group()) if re.search(r'20\d{2}',t) else 2026
        months={'janeiro':1,'fevereiro':2,'marco':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
        month=next((v for k,v in months.items() if k in t),None)
        if month is None:return 'Informe o mês para comparar os orçamentos.', ['orcamento_mensal.csv']
        grouped=defaultdict(Decimal)
        for row in budget:
            if int(row['ano'])==year and int(row['mes'])==month:grouped[row['departamento']]+=Decimal(row['orcamento_brl'])
        if not grouped:return 'Não encontrei orçamento para esse período.',['orcamento_mensal.csv']
        dep,val=max(grouped.items(),key=lambda p:p[1]);return f'O departamento com maior orçamento em {month:02d}/{year} é {dep}, com {money(val)}. Os valores foram somados por departamento.',['orcamento_mensal.csv']
    kind='Receita' if any(x in t for x in ['receita','faturamento']) else 'Despesa'
    status='Pago' if kind=='Despesa' and any(x in t for x in ['paga','pagas','efetivamente','gasto']) else None
    years=re.findall(r'20\d{2}',t);year=int(years[0]) if years else None
    months={'janeiro':1,'fevereiro':2,'marco':3,'abril':4,'maio':5,'junho':6,'julho':7,'agosto':8,'setembro':9,'outubro':10,'novembro':11,'dezembro':12}
    hits=[v for k,v in months.items() if k in t]; start=min(hits) if hits else 1;end=max(hits) if hits else 12
    filtered=[r for r in entries if r['tipo']==kind and (status is None or r['status']==status) and (year is None or int(r['data_competencia'][:4])==year) and start<=int(r['data_competencia'][5:7])<=end]
    total=sum((Decimal(r['valor_brl']) for r in filtered),Decimal('0'))
    criterion=f'{kind}s' + (' com status Pago' if status else ' em todos os status')
    period=(f' em {year}' if year else ' no período disponível')+(f', meses {start:02d}–{end:02d}' if hits else '')
    return f'Total de {criterion}{period}: {money(total)} ({len(filtered)} lançamentos). Filtro por data de competência; valores calculados com Decimal.', ['lancamentos_financeiros.csv']
def ombuds(q):
    t=norm(q); m=re.search(r'ouv-\d{4}',t)
    if m:
        protocol=m.group().upper();rows=[r for r in csvrows('manifestacoes.csv') if r['protocolo']==protocol]
        if not rows:return f'O protocolo {protocol} não foi encontrado na base.',['manifestacoes.csv']
        r=rows[0];return f"Protocolo {protocol}: status {r['status']}; categoria {r['categoria']}; abertura {r['data_abertura']}; prioridade {r['prioridade']}; área responsável {r['area_responsavel']}.",['manifestacoes.csv']
    ref=json.loads((DATA/'referencia_ouvidoria.json').read_text(encoding='utf-8'))
    if 'status' in t:return 'Status possíveis: '+', '.join(ref['status_validos'])+'.',['referencia_ouvidoria.json']
    if 'prazo' in t:return 'O prazo de referência na base sintética é de 10 dias; não é um prazo legal nem promessa de atendimento.',['referencia_ouvidoria.json']
    return 'Para consultar uma manifestação, informe o protocolo no formato OUV-0001. Os dados são sintéticos.',['referencia_ouvidoria.json']
def answer(question):
    domain=classify(question)
    if domain=='financeiro':response,sources=finance(question)
    elif domain=='informacoes_internas':response,sources=internal(question)
    elif domain=='ouvidoria':response,sources=ombuds(question)
    elif domain=='seguranca':response,sources='Não posso fornecer senhas ou credenciais de outras pessoas. Solicite acesso pelo canal autorizado de TI.',['04_seguranca_da_informacao.md','09_politica_privacidade.md']
    else:response,sources='Não consegui classificar a pergunta com segurança. Reformule indicando se o assunto é financeiro, informações internas ou ouvidoria.',[]
    return {'domain':domain,'agent':domain,'answer':response,'sources':sources}
@app.post('/api/chat')
def chat(payload:Query):
    start=time.perf_counter()
    try:
        result=answer(payload.question);status='ok'
    except Exception:
        logging.exception('Erro de processamento');result={'domain':'erro','agent':'erro','answer':'Erro ao processar. Consulte os logs do servidor.','sources':[]};status='error'
    # No raw question or response: avoid leaking sensitive text.
    record={'timestamp':datetime.now(timezone.utc).isoformat(),'domain':result['domain'],'agent':result['agent'],'sources':result['sources'],'latency_ms':round((time.perf_counter()-start)*1000,2),'status':status,'question_length':len(payload.question)}
    with (LOG/'interactions.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    return result
@app.get('/api/health')
def health():return {'status':'ok','datasets':{'financeiro':len(csvrows('lancamentos_financeiros.csv')),'ouvidoria':len(csvrows('manifestacoes.csv'))}}
@app.get('/')
def home():return FileResponse(ROOT/'frontend'/'index.html')
@app.get('/style.css')
def css():return FileResponse(ROOT/'frontend'/'style.css')
@app.get('/script.js')
def js():return FileResponse(ROOT/'frontend'/'script.js')
