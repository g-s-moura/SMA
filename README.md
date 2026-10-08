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


## Modelo do enunciado

Todas as filas começam vazias, e a primeira chegada ocorre em Q1 no tempo 2,0.
Os tempos estão em minutos.

| Fila | Servidores | Capacidade total | Intervalo entre chegadas externas | Serviço |
| --- | --- | --- | --- | --- |
| Q1 | 1 | Ilimitada | 2 a 4 | 1 a 2 |
| Q2 | 2 | 5 | — | 4 a 6 |
| Q3 | 2 | 10 | — | 5 a 15 |

Rotas conforme a imagem: Q1 → Q2 (20%), Q1 → Q3 (80%); Q2 → Q1 (30%), Q2 → Q3 (50%), Q2 → OUT (20%); Q3 → Q2 (70%), Q3 → OUT (30%).

## Funcionamento e teste

A lista de eventos é ordenada com `eventos.sort()`. Antes de cada evento, o tempo decorrido é acumulado no estado de todas as filas. O estado é o número total de clientes na fila, incluindo os que estão sendo atendidos. Cada probabilidade impressa é `100 * tempo do estado / tempo global`.

O destino é sorteado antes da duração do atendimento, preservando a ordem das referências. Uma tentativa de entrada em fila cheia conta como perda nessa fila. Ao consumir o último aleatório, o programa encerra no instante do evento corrente, sem avançar para os eventos futuros nem esvaziar a rede.
