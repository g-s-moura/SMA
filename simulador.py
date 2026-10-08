# Simulador configurável de redes de filas
import sys
import yaml


# Leitor para aceitar o !PARAMETERS
class ParametersLoader(yaml.SafeLoader):
    pass


def parameters_constructor(loader, node):
    return loader.construct_mapping(node, deep=True)


ParametersLoader.add_constructor('!PARAMETERS', parameters_constructor)

# Parâmetros do gerador congruente linear
pA = 1664525
pC = 1013904223
pM = 2**32
seed = 1
numbers_gen = 0
n_max = 100000
rndnumbers = []
usar_rndnumbers = False


def next_random():
    """Obtém um aleatório sem ultrapassar o limite da simulação."""
    global seed, numbers_gen

    if numbers_gen >= n_max:
        return None

    if usar_rndnumbers:
        valor = rndnumbers[numbers_gen]
    else:
        seed = (pA * seed + pC) % pM
        valor = seed / pM

    numbers_gen += 1
    return valor


def simular_rede(modelo):
    global seed, numbers_gen, n_max, rndnumbers, usar_rndnumbers

    with open(modelo, 'r', encoding='utf-8') as file:
        config = yaml.load(file, Loader=ParametersLoader)

    # Reinicia os aleatórios a cada execução. Usa uma semente por simulação.
    numbers_gen = 0
    usar_rndnumbers = 'rndnumbers' in config and 'seeds' not in config
    rndnumbers = config.get('rndnumbers', []) if usar_rndnumbers else []
    seed = config.get('seeds', [1])[0]
    n_max = len(rndnumbers) if usar_rndnumbers else config.get('rndnumbersPerSeed', 100000)

    filas = config['queues']
    roteamento = {q: [] for q in filas}
    for rota in config.get('network', []):
        roteamento[rota['source']].append((rota['target'], rota['probability']))

    # Todas as filas começam vazias.
    estado_atual = {q: 0 for q in filas}
    clientes_perdidos = {q: 0 for q in filas}
    tempos_estados = {q: {} for q in filas}
    tempo_global = 0.0
    eventos = []  # (tempo, tipo_evento, fila_origem, destino)

    for fila, tempo in config.get('arrivals', {}).items():
        eventos.append((tempo, 'CHEGADA_EXTERNA', fila, 'OUT'))

    def escolher_destino(fila):
        # Sem rotas, o cliente sai sem gastar aleatório de roteamento.
        if not roteamento[fila]:
            return 'OUT'

        rnd = next_random()
        if rnd is None:
            return None

        soma_acumulada = 0.0
        for destino, prob in roteamento[fila]:
            soma_acumulada += prob
            if rnd < soma_acumulada:
                return destino
        return 'OUT'  # Probabilidade restante: saída do sistema.

    def agendar_saida(fila, tempo):
        # Mantém a ordem da referência: destino antes do tempo de serviço.
        destino = escolher_destino(fila)
        if destino is None or numbers_gen >= n_max:
            return False

        rnd = next_random()
        if rnd is None:
            return False
        min_s = filas[fila]['minService']
        max_s = filas[fila]['maxService']
        t_serv = min_s + (max_s - min_s) * rnd
        eventos.append((tempo + t_serv, 'SAIDA', fila, destino))
        return numbers_gen < n_max

    def tratar_chegada(fila, tempo):
        cap = filas[fila].get('capacity', float('inf'))
        servs = filas[fila]['servers']

        if estado_atual[fila] < cap:
            estado_atual[fila] += 1
            if estado_atual[fila] <= servs:
                return agendar_saida(fila, tempo)
        else:
            clientes_perdidos[fila] += 1
        return True

    # Loop principal: processa sempre o evento de menor tempo.
    while eventos and numbers_gen < n_max:
        eventos.sort()
        tempo_atual, tipo_evento, fila, destino = eventos.pop(0)

        # Acumula o tempo de TODAS as filas antes de alterar os estados.
        var_tempo = tempo_atual - tempo_global
        for q in filas:
            est = estado_atual[q]
            tempos_estados[q][est] = tempos_estados[q].get(est, 0.0) + var_tempo
        tempo_global = tempo_atual

        if tipo_evento == 'CHEGADA_EXTERNA':
            if not tratar_chegada(fila, tempo_atual):
                break

            min_c = filas[fila].get('minArrival')
            max_c = filas[fila].get('maxArrival')
            if min_c is not None and max_c is not None:
                rnd = next_random()
                if rnd is None:
                    break
                t_chegada = min_c + (max_c - min_c) * rnd
                eventos.append((tempo_atual + t_chegada, 'CHEGADA_EXTERNA', fila, 'OUT'))

        elif tipo_evento == 'SAIDA':
            estado_atual[fila] -= 1

            # O servidor liberado atende o próximo cliente que estava esperando.
            if estado_atual[fila] >= filas[fila]['servers']:
                if not agendar_saida(fila, tempo_atual):
                    break

            # Na passagem, eventual perda pertence à fila de destino.
            if destino != 'OUT':
                if not tratar_chegada(destino, tempo_atual):
                    break

    print('RESULTADOS DA SIMULAÇÃO')
    print(f'Tempo Global de Simulação: {tempo_global:.4f}')
    print(f'Números Aleatórios Utilizados: {numbers_gen}')
    print(f'Total de Clientes Perdidos: {sum(clientes_perdidos.values())}')

    for q in filas:
        print(f'\nResultado da fila {q}')
        print(f'Clientes Perdidos na fila {q}: {clientes_perdidos[q]}')
        cap = filas[q].get('capacity')
        maior_estado = cap if cap is not None else max(tempos_estados[q], default=0)
        for est in range(maior_estado + 1):
            tempo_acumulado = tempos_estados[q].get(est, 0.0)
            probabilidade = 100 * tempo_acumulado / tempo_global if tempo_global > 0 else 0
            print(f'{est:>2} clientes: Tempo = {tempo_acumulado:.4f} | Prob = {probabilidade:.4f}%')


if __name__ == '__main__':
    simular_rede(sys.argv[1] if len(sys.argv) > 1 else 'modelo.yml')
