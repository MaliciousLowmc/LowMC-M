'''
The tweak schedule is SHAKE128
'''
from sage.all import *
import numpy as np
from SHAKE128 import *


blocksize = 128
keysize = 128
rounds = 10
m = 3 # number of sboxes
sboxsize = 3 #sbox size
nonLsize = sboxsize*m #non-linear size
num_dc = 5 #number of embedded differential characteristics
tweaksize = 128


def generate_Kmatrix():
    roundkey_matrices = []
    while True:
        mat = np.random.randint(0,2,size = (blocksize,keysize))
        Mat = matrix(GF(2),mat)
        if rank(Mat) == min(blocksize,keysize):
            break
    roundkey_matrices.append(mat)

    for r in range(rounds):
        while True:
            mat = np.random.randint(0,2,size = (nonLsize,keysize))
            Mat = matrix(GF(2),mat)
            if rank(Mat) == min(nonLsize,keysize):
                break
        roundkey_matrices.append(mat)

    return roundkey_matrices
    
def generate_constants():
    cons = []
    for r in range(rounds):
        con = np.random.randint(0,2,size = nonLsize)
        cons.append(con)
    return cons 

def generate_tweakdifferences():
    subtweakdiff_set = []
    tweak_set = []
    for i in range(num_dc):
        subtweaks1 = [0] * (rounds+1)
        subtweaks2 = [0] * (rounds+1)

        tweak1 = list(np.random.randint(0,2,size=tweaksize))    # can be chosen by the user alternatively, both size and value,
        tweak2 = list(np.random.randint(0,2,size=tweaksize))    # can be chosen by the user alternatively, both size and value,
        tstring1 = shake128(tweak1, blocksize+rounds*nonLsize)
        tstring2 = shake128(tweak2, blocksize+rounds*nonLsize)
        subtweaks1[0] = tstring1[:blocksize]
        subtweaks2[0] = tstring2[:blocksize]
        for r in range(rounds):
            subtweaks1[r+1] = tstring1[blocksize+r*nonLsize:blocksize+(r+1)*nonLsize]
            subtweaks2[r+1] = tstring2[blocksize+r*nonLsize:blocksize+(r+1)*nonLsize]

        subtweak_differences = []
        for r in range(rounds+1):
            subtweak_differences.append([subtweaks1[r][j] ^ subtweaks2[r][j] for j in range(len(subtweaks1[r]))])

        subtweakdiff_set.append(subtweak_differences)
        tweak_set.append([tweak1,tweak2])
    return subtweakdiff_set, tweak_set

def generate_DC():     
    roundkey_matrices = generate_Kmatrix()
    constants = generate_constants()

    tweakdifferences, tweak_set = generate_tweakdifferences()
    BS_differences = [[] for _ in range(rounds)] #differences Before Sbox
    AM_differences = [[] for _ in range(rounds)] #differences After Matrix multiplication
    LMatrices = []


    plaintext_differences = []
    # the plaintext_differences are input differences of the differential characteristics to be embedded,
    # it can be chosen by the user along with the first subtweak difference.
    for i in range(num_dc):
        plaintext_differences.append(tweakdifferences[i][0][:nonLsize] + list(np.random.randint(0,2,size=blocksize-nonLsize)))

    for i in range(num_dc):
        BS_differences[0].append([plaintext_differences[i][j] ^ tweakdifferences[i][0][j] for j in range(blocksize)])


    for r in range(rounds-1):
        if r < (rounds-1-num_dc):
            LMatrices.append(generate_Lmatrix(BS_differences[r],tweakdifferences,r))

            for i in range(num_dc):
                AM_differences[r].append(list(matrix(GF(2),LMatrices[r]) * vector(GF(2),BS_differences[r][i])))

                BS_differences[r+1].append([AM_differences[r][i][j] + tweakdifferences[i][r+1][j] for j in range(nonLsize)] + \
                                            AM_differences[r][i][nonLsize:])
        elif r >= (rounds-1-num_dc):
            if r == rounds-1-num_dc:
                LMatrices.append(generate_Lmatrix(BS_differences[r],tweakdifferences,r))
            else:
                LMatrices.append(generate_Lmatrix(BS_differences[r][:-1],tweakdifferences,r))

            for i in range(rounds-r-1):
                AM_differences[r].append(list(matrix(GF(2),LMatrices[r]) * vector(GF(2),BS_differences[r][i])))

                BS_differences[r+1].append([AM_differences[r][i][j] + tweakdifferences[i][r+1][j] for j in range(nonLsize)] + \
                                        AM_differences[r][i][nonLsize:])
    # The last linear matrix
    while True:
        mat = np.random.randint(0,2,size = (blocksize,blocksize))
        Mat = matrix(GF(2),mat)
        if rank(Mat) == blocksize:
            break
    LMatrices.append(mat)

    with open('matrices_and_constants.txt', 'w') as matfile:
        s = 'Linear layer matrices\n\n'
        for r in range(rounds):
            s += '\nrounds' + str(r) + ':\n'
            for row in LMatrices[r]:
                s += str(row) + '\n'

        s += '\nKey matrices\n\n'
        for r in range(rounds+1):
            s += 'round' + str(r) + ":\n"
            for row in roundkey_matrices[r]:
                s += str(row) + "\n"

        s += '\nRound constants\n\n'
        for r in range(rounds):
            s += str(constants[r]) + '\n'

        matfile.write(s)


    with open('Differential Characteristics.txt','w') as dcfile:
        s = 'Differential Characteristics\n\n\n'
        for i in range(num_dc):
            s += '\ndifferential ' + str(i+1) + ':\n'
            s += 'length: {} rounds\n'.format(rounds-i-1) 
            s += 'tweak pair:\n'
            s += str(tweak_set[i][0]) + '\n' 
            s += str(tweak_set[i][1]) + '\n'
            s += 'plaintext difference:\n'
            s += str(plaintext_differences[i]) + '\n'
            s +=  'differences before SB:\n'
            for r in range(rounds-i):
                s += 'round {:3} '.format(r+1) + str(BS_differences[r][i]) + '\n'
        dcfile.write(s)


def generate_Lmatrix(differences, tweakdiff, r):
    Length = len(differences)
    Nonzero = [0]*sboxsize
    if r >= (rounds-1-num_dc):
        for i in range(m):
            while True:
                Nonzero[i] = np.random.randint(0,2,size=m)
                if sum([Nonzero[i][j]^tweakdiff[Length-1][r+1][j+m*i] for j in range(sboxsize)]) != 0:
                    break

    Set = []
    for t in range(nonLsize):

        extra_column = []
        for i in range(Length):
            extra_column.append([tweakdiff[i][r+1][t]])
        
        if r >= (rounds-1-num_dc):
            extra_column[-1][0] = Nonzero[t//m][t%m]

        augmented_mat = (np.append(differences, extra_column, axis=1)).tolist()
        Mat = matrix(GF(2),augmented_mat)
        Set.append(Mat.right_kernel().basis_matrix())

    while True: 
        Matrice = []
        #generate the first nonLsize rows
        for t in range(nonLsize):
            while True:
                tmpvec = random_vector(GF(2),len(list(Set[t])))
                if (tmpvec*Set[t])[-1] == 1:
                    Matrice.append(list((tmpvec*Set[t])[:-1]))
                    break
        #generate the left (blocksize-nonLsize) rows
        for i in range(blocksize-m*sboxsize):
            Matrice.append(list(np.random.randint(0,2,size=blocksize)))
        mat = matrix(GF(2),Matrice)
        if rank(mat) == blocksize:
            return Matrice
    
def main():
    if num_dc > (keysize/sboxsize*m):
        print("Too many differential paths")
        exit(0)
    else:
        generate_DC()

if __name__ == "__main__":
    main()