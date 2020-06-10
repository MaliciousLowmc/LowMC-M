'''
This program generates an instance of LowMC-M

Only SHAKE128 is considered, so the key size 
is fixed to 128 bits for security concern.
'''
from sage.all import *
from SHAKE128 import *
import numpy as np


blocksize = 128
keysize = 128
tweaksize = 128
sboxsize = 3               # sbox size
m = 3                      # number of sboxes
nonLsize = sboxsize*m      # non-linear size
rounds = 70                # number of rounds
num_dc = 14                # number of differential characteristics to be embedded


def generate_Kmatrix():
    roundkey_matrices = []

    #Generate the whitening key
    while True:
        mat = np.random.randint(0,2,size = (blocksize,keysize))
        Mat = matrix(GF(2),mat)
        if rank(Mat) == min(blocksize,keysize):
            break
    roundkey_matrices.append(mat.tolist())

    #Generate the round keys
    for r in range(rounds):
        while True:
            mat = np.random.randint(0,2,size = (nonLsize,keysize))
            Mat = matrix(GF(2),mat)
            if rank(Mat) == min(nonLsize,keysize):
                break
        roundkey_matrices.append(mat.tolist())

    return roundkey_matrices
    
def generate_constants():
    cons = []
    for r in range(rounds):
        con = np.random.randint(0,2,size = nonLsize)
        cons.append(con.tolist())
    return cons 

def generate_tweakdifferences():
    subtweakdiff_set = []
    tweak_set = []
    for i in range(num_dc):
        subtweaks1 = [0] * (rounds+1)
        subtweaks2 = [0] * (rounds+1)

        #*************TWEAK GENERATION**************
        # It can be chosen by the user alternatively, both size and value

        tweak1 = list(np.random.randint(0,2,size=tweaksize))
        tweak2 = list(np.random.randint(0,2,size=tweaksize))
        #*******************************************

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

def generate_Lmatrix(differences, tweakdiff, r):
    Length = len(differences)
    Nonzero = [0]*sboxsize

    # This is to ensure that an i-round deterministic differential characteristic will active all the Sboxes in round i+1
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
        # Generate the first (nonLsize) rows
        for t in range(nonLsize):
            while True:
                tmpvec = random_vector(GF(2),len(list(Set[t])))
                if (tmpvec*Set[t])[-1] == 1:
                    Matrice.append(list((tmpvec*Set[t])[:-1]))
                    break
        # Generate the left (blocksize-nonLsize) rows
        for i in range(blocksize-m*sboxsize):
            Matrice.append(list(np.random.randint(0,2,size=blocksize)))
        mat = matrix(GF(2),Matrice)
        if rank(mat) == blocksize:
            return Matrice
 
def generate_DC():     
    roundkey_matrices = generate_Kmatrix()  #Generate key matrices
    constants = generate_constants()    #Generate round constants

    tweakdifferences, tweak_set = generate_tweakdifferences()   #Generate tweak pairs and its corresponding sub-tweak differences
    BS_differences = [[] for _ in range(rounds)] # Difference before Sbox transformation in each round
    AM_differences = [[] for _ in range(rounds)] # Difference after matrix multiplication in each round
    LMatrices = []  # Linear matrices
    plaintext_differences = []  # The plaintext difference is input difference of the differential characteristic to be embedded, it can be chosen by the user along with the first sub-tweak difference.
    
    for i in range(num_dc): # Generate plaintext difference
        plaintext_differences.append(tweakdifferences[i][0][:nonLsize] + list(np.random.randint(0,2,size=blocksize-nonLsize)))

    for i in range(num_dc): # Compute the difference between the plaintext difference and the first sub-tweak difference
        BS_differences[0].append([plaintext_differences[i][j] ^ tweakdifferences[i][0][j] for j in range(blocksize)])


    #*************GENERATE ROUND DIFFERENCE**************
    # Building (num_dc) differential characteristics, the number of rounds ranges from (rounds-1) to (rounds-1-num_dc+1)
    
    #****************************************************

    for r in range(rounds-1):
        if r <= (rounds-1-num_dc):
            LMatrices.append(generate_Lmatrix(BS_differences[r],tweakdifferences,r)) # Generate linear matrix
            current_num_dc = num_dc

        elif r > (rounds-1-num_dc):
            LMatrices.append(generate_Lmatrix(BS_differences[r][:-1],tweakdifferences,r))   # Generate linear matrix
            current_num_dc = rounds-r-1

        for i in range(current_num_dc):
            AM_differences[r].append(list(matrix(GF(2),LMatrices[r]) * vector(GF(2),BS_differences[r][i])))
            BS_differences[r+1].append([AM_differences[r][i][j] + tweakdifferences[i][r+1][j] for j in range(nonLsize)] + \
                                    AM_differences[r][i][nonLsize:])
    
    # Generate the last linear matrix
    while True:
        mat = np.random.randint(0,2,size = (blocksize,blocksize))
        Mat = matrix(GF(2),mat)
        if rank(Mat) == blocksize:
            break
    LMatrices.append(mat.tolist())

    with open('matrices_and_constants.txt', 'w') as matfile:
        s = 'Linear layer matrices\n\n'
        for r in range(rounds):
            s += '\nround ' + str(r) + ':\n'
            for row in LMatrices[r]:
                s += str(row) + '\n'

        s += '\nKey matrices\n\n'
        for r in range(rounds+1):
            s += 'round ' + str(r) + ":\n"
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
   
def main():
    generate_DC()

if __name__ == "__main__":
    main()
