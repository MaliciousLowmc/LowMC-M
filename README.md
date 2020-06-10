# LowMC-M

MALICIOUS is a framework of embedding backdoors into tweakable block ciphers. LowMC-M is a familiy of instantiations of MALICIOUS, which is based on the block cipher LowMC. This repository contains the code to benchmark the optimized implementation of LowMC-M using AVX2 instruction. It also contains the code to generate a concrete instance of LowMC-M, including the components of the cipher and the backdoor.

Benchmark
----
The codes are stored inside the "benchmark" folder, it is provided by the Picnic team, which can be found at (https://github.com/IAIK/Picnic). Simply compile it by running  `make`, then run it with `./lowmc_bench -i x y`(read/write permission is required)  where `x` is the number of iterations you want to run and `y` is the LowMC instance number you want to test:  
```
1 is "lowmc_128_128_20.h"
2 is "lowmc_192_192_30.h"
3 is "lowmc_256_256_38.h"
4 is "lowmc_129_129_4.h"
5 is "lowmc_192_192_4.h"
6 is "lowmc_255_255_4.h"
```
Generating LowMC-M
----
The codes are stored inside the "generate" folder. After installing [SageMath](https://www.sagemath.org/), simply run `sage generate_lowmc-m.py`

