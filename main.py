from io import TextIOWrapper
from os import unlink


class Fita:

    def __init__(self, numero) -> None:
        self._numero = numero
        self._nome = f"fita-{numero}.txt"
        self._grupos: list[int] = []
        self._registro = ""
        self._posicao = 0
        self._grupo_atual = 0
    
    @property
    def numero(self) -> int:
        return self._numero

    @property
    def nome(self) -> str:
        return self._nome
    
    @property 
    def grupos(self) -> list[int]:
        return self._grupos
    
    @property
    def registro(self) -> str:
        return self._registro
    
    @property
    def grupo_atual(self) -> int:
        return self._grupo_atual

    @property
    def registros(self) -> int:
        registros = 0
        for grupo in self._grupos:
            registros += grupo
        if self.registro != "":
            registros += 1
        return registros
    
    @property
    def vazio(self) -> bool:
        if self.registros == 0:
            return True
        return False
    
    def inserir_grupo(self, grupo: str) -> None:
        with open(self._nome, "a") as fita:
            fita.write(grupo)
        self._grupos.append(len(grupo))
    
    def limpar_para_escrita(self) -> None:
        with open(self._nome, "w") as fita:
            fita.write("")
        self._grupos = []

    def _ler(self) -> None:
        with open(self._nome, "r") as fita:
            fita.seek(self._posicao)
            self._registro = fita.read(1)
        self._grupos[self._grupo_atual] -= 1
        self._posicao += 1
    
    def abrir_para_leitura(self) -> None:
        self._ler()
    
    def ler_do_grupo_atual(self) -> None:
        if self._grupos[self._grupo_atual] > 0:
            self._ler()
        else:
            self._registro = ""
    
    def ler_do_proximo_grupo(self) -> None:
        if self._grupo_atual < len(self._grupos):
            self._grupo_atual += 1
            self._ler()
        else:
            self._registro = ""

    def abrir_para_escrita(self) -> None:
        with open(self._nome, "w") as fita:
            fita.write("")
        self._grupos.append(0)
    
    def escrever(self, registro: str) -> None:
        with open(self._nome, "a") as fita:
            fita.write(registro)
        if len(self._grupos) == 0:
            self._grupos.append(1)
        else:
            self._grupos[0] += 1

    def _transferir_para_saida(self) -> None:
        with open("fita-de-saida.txt", "w") as saida:
            saida.write("")
        for i in range(self.registros):
            with open(self._nome, "r") as temporario:
                temporario.seek(i)
                caractere = temporario.read(1)
                with open("fita-de-saida.txt", "a") as saida:
                    saida.write(f"{caractere} ")
    
    def apagar(self) -> None:
        if self.registros > 0:
            self._transferir_para_saida()
        unlink(self._nome)


class Ordenacao:

    def __init__(self, fita: TextIOWrapper, capacidade: int, unidades: int) -> None:
        self._entrada = fita
        self._capacidade = capacidade
        self._unidades = unidades
        self._ordenados = 0
        self._get_tamanho()
        self._fitas: list[Fita] = []
        self._criar_fitas_temporarias()
        self._ordenar()
        self._abrir_para_leitura()
        self._abrir_para_escrita()
        self._intercalar()
        self._apagar_temporarios()
    
    def _get_tamanho(self) -> None:
        self._entrada.seek(0, 2)
        self._tamanho = self._entrada.tell() / 2
        self._entrada.seek(0)

    def _criar_fitas_temporarias(self) -> None:
        for unidade in range(self._unidades):
            self._fitas.append(Fita(unidade + 1))
    
    def _ordenar(self) -> None:
        fita = 0
        while self._ordenados < self._tamanho:
            grupo = self._entrada.read(self._capacidade * 2).split(' ')[:self._capacidade]
            grupo.sort()
            self._fitas[fita % (self._unidades // 2)].inserir_grupo(''.join(grupo))
            self._ordenados += len(grupo)
            fita += 1
    
    def _todos_em_uma_fita(self) -> bool:
        vazios = 0
        for fita in self._fitas:
            if fita.vazio:
                vazios += 1
        return vazios == self._unidades - 1
    
    def _abrir_para_leitura(self) -> None:
        self._em_leitura: list[int] = []
        for i in range(self._unidades):
            if len(self._fitas[i].grupos) > 0:
                self._em_leitura.append(i)
                self._fitas[i].abrir_para_leitura()
    
    def _abrir_para_escrita(self) -> None:
        for i in range(self._unidades):
            if len(self._fitas[i].grupos) == 0:
                self._fitas[i].abrir_para_escrita()
                self._em_escrita = i
                break
    
    def _menor(self) -> str:
        indice = 0
        menor = self._fitas[indice].registro
        for i in self._em_leitura:
            registro = self._fitas[i].registro
            if (registro != "" and registro <= menor) or menor == "":
                indice = i
                menor = registro
        self._fitas[indice].ler_do_grupo_atual()
        return menor
    
    def _sem_registro_no_grupo_atual(self) -> bool:
        sem_registro_no_grupo_atual = 0
        for i in self._em_leitura:
            if self._fitas[i].grupos[self._fitas[i].grupo_atual] == 0 and self._fitas[i].registro == "":
                sem_registro_no_grupo_atual += 1
        return sem_registro_no_grupo_atual == self._unidades // 2
    
    def _mudar_em_escrita(self) -> None:
        for i in range(len(self._em_leitura)):
            self._fitas[i].ler_do_proximo_grupo()
        self._em_escrita += 1
    
    def _intercalacao_atual_finalizada(self) -> None:
        fitas_sem_registro = 0
        for i in self._em_leitura:
            if self._fitas[i].vazio:
                fitas_sem_registro += 1
        return fitas_sem_registro == self._unidades // 2
    
    def _mudar_em_leitura(self) -> None:
        self._em_leitura = []
        for i in range(self._unidades):
            if not self._fitas[i].vazio:
                self._fitas[i].abrir_para_leitura()
                self._em_leitura.append(i)
            else:
                self._fitas[i].limpar_para_escrita()
    
    def _apagar_temporarios(self) -> None:
        for fita in self._fitas:
            fita.apagar()

    
    def _intercalar(self) -> None:
        iteracao = 0
        while True:
            self._fitas[self._em_escrita].escrever(self._menor())
            if iteracao == 50:
                break
            if self._intercalacao_atual_finalizada():
                if self._todos_em_uma_fita():
                    break
                else:
                    self._mudar_em_leitura()
                    self._abrir_para_escrita()
            elif self._sem_registro_no_grupo_atual():
                self._mudar_em_escrita()
            iteracao += 1


with open("fita-de-entrada.txt", "r") as fita:
    Ordenacao(fita, 3, 6)