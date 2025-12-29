# Cocotb Makefile for AIPP-SH Gate
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

VERILOG_SOURCES += $(PWD)/aipp_sh_gate.v
TOPLEVEL = aipp_sh_gate
MODULE = test_sh_gate

include $(shell cocotb-config --makefiles)/Makefile.sim

