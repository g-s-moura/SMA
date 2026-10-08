## Aluno

Gabriel Silva de Moura

## Como executar

É necessário ter Python 3 e PyYAML. Se o PyYAML ainda não estiver instalado:

```bash
python3 -m pip install pyyaml
```

Abra o terminal na pasta dos arquivos e execute:

```bash
python3 simulador.py
```

Para usar outro modelo ou salvar a saída:

```bash
python3 simulador.py outro-modelo.yml
python3 simulador.py modelo.yml > resultados.txt
```

## Configuração

- `arrivals`: nome da fila e instante da primeira chegada externa. Pode haver entradas em diferentes filas.
- `queues`: filas, com `servers`, `minService` e `maxService`. `capacity` inclui clientes em atendimento e em espera; sua ausência significa capacidade ilimitada. `minArrival` e `maxArrival` definem os intervalos entre chegadas externas à fila; se ausentes, não são agendadas novas chegadas externas.
- `network`: conexões com `source`, `target` e `probability`. `OUT` representa a saída do sistema. Se a soma das probabilidades for menor que 1, o restante é saída. Uma fila sem conexões também envia seus clientes para fora. Use probabilidades entre 0 e 1, cuja soma por origem não ultrapasse 1, e nomes de filas existentes.
- `seeds`: lista de sementes; esta implementação usa a primeira, para uma execução por chamada.
- `rndnumbersPerSeed`: limite de aleatórios utilizados nessa execução.
- `rndnumbers`: lista fixa de aleatórios em [0, 1), para comparação com a referência. Para utilizá-la, remova `seeds`; a simulação termina ao consumir a lista. Quando `seeds` existe, a lista fixa é ignorada.
