import time
import re
import os

VALID_BIN_PREFIXES = {'Visa CB': ['417500', '4974'],
    'MasterCard': ['51', '52', '53', '54', '55'],
    'MasterCard CB': ['5400', '545454'],
    'American Express': ['34', '37']
 }


def check_16_19_digits(line):
    pattern = re.compile(r'\b\d{16,19}\b')
    matches = pattern.findall(line)
    return matches


def card_checker(cards):
    L = {}
    progression = 0
    true_cards = 0
    true_cards_list = {}

    for index, extended_card in enumerate(cards):
        progression += 1
        possible_cards = check_16_19_digits(str(extended_card))

        if possible_cards:
            for card in possible_cards:
                if isValid(card) and is_valid_prefix(card) and not is_too_simple(card):
                    true_cards += 1
                    true_cards_list[index] = card
                    L[index] = True
                    break
            else:
                L[index] = False

        if progression % 100 == 0 or progression == len(cards):
            print(f"Progression : {round(progression / len(cards) * 100, 3)} %")

    return L, true_cards, true_cards_list


def isValid(card):
    card = [int(x) for x in reversed(card)]
    total = sum(card[0::2]) + sum([sum(divmod(2 * x, 10)) for x in card[1::2]])
    return total % 10 == 0


def is_valid_prefix(card):
    for issuer, prefixes in VALID_BIN_PREFIXES.items():
        if any(card.startswith(prefix) for prefix in prefixes):
            return True
    return False


def is_too_simple(card):
    # Exclure les séquences trop simples ou répétitives
    if card == card[0] * len(card):  # Tous les chiffres identiques
        return True
    if card in ''.join(str(x) for x in range(10)) * 2:  # Séquence montante
        return True
    if card in ''.join(str(x) for x in range(9, -1, -1)) * 2:  # Séquence descendante
        return True
    return False


if __name__ == "__main__":
    # Change le chemin du fichier ici
    path = "/data/sftp/prod/x_autorisation/input/tucb/"

    for filename in os.listdir(path):
        print(filename)
        with open(path + filename, "r") as file:
            lines = file.readlines()

        start_time = time.time()
        L, true_cards, true_cards_list = card_checker(lines)
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        if true_cards == 0:
            exit()

        # Détails de chaque ligne du fichier, si le PAN est valide
        with open("/data/prod/commun/pan_buster/logs/" + filename+"_card_detail.txt", 'w') as f:
            f.write(f"Number of valid cards : {true_cards}")
            for line in L:
                f.write(f'{line + 1} : {L[line]}\n')

        # Liste des CBs valides et leurs lignes d'entrées
        with open("/data/prod/commun/pan_buster/logs/" + filename+"_card_list_detail.txt", 'w') as f:
            f.write(f"Number of valid cards : {true_cards}")
            for line in true_cards_list:
                f.write(f'{line + 1} : {true_cards_list[line]}\n')

        print(f"Time taken : {elapsed_time} seconds\n")
        print(f"The detail file card_detail.txt has been written\n")
        print(f"The detail file card_list_detail.txt has been written\n")
        print(f"Number of valid cards : {true_cards}")
