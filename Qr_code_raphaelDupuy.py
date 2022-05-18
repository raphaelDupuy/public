######################################################################
# imports

from telnetlib import DM
import PIL as pil
from PIL import Image
from PIL import ImageTk

######################################################################
# globals
lenght = 0

######################################################################
# functions 1


def nbrCol(qr_code):
    return len(qr_code[0])


def nbrLig(qr_code):
    return len(qr_code)


# sauvegarde l'image contenue dans matpix dans le fichier filename
# utiliser une extension png pour que la fonction
# fonctionne sans perte d'information
def saving(matPix, filename):

    toSave = pil.Image.new(mode="1", size=(nbrCol(matPix), nbrLig(matPix)))
    for i in range(nbrLig(matPix)):
        for j in range(nbrCol(matPix)):
            toSave.putpixel((j, i), matPix[i][j])
    toSave.save(filename)


# charge le fichier image filename et
# renvoie une qr_code de 0 et de 1 qui représente
# l'image en noir et blanc
def loading(filename):

    toLoad = pil.Image.open(filename)
    mat = [[0]*toLoad.size[0] for k in range(toLoad.size[1])]
    for i in range(toLoad.size[1]):
        for j in range(toLoad.size[0]):
            mat[i][j] = 0 if toLoad.getpixel((j, i)) == 0 else 1
    return mat


######################################################################
# functions 2


# load la matrice de coin
def proof():
    mat_proof = loading("Exemples/coin.png")
    return(mat_proof)


# verifie si le code est tourné dans le bon sens
def verify_rotation(qr_code):
    corner = qr_code[18:len(qr_code)]
    for i in range(len(corner)):
        corner[i] = corner[i][18:25]
    saving(corner, "corner.png")
    if loading("corner.png") == proof():
        mat = []
        for i in range(len(qr_code)):
            ligne = []
            for j in range(len(qr_code)):
                ligne.append(qr_code[j][i])
            ligne.reverse()
            mat.append(ligne)
        qr_code = list(mat)
        saving(qr_code, "qr_tst_rota.png")
        verify_rotation(qr_code)
    return(qr_code)


# verifie l'alignement du qr_code
def verify_alternation(qr_code):
    segment, line, check = qr_code[7:18], [], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    for lines in segment:
        line.append(lines[6])
    if qr_code[6][7:18] == check and line == check:
        print("good alternation")
    return(qr_code)


# applique le code de hamming sur les bits du qr code
def hamming(bits):
    p1 = bits[0] ^ bits[1] ^ bits[2]
    p2 = bits[0] ^ bits[2] ^ bits[3]
    p3 = bits[1] ^ bits[2] ^ bits[3]
    # position erreur
    num = int(p1 != bits[4]) + int(p2 != bits[5]) * 2 + int(p3 != bits[6]) * 4
    if (num == 3):
        bits[0] = int(not bits[0])
    if num == 5:
        bits[1] = int(not bits[1])
    if num == 6:
        bits[2] = int(not bits[2])
    if num == 7:
        bits[3] = int(not bits[3])
    return bits[:4]


# lit les bits contenu dans le qr code dans le bon ordre
def reading(qr_code):
    global lenght
    output, code, = [], qr_code[9:len(qr_code)]
    for i in range(16):
        code[i] = code[i][11:len(code[i])]
    for i in range(1, len(code) + 1, 2):
        content = []
        if ((i-1) // 2) % 2 == 0:
            for j in range(14):
                content.append(code[-i][-(j + 1)])
                content.append(code[- (i + 1)][-(j + 1)])
            output.append(content)
        else:
            for j in range(14):
                content.append(code[-i][j])
                content.append(code[- (i + 1)][j])
            output.append(content)
    result = []
    for elem in output:
        result.append(elem[0:14])
        result.append(elem[14:28])
    print(str(lenght) + " blocks à décoder")
    result = result[:lenght]
    return(result)


# permet de traduire le contenu du qr_code
def display(qr_code):
    # 1 = ascii, 0 = hexadécimal
    content, message, output = reading(filtre(verify_alternation(
                                       verify_rotation(qr_code)))), [], []
    if qr_code[24][8] == 1:
        for blocks in content:
            block, block2 = hamming(blocks[:7]), hamming(blocks[7:14])
            block.extend(block2)
            message.append(block)
        for block in message:
            m = ""
            for j in block:
                m += str(j)
            output.append(chr(int(m, 2)))
    else:
        for blocks in content:
            block, block2 = hamming(blocks[:7]), hamming(blocks[7:14])
            message.append(block)
            message.append(block2)
        for block in message:
            m = ""
            for j in block:
                m += str(j)
            output.append(hex(int(m, 2))[2:])
    result = ""
    for char in output:
        result += str(char)
    return result


# ajoute le filtre correspondant sur le qr code
def filtre(qr_code):
    global lenght
    lenght = int(str(str(qr_code[13][0]) + str(qr_code[14][0]) +
                     str(qr_code[15][0]) + str(qr_code[16][0]) +
                     str(qr_code[17][0])), 2)
    filtre = (qr_code[22][8], qr_code[23][8])
    # pas de filtre
    if filtre == (0, 0):
        pass
    # filtre damier [0][0] noire
    elif filtre == (0, 1):
        line = 0
        for i in qr_code:
            cnt = 0
            for j in qr_code[0]:
                if line % 2 == 0:  # ligne pair
                    if cnt % 2 != 0:
                        if i[cnt] == 1:
                            i[cnt] = 0
                        else:
                            i[cnt] = 1
                        cnt += 1
                    else:
                        cnt += 1
                else:  # ligne impair
                    if cnt % 2 == 0:
                        if i[cnt] == 1:
                            i[cnt] = 0
                        else:
                            i[cnt] = 1
                        cnt += 1
                    else:
                        cnt += 1
            line += 1
    # filtre horizontal premiere ligne noire
    elif filtre == (1, 0):
        line = 0
        for i in qr_code:
            if line % 2 != 0:
                cnt = 0
                for j in i:
                    if i[cnt] == 1:
                        i[cnt] = 0
                    else:
                        i[cnt] = 1
                    cnt += 1
            line += 1
    # filtre vertical premiere colonne noire
    elif filtre == (1, 1):
        for i in qr_code:
            cnt = 0
            for j in qr_code[0]:
                if cnt % 2 != 0:
                    if i[cnt] == 1:
                        i[cnt] = 0
                    else:
                        i[cnt] = 1
                    cnt += 1
                else:
                    cnt += 1
    return qr_code


# décode le qr code en utilisant toutes les fonctions ci-dessus
def decode(qr_code):
    print(display(loading(qr_code)))


######################################################################
# Exec.

decode("Exemples/qr_code_ssfiltre_ascii.png")
