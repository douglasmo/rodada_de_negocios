
# 🧩 Gerador de Rodadas de Negócios

Aplicação em Python com interface gráfica (Tkinter) que organiza **rodadas de negócios** com base no número de participantes, mesas, cadeiras por mesa e rodadas. O objetivo é **maximizar a troca de contatos entre os participantes**, evitando repetições de duplas em mesas diferentes.

Ideal para eventos corporativos, encontros de networking, feiras e cooperativas como o Sicredi.

---

## ✅ Funcionalidades

- Interface intuitiva e leve usando **Tkinter**
- Validações automáticas de capacidade e entradas numéricas
- Algoritmo que **minimiza repetições entre participantes**
- Geração de:
  - 🖼️ **Imagens individuais** por participante com sua agenda
  - 📊 **Planilha Excel** com visão geral das mesas por rodada
  - 📄 **PDF final** compilando todas as agendas

---

## 📦 Instalação

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/gerador-rodadas-negocios.git
cd gerador-rodadas-negocios
````

2. Instale as dependências:

```bash
pip install pandas matplotlib openpyxl pillow
```

> Obs: `openpyxl` ou `xlsxwriter` podem ser usados para salvar Excel; `Pillow` é usado para gerar o PDF com imagens.

---

## ▶️ Como usar

1. Execute o script:

```bash
python gerador_rodadas_negocios.py
```

2. Preencha os campos:

* **Nº de Participantes (N)**
* **Nº de Mesas (M)**
* **Cadeiras por Mesa (C)**
* **Nº de Rodadas (R)**

3. Clique em **"Gerar Rodadas"**

4. Os arquivos serão exportados automaticamente para:

```bash
~/Downloads/rodada_de_negocio/
```

---

## 📂 Arquivos Gerados

| Tipo                        | Caminho                                | Conteúdo                                  |
| --------------------------- | -------------------------------------- | ----------------------------------------- |
| `resumo_rodadas_geral.xlsx` | `Downloads/rodada_de_negocio/`         | Planilha com visão geral por participante |
| `Participante_X.png`        | `Downloads/rodada_de_negocio/imagens/` | Imagens individuais de cada agenda        |
| `agendas_compiladas.pdf`    | `Downloads/rodada_de_negocio/`         | PDF com todas as agendas reunidas         |

---

## 🧠 Lógica do Algoritmo

O script utiliza uma estratégia otimizada baseada em:

* **Geração aleatória com restrições**
* Verificação de pares já encontrados entre participantes
* Seleção da melhor distribuição possível para cada rodada com menor colisão

---

## 🛡️ Validações Inclusas

* Números inteiros positivos obrigatórios
* Capacidade total ≥ número de participantes
* Mínimo de 2 cadeiras por mesa
* Barra de progresso e mensagens de status dinâmicas

---


## 🧑‍💻 Autor

Desenvolvido por \ Douglas 
Projeto open-source sob licença MIT

---

## 🪪 Licença

Este projeto está licenciado sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.
