document.addEventListener('DOMContentLoaded', function () {
    const contentDiv = document.getElementById('content');

    // Função para exibir a lista de funcionários
    function exibirFuncionarios() {
        // solicitação AJAX para obter dados do servidor Flask
        fetch('/get-funcionarios', {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            contentDiv.innerHTML = '';

            const funcionarios = data || [];
            funcionarios.forEach(funcionario => {
                const funcionarioInfo = `
                    <p class="highlight">
                        Matrícula: ${funcionario['Matrícula']}<br>
                        Nome: ${funcionario['Nome']}<br>
                        Setor: ${funcionario['Setor']}<br>
                        Turno: ${funcionario['Turno']}<br>
                    </p>
                `;
                contentDiv.innerHTML += funcionarioInfo;
            });
        })
        .catch(error => console.error('Erro:', error));
    }

    // Função para abrir a página de cadastrar funcionário
    function openCadastrarFuncionarioPage() {
        fetch('/cadastrar-funcionario')
            .then(response => response.text())
            .then(data => {
                contentDiv.innerHTML = data;
            })
            .catch(error => console.error('Erro:', error));
    }

    // Adicione um ouvinte de evento para o botão "Exibir Funcionários"
    document.getElementById('exibir_funcionarios').addEventListener('click', function () {
        // Redireciona para a rota Flask que renderiza a página de lista de funcionários
        window.location.href = '/exibir_funcionarios';
    });

    // Evento de clique para o botão "Cadastrar Funcionário"
    document.getElementById('cadastrarFuncionario').addEventListener('click', function () {
        openCadastrarFuncionarioPage();
    });
    function getMatriculaFromURL() {
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        return urlParams.get('matricula');
    }
    const matriculaDoFuncionario = getMatriculaFromURL();
    console.log(matriculaDoFuncionario);
});
