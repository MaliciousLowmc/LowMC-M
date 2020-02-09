# Malicious

This is a sage implementation of MALICIOUS instantiations based on LowMC block cipher familiy, called LowMC-M. 

The file "shake128" is python implementation of SHAKE128. 

The file "generate_withshake128" is used to generate LowMC-M with parameters: 1.blocksize 2.keysize 3.number of Sboxes per round 4.the number of embedded mailicious differential characteristics. The input difference and tweak pair of the embedded characteristic are chosen  by the user.
