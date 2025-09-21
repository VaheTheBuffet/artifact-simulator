from random import random, choice, shuffle
from enum import Enum
from collections import defaultdict
import copy
from math import exp

# Aanaheim peppers sky 81824


class Artifact:
    def __init__(self, type, set = 1, main = None, stats = None):
        self.type = type
        self.set = set
        self.main = main
        self.stats = defaultdict(float, stats) if stats else defaultdict(float)


class Character:
    def __init__(self, stats = None):
        self.stats = defaultdict(float, stats) if stats else defaultdict(float)
        self.artifacts = defaultdict(float)
        self.total_stats = defaultdict(float)


    def equip(self, artifact):
        self.artifacts[artifact.type] = artifact


    def tally_stats(self):
        s = self.get_artifact_stats()
        self.total_stats[Stat.HP] = self.stats[Stat.HP] + s[Stat.HP] + 0.01*self.stats[Stat.HP] * s[Stat.HPP]
        self.total_stats[Stat.ATK] = self.stats[Stat.ATK] + s[Stat.ATK] + 0.01*self.stats[Stat.ATK] * s[Stat.ATKP]
        self.total_stats[Stat.DEF] = self.stats[Stat.DEF] + s[Stat.DEF] + 0.01*self.stats[Stat.DEF] * s[Stat.DEFP]
        self.total_stats[Stat.ER] = s[Stat.ER] + self.stats[Stat.ER]
        self.total_stats[Stat.EM] = s[Stat.EM] + self.stats[Stat.EM]
        self.total_stats[Stat.CR] = s[Stat.CR] + self.stats[Stat.CR]
        self.total_stats[Stat.CD] = s[Stat.CD] + self.stats[Stat.CD]
        self.total_stats[Stat.PYRO] = s[Stat.PYRO] + self.stats[Stat.PYRO]


    def get_artifact_stats(self):
        temp_stats = defaultdict(float)
        for category in self.artifacts:
            artifact = self.artifacts[category]
            main = artifact.main
            temp_stats[main] += _MAINVALS[main]
            for sub in artifact.stats:
                temp_stats[sub] += artifact.stats[sub]
        return temp_stats




class Type(Enum):
    FEATHER = 1
    FLOWER = 2
    SANDS = 3
    GOBLET = 4 
    CIRCLET = 5


class Stat(Enum):
    ATK = (1, 'ATK')
    ATKP = (2, 'ATK%')
    HP = (3, 'HP')
    HPP = (4, 'HP%')
    DEF = (5, 'DEF')
    DEFP = (6, 'DEF%')
    ER = (7, 'Energy Recharge')
    CR = (8, 'CRIT rate')
    CD = (9, 'CRIT DMG')
    EM = (10, 'Elemental Mastery')
    PHYS = (11, 'Physical DMG Bonus')
    PYRO = (12, 'Pyro DMG Bonus')
    HYDRO = (13, 'Hydro DMG Bonus')
    ELECTRO = (14, 'Electro DMG Bonus')
    CRYO = (15, 'Cryo DMG Bonus')
    ANEMO = (16, 'Anemo DMG Bonus')
    GEO = (17, 'Geo DMG Bonus')
    DENDRO = (18, 'Dendro DMG Bonus')
    HEAL = (19, 'Healing Bonus')

    def __str__(self):
        return self.value[1]


#MAIN STATS FOR ARTIFACT TYPES
_MAIN = {
        Type.FEATHER: {Stat.ATK: 1},
        Type.FLOWER:  {Stat.HP: 1},
        Type.SANDS:   {Stat.HPP:0.2668, Stat.ATKP:0.2666, Stat.DEFP:0.2666,
                            Stat.ER:0.1, Stat.EM: 0.1},
        Type.GOBLET:  {Stat.HPP:0.1925, Stat.ATKP: 0.1925, Stat.DEFP:0.19,
                            Stat.EM: 0.025, Stat.PHYS:0.05, Stat.PYRO:0.05, Stat.HYDRO:0.05,
                            Stat.ELECTRO:0.05, Stat.CRYO:0.05, Stat.ANEMO:0.05, Stat.GEO:0.05, Stat.DENDRO:0.05},
        Type.CIRCLET: {Stat.HPP:0.22, Stat.ATKP:0.22, Stat.DEFP:0.22, Stat.CR:0.1,
                            Stat.CD:0.1, Stat.HEAL:0.1, Stat.EM:0.04, Stat.HEAL:0.1}
            
        }

_WEIGHTS = {Stat.HP:6, Stat.ATK:6, Stat.DEF:6, Stat.HPP:4, Stat.ATKP:4, Stat.DEFP:4,
            Stat.ER: 4, Stat.EM: 4, Stat.CR: 3, Stat.CD: 3}

_MAINVALS = {Stat.HP:4780, Stat.ATK:311, Stat.HPP:46.6, Stat.ATKP:46.6, Stat.DEFP:58.3,
             Stat.EM:186.5, Stat.ER:51.8, Stat.CR:31.1, Stat.CD:62.2, Stat.HEAL:35.9,
             Stat.PYRO:46.6, Stat.HYDRO:46.6, Stat.ELECTRO:46.6, Stat.CRYO:46.6,
             Stat.ANEMO:46.6, Stat.GEO:46.6, Stat.DENDRO:46.6, Stat.PHYS: 58.3}

_VALUES = {Stat.HP:298.75, Stat.ATK:19.45, Stat.DEF:23.15, Stat.HPP:5.83,
           Stat.ATKP:5.83, Stat.DEFP:7.29, Stat.EM:23.31, Stat.ER:6.48, Stat.CR:3.89,
           Stat.CD:7.77}


#P(SUBSTAT) = W(SUBSTAT) / SUM(W(SUBSTATS))
#ROLL VALUE goes from 70% to 100% in 25% probability intervals

def get_damage_flat(char):
    char.tally_stats()
    a = char.total_stats[Stat.ATK]
    cr = 0.01 * char.total_stats[Stat.CR]
    cd = 0.01 * char.total_stats[Stat.CD]
    m = 0.01 * char.total_stats[Stat.PYRO]
    return a * (1 + cr*cd) * (1 + m)


def get_damage_aggravate(char):
    """ Total damage output for keqing assuming burst + n1c on TF"""
    char.tally_stats()
    a = char.total_stats[Stat.ATK]
    cr = 0.01 * char.total_stats[Stat.CR]
    cd = 0.01 * char.total_stats[Stat.CD]
    m = 0.01 * char.total_stats[Stat.PYRO]
    e = 1 + 20 * char.total_stats[Stat.EM] / (1400 + char.total_stats[Stat.EM]) + 0.2

    return (1+cr*cd) * (11*a*(1+m) + 1600*e)


def pick_from_distribution(distribution, scale = 1):
    """Picks an item from a dictionary where the values are probabilites"""
    a = random() * scale
    for val in distribution:
        a -= distribution[val]
        if a <= 0: return val

    return -1

    
def random_piece():
    """Generates a piece""" 
    match int(random()*5):
        case 0: piece = Artifact(Type.FEATHER)
        case 1: piece = Artifact(Type.FLOWER)
        case 2: piece = Artifact(Type.SANDS)
        case 3: piece = Artifact(Type.GOBLET)
        case 4: piece = Artifact(Type.CIRCLET)

    piece.set = int(random()*2)
    piece.main = pick_from_distribution(_MAIN[piece.type])
    for _ in range(4): add_sub(piece)

    return piece


def upgrade(piece):
    if len(piece.stats) == 3: add_sub(piece)
    stats = list(piece.stats.keys())
    for _ in range(4 + int(random() / 0.75)):
        stat = stats[int(random()*4)]
        piece.stats[stat] += (int(random()*4) * 0.1 + 0.7) * _VALUES[stat]


def add_sub(piece):
    scale = 44
    if piece.main in _WEIGHTS: scale -= _WEIGHTS[piece.main]
    for sub in piece.stats: scale -= _WEIGHTS[sub]
    a = random() * scale
    for w in _WEIGHTS:
        if w in piece.stats: continue
        if w is piece.main: continue
        a -= _WEIGHTS[w]

        if a <= 0:
            piece.stats[w] = (int(random()*4) * 0.1 + 0.7) * _VALUES[w]
            return

    raise(ValueError(f'COULD NOT FIND SUBSTAT for {piece.type} {piece.main}'
                     +f'\n{piece.stats}\na is {a}'))


def roll_value(artifact):
    a = artifact.stats[Stat.ATK] / _VALUES[Stat.ATK]
    b = artifact.stats[Stat.ATKP] / _VALUES[Stat.ATKP]
    c = artifact.stats[Stat.CR] / _VALUES[Stat.CR]
    d = artifact.stats[Stat.CD] / _VALUES[Stat.CD]

    return a + b + c + d



def random_pieces(number):
    offensive = {Stat.ATKP, Stat.ATK, Stat.CR, Stat.CD}
    feathers, flowers, sands, circlets, goblets = set(), set(), set(), set(), set()
    max_dmg = 0
    best_piece = None
    for _ in range(number):
        piece = random_piece()
        if piece.set == 0: continue
        num_offensive = 0
        for sub in piece.stats:
            if sub in offensive: num_offensive += 1
        if num_offensive == 0: continue
        

        match piece.type:
            case Type.FEATHER:
                upgrade(piece)
                feathers.add(piece)
            case Type.FLOWER:
                upgrade(piece)
                flowers.add(piece)
            case Type.SANDS:
                upgrade(piece)
                if piece.main is Stat.ATKP or piece.main is Stat.EM: sands.add(piece)
            case Type.GOBLET:
                upgrade(piece)
                if len(goblets) == 0: goblets.add(piece)
                if piece.main is Stat.PYRO: goblets.add(piece)
            case Type.CIRCLET:
                upgrade(piece)
                if piece.main is Stat.CR or piece.main is Stat.CD: circlets.add(piece)

    return (feathers, flowers, sands, circlets, goblets)



def flat_trial(n, character, artifacts = None):
    max_dmg, best_set = 0, None
    if artifacts: feathers, flowers, sands, circlets, goblets = artifacts
    else: feathers, flowers, sands, circlets, goblets = random_pieces(number)

    best_sands = roll_value(max(sands, key = roll_value))
    best_feather = roll_value(max(feathers, key = roll_value))
    best_flower = roll_value(max(flowers, key = roll_value))
    best_circlet = roll_value(max(circlets, key = roll_value))
    best_goblet =  0 if len(goblets) == 0 else roll_value(max(goblets, key = roll_value))



    for feather in feathers:
        character.equip(feather)
        for flower in flowers:
            character.equip(flower)
            for sand in sands:
                character.equip(sand)
                for circlet in circlets:
                    character.equip(circlet)
                    for goblet in goblets:
                        character.equip(goblet)
                        dmg = character.get_damage_flat()
                        if dmg > max_dmg:
                            max_dmg = dmg
                            best_set = copy.deepcopy(character.artifacts)

    return max_dmg


def trial_genetic(n, dmg_func = get_damage_flat, god = None, artifacts = None):
    if artifacts: feathers, flowers, sands, circlets, goblets = (list(item) for item in artifacts) 
    else: feathers, flowers, sands, circlets, goblets = (list(item) for item in random_pieces(n))
    characters = []

    for _ in range(5*n):
        char = Character(god.stats)
        char.equip(choice(feathers))
        char.equip(choice(flowers))
        char.equip(choice(sands))
        char.equip(choice(circlets))
        char.equip(choice(goblets))
        characters.append(char)


    for generation in range(25):
        characters = sorted(characters, key = lambda char: -1*dmg_func(char))[:n]
        #shuffle(characters)
        next_chars = []
        for mother, father in zip(characters, characters[1:]):
            a, b = dmg_func(mother), dmg_func(father)
            m = max(a,b)
            p = exp(a-m) / (exp(b-m) + exp(a-m))
            for _ in range(5):
                child = Character(god.stats)
                for t in Type:
                    if random() < 0.05:
                        match t:
                            case Type.FEATHER: child.equip(choice(feathers))
                            case Type.FLOWER: child.equip(choice(flowers))
                            case Type.SANDS: child.equip(choice(sands))
                            case Type.CIRCLET: child.equip(choice(circlets))
                            case Type.GOBLET: child.equip(choice(goblets))

                    elif random() < p: child.equip(mother.artifacts[t])
                    else: child.equip(father.artifacts[t])
                next_chars.append(child)
        characters = next_chars

    return max(characters, key = dmg_func)



if __name__ == '__main__':
    keqing = Character(defaultdict(float, {Stat.ATK: 800, Stat.CR: 5, Stat.CD: 50}))
    fischl = Character(defaultdict(float, {Stat.ATK: 754, Stat.CR: 5, Stat.CD: 50}))

    fischl.equip(Artifact(Type.FLOWER, 1, Stat.HP, {Stat.DEF:19, Stat.CD:34.2, Stat.ATKP:5.8, Stat.ER:5.2}))
    fischl.equip(Artifact(Type.FEATHER, 1, Stat.ATK, {Stat.CR:10.1, Stat.CD:14.8, Stat.DEFP:12.4, Stat.HPP:10.5}))
    fischl.equip(Artifact(Type.SANDS, 1, Stat.ATKP, {Stat.EM:84, Stat.HPP:9.9, Stat.CR:3.9, Stat.ER:11}))
    fischl.equip(Artifact(Type.CIRCLET, 1, Stat.CR, {Stat.ATK:18, Stat.ATKP:20.4, Stat.DEFP:5.1, Stat.CD:13.2}))
    fischl.equip(Artifact(Type.GOBLET, 1, Stat.PYRO, {Stat.ATKP:8.7, Stat.CD:13.2, Stat.CR:9.3, Stat.HP:269}))

    keqing.equip(Artifact(Type.FLOWER, 1, Stat.HP, {Stat.ATK:18, Stat.EM:16, Stat.CR:15.9, Stat.CD:5.4}))
    keqing.equip(Artifact(Type.FEATHER, 1, Stat.ATK, {Stat.ATKP:14, Stat.EM:54, Stat.CR:3.5, Stat.CD:5.4}))
    keqing.equip(Artifact(Type.SANDS, 1, Stat.ATKP, {Stat.DEF:42, Stat.EM:37, Stat.CR:11.3, Stat.CD:6.2}))
    keqing.equip(Artifact(Type.CIRCLET, 1, Stat.CR, {Stat.HP:687, Stat.ER:11.7, Stat.EM:42, Stat.CD:5.4}))
    keqing.equip(Artifact(Type.GOBLET, 1, Stat.PYRO, {Stat.HPP:18, Stat.EM:16, Stat.CR:2.7, Stat.CD:27.2}))

    damage_initial = fischl.get_damage_flat()
    res = 0
    print(damage_initial)
    trials = 20
    for trial in range(trials):
        print(f'{str(trial).zfill(3)}\r', end = "")
        artifacts = random_pieces(625)
        artifacts[0].add(fischl.artifacts[Type.FEATHER])
        artifacts[1].add(fischl.artifacts[Type.FLOWER])
        artifacts[2].add(fischl.artifacts[Type.SANDS])
        artifacts[3].add(fischl.artifacts[Type.CIRCLET])
        artifacts[4].add(fischl.artifacts[Type.GOBLET])

        max_dmg = trial_genetic(630, fischl, artifacts)
        print(max_dmg, max_dmg.get_damage_flat())
#        print(f'TRUE MAX DMG {flat_trial(630, fischl, artifacts)}')
        for artifact in max_dmg.artifacts: print(artifact, max_dmg.artifacts[artifact].stats)

        res += max_dmg.get_damage_flat()


    #print(max_dmg.total_stats)
    print(res / trials)
    print(res / trials / damage_initial)

