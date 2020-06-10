# LowMC-M

MALICIOUS is a framework of embedding backdoors into tweakable block ciphers. LowMC-M is a familiy of instantiations of MALICIOUS, which is based on the block cipher LowMC. This repository contains the code to benchmark the optimized implementation of LowMC-M using AVX2 instruction. It also contains the code to generate a concrete instance of LowMC-M, including the components of the cipher and the backdoor.

This is a sage implementation of MALICIOUS instantiations based on LowMC block cipher familiy, called LowMC-M. 

The file "shake128" is python implementation of SHAKE128. 

The file "generate_withshake128" is used to generate LowMC-M with parameters: 1.blocksize 2.keysize 3.number of Sboxes per round 4.the number of embedded mailicious differential characteristics. The input difference and tweak pair of the embedded characteristic are chosen  by the user.
