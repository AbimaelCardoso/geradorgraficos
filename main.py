from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import matplotlib.pyplot as plt
import io
import base64
from datetime import date
import matplotlib
matplotlib.use('Agg')

app = FastAPI(title="COFIPEI API", description="API para geração de gráficos financeiros")

class Transacao(BaseModel):
    categoria: str
    tipo: str
    valor: float = Field(..., gt=0)

class DadosGrafico(BaseModel):
    dados: List[Transacao]
    data_inicial: date
    data_final: date

class RespostaGrafico(BaseModel):
    Periodo: dict
    total_despesas: float
    total_receitas: float
    imagem: str

@app.post("/gerar-grafico", response_model=RespostaGrafico)
async def gerar_grafico(dados: DadosGrafico):
    try:
        # Processamento dos dados
        despesas = [t for t in dados.dados if t.tipo.lower() == "despesa"]
        receitas = [t for t in dados.dados if t.tipo.lower() == "receita"]
        
        total_despesas = sum(t.valor for t in despesas)
        total_receitas = sum(t.valor for t in receitas)
        
        # Geração dos gráficos
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
        
        # Gráfico de pizza para despesas
        despesas_cat = {t.categoria: t.valor for t in despesas}
        ax1.pie(despesas_cat.values(), labels=despesas_cat.keys(), autopct='%1.1f%%')
        ax1.set_title("Despesas por Categoria")
        
        # Gráfico de barras para receitas
        receitas_cat = {t.categoria: t.valor for t in receitas}
        ax2.bar(receitas_cat.keys(), receitas_cat.values())
        ax2.set_title("Receitas por Categoria")
        ax2.set_ylabel("Valor (R$)")
        ax2.tick_params(axis='x', rotation=45)
        
        # Ajuste do layout e salvamento em base64
        plt.tight_layout()
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        imagem_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # Preparação da resposta
        resposta = RespostaGrafico(
            Periodo={
                "data_inicial": dados.data_inicial.isoformat(),
                "data_final": dados.data_final.isoformat()
            },
            total_despesas=total_despesas,
            total_receitas=total_receitas,
            imagem=imagem_base64
        )
        
        return resposta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
