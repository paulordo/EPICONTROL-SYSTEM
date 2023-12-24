from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime
from flask import abort

app = Flask(__name__)

# Lista para armazenar os funcionários
funcionarios = []

# Dicionário para armazenar as requisições de EPIs com histórico de datas
requisicoes_epi = {}

# variável para armazenar a última matrícula cadastrada
ultima_matricula = None
ultimo_nome = None

@app.route('/requisitar_epi.html', methods=['GET', 'POST'])
def requisitar_epi_page():
    if request.method == 'POST':
        matricula = request.form.get('matricula')
        epi = request.form.get('epi')
        quantidade_str_form = request.form.get('quantidade')
        tamanho = request.form.get('tamanho')  # Para o campo de texto 'tamanho'
        dropdown_tamanho = request.form.get('dropdown-tamanho')  # Para o dropdown 'tamanho'

        if not matricula or not epi:
            return render_template('requisitar_epi.html', error='Matrícula e EPI são obrigatórios.')

        quantidade_str_form = quantidade_str_form or None

        try:
            quantidade = int(quantidade_str_form)
        except ValueError:
            return render_template('requisitar_epi.html', error='A quantidade deve ser um número inteiro.')

        funcionario = next((f for f in funcionarios if f['Matrícula'] == matricula), None)

        if not funcionario:
            return render_template('funcionario_nao_encontrado.html', matricula=matricula)

        # Use o valor correto dependendo do tipo de EPI selecionado
        tamanho_selecionado = dropdown_tamanho if epi == 'Botas' else tamanho

        requisitar_epi_individual(matricula, epi, quantidade, tamanho_selecionado)

        return render_template('requisicao_epi_sucesso.html', matricula=matricula, epi=epi, quantidade=quantidade, tamanho=tamanho_selecionado)

    return render_template('requisitar_epi.html')

@app.route('/excluir-historico/<matricula>/<epi>/<data>')
def excluir_historico(matricula, epi, data):
    global funcionarios, requisicoes_epi

    funcionario = next((f for f in funcionarios if f['Matrícula'] == matricula), None)

    if not funcionario:
        return f"Funcionário com matrícula {matricula} não encontrado."

    if 'Histórico' in funcionario:
        # Filtra o histórico para manter apenas os itens que não correspondem ao EPI e à data fornecidos
        funcionario['Histórico'] = [h for h in funcionario['Histórico'] if not (h['EPI'] == epi and h['Data'] == data)]

        # Atualiza as requisições_epi para refletir a alteração no histórico
        if matricula in requisicoes_epi and epi in requisicoes_epi[matricula]:
            requisicoes_epi[matricula][epi]['Data'] = [d for d in requisicoes_epi[matricula][epi]['Data'] if d['Data'] != data]

    return redirect(url_for('exibir_funcionarios_page'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/exibir_funcionarios')
def exibir_funcionarios_page():
    return render_template('exibir_funcionarios.html', funcionarios=funcionarios)

                           
@app.route('/get-funcionarios', methods=['GET'])
def get_funcionarios():
    return render_template('exibir_funcionarios.html', funcionarios=funcionarios)

@app.route('/cadastrar-funcionario', methods=['GET', 'POST'])
def cadastrar_funcionario_page():
    error_message = None

    if request.method == 'POST':
        matricula = request.form.get('matricula')
        nome = request.form.get('nome')
        setor = request.form.get('setor')
        turno = request.form.get('turno')

        # Verificar se a matrícula já existe
        if any(funcionario['Matrícula'] == matricula for funcionario in funcionarios):
            error_message = "Matrícula já existente. Tente novamente."
        else:
            # Dicionário para representar o novo funcionário
            novo_funcionario = {"Matrícula": matricula, "Nome": nome, "Setor": setor, "Turno": turno}

            # Adicionando o funcionário à lista
            funcionarios.append(novo_funcionario)

            # Atualiza a última matrícula e nome
            global ultima_matricula, ultimo_nome
            ultima_matricula = matricula
            ultimo_nome = nome

            return render_template('cadastro_sucesso.html', matricula=ultima_matricula, nome=ultimo_nome)

    # Se o método for GET ou se houver um erro, renderize a página do formulário
    return render_template('cadastrar_funcionario.html', error_message=error_message, ultima_matricula=ultima_matricula, ultimo_nome=ultimo_nome)

@app.route('/cadastro-sucesso')
def cadastro_sucesso():
    return render_template('cadastro_sucesso.html', ultima_matricula=ultima_matricula, ultimo_nome=ultimo_nome)



@app.route('/data', methods=['POST'])
def get_data():
    data = {"funcionarios": funcionarios, "requisicoes_epi": requisicoes_epi}
    return jsonify(data)

# Função para gerar nomes diferentes
def gerar_nome(i):
    return f"Funcionário {i}"

# Função para povoar funcionários de 1 a 5
def povoar_funcionarios():
    for i in range(1, 6):
        matricula = str(0 + i)
        nome = gerar_nome(i)
        setor = f"Setor {i % 5}"
        turno = "Manhã" if i % 2 == 0 else "Tarde"

        # Dicionário para representar o funcionário
        funcionario = {"Matrícula": matricula, "Nome": nome, "Setor": setor, "Turno": turno}

        # Adicionando o funcionário à lista
        funcionarios.append(funcionario)

def requisitar_epi_individual(matricula, epi, quantidade, tamanho=None):
    funcionario = next((f for f in funcionarios if f['Matrícula'] == matricula), None)

    if not funcionario:
        return f"Funcionário com matrícula {matricula} não encontrado."

    data_requisicao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    requisicoes_epi.setdefault(matricula, {}).setdefault(epi, {"Quantidade": 0, "Data": []})
    requisicoes_epi[matricula][epi]["Quantidade"] += quantidade
    requisicoes_epi[matricula][epi]["Data"].append({"Data": data_requisicao, "Quantidade": quantidade, "Tamanho": tamanho})

    # Adiciona a requisição ao histórico do funcionário
    funcionario.setdefault('Histórico', []).append({
        "EPI": epi,
        "Quantidade": quantidade,
        "Data": data_requisicao,
        "Tamanho": tamanho
    })

    mensagem_sucesso = f"{quantidade} {epi}(s) requisitado(s) com sucesso para o funcionário de matrícula {matricula}!"
    return mensagem_sucesso

@app.route('/excluir-funcionario/<matricula>')
def excluir_funcionario(matricula):
    global funcionarios
    funcionarios = [f for f in funcionarios if f['Matrícula'] != matricula]
    return redirect(url_for('exibir_funcionarios_page'))

# Função para exibir funcionários
def exibir_funcionarios():
    print("\nLista de Funcionários:")
    for i, funcionario in enumerate(funcionarios, start=1):
        print("------------------------------------------------"
              f"\n{i}. Matrícula: {funcionario['Matrícula']}"
              f"\nNome: {funcionario['Nome']},"
              f"\nSetor: {funcionario['Setor']},"
              f"\nTurno: {funcionario['Turno']}")

        if funcionario['Matrícula'] in requisicoes_epi:
            print("  EPIs Requisitados\n>>")
            for epi, historico in requisicoes_epi[funcionario['Matrícula']].items():
                print(f"    - {epi}:")
                for requisicao in historico["Data"]:
                    if "Tamanho do Calçado" in requisicao:
                        print(f"      Tamanho do Calçado: {requisicao['Tamanho do Calçado']}, Data: {requisicao['Data']}")
                    else:
                        print(f"      Data: {requisicao['Data']}, Quantidade: {requisicao['Quantidade']}")

    print()

if __name__ == "__main__":
    povoar_funcionarios()  # Adiciona automaticamente funcionários à lista
    app.run(debug=False)
