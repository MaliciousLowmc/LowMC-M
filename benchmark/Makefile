
CFLAGS += -g -O3 -march=native -std=gnu11
CPPFLAGS += -DWITH_LOWMC_128_128_20
CPPFLAGS += -DWITH_LOWMC_129_129_4
CPPFLAGS += -DWITH_LOWMC_192_192_30
CPPFLAGS += -DWITH_LOWMC_192_192_4
CPPFLAGS += -DWITH_LOWMC_255_255_4
CPPFLAGS += -DWITH_LOWMC_256_256_38
CPPFLAGS += -DWITH_OPT -DWITH_SSE2 -DWITH_AVX2

LIBSRCS = aligned_alloc.c io.c lowmc_129_129_4.c lowmc_192_192_4.c lowmc_256_256_38.c cpu.c lowmc_128_128_20.c lowmc_192_192_30.c lowmc_255_255_4.c lowmc.c mzd_additional.c randomness.c
LIBOBJS = $(patsubst %.c,%.o,$(LIBSRCS))

BENCHSRCS = bench_lowmc.c bench_utils.c bench_timing.c
BENCHOBJS = $(patsubst %.c,%.o,$(BENCHSRCS))

TESTSRCS = lowmc_test.c
TESTOBJS = $(patsubst %.c,%.o,$(TESTSRCS))

all: lowmc_bench lowmc_test

%.o: %.c
	$(CC) $(CPPFLAGS) $(CFLAGS) -o $@ -c $<

lowmc_test: $(TESTOBJS) $(LIBOBJS)
	$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -o $@

lowmc_bench: $(BENCHOBJS) $(LIBOBJS)
	$(CC) $(CPPFLAGS) $(LDFLAGS) $^ -o $@

clean:
	$(RM) -f $(LIBOBJS) $(BENCHOBJS) $(TESTOBJS) lowmc_test lowmc_bench
