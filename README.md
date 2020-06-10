# LowMC-M

MALICIOUS is a framework of embedding backdoors into tweakable block ciphers. LowMC-M is a familiy of instantiations of MALICIOUS, which is based on the block cipher LowMC. This repository contains the code to benchmark the optimized implementation of LowMC-M using AVX2 instruction. It also contains the code to generate a concrete instance of LowMC-M, including the components of the cipher and the backdoor.

Benchmark
----
The codes are stored inside the "benchmark" folder. Complie it by simply run `make`

Generating LowMC-M
----
The codes are stored inside the "generate" folder. After installing [SageMath](https://www.sagemath.org/), simply run "sage generate_lowmc-m.py"

