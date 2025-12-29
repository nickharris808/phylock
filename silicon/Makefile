################################################################################
# Portfolio B HLS - Makefile
#
# Build system for synthesizable C++ cores (ARC-3, D-Gate+, PQLock)
#
# Targets:
#   all:       Build all testbenches
#   arc3_tb:   Build ARC-3 CSI Correlator testbench
#   dgate_tb:  Build D-Gate+ FSM testbench
#   csim:      Run C simulation (software validation)
#   synth:     Run HLS synthesis (requires Vivado/Vitis HLS)
#   cosim:     Run C/RTL co-simulation
#   export:    Export RTL as IP core
#   clean:     Remove build artifacts
#
# Requirements:
#   - Xilinx Vivado/Vitis HLS 2023.2+ (for synthesis)
#   - g++ 9+ (for C simulation without HLS)
#   - AP library headers (included with Vivado)
#
# Usage:
#   make csim       # Run C simulation (quick validation)
#   make synth      # Synthesize to RTL (requires Vivado license)
#   make export     # Export IP for Vivado integration
#
################################################################################

# Compiler settings (for C simulation without Vivado)
CXX = g++
CXXFLAGS = -std=c++14 -O2 -Wall -Wno-unknown-pragmas

# Xilinx HLS installation path (adjust for your system)
XILINX_HLS ?= /opt/Xilinx/Vitis_HLS/2023.2
HLS_INCLUDE = -I$(XILINX_HLS)/include

# Target FPGA (adjust for your board)
FPGA_PART = xczu9eg-ffvb1156-2-e  # ZCU102 Evaluation Board
CLOCK_PERIOD = 1.0               # 1ns = 1 GHz target

# Source files
ARC3_SRCS = arc3_csi_correlator.cpp arc3_csi_correlator_tb.cpp
DGATE_SRCS = dgate_fsm.cpp dgate_fsm_tb.cpp

# Output directories
BUILD_DIR = build
SYNTH_DIR = $(BUILD_DIR)/synthesis
EXPORT_DIR = $(BUILD_DIR)/ip_export

################################################################################
# C Simulation Targets (no Vivado required)
################################################################################

.PHONY: all csim clean

all: arc3_tb dgate_tb

# ARC-3 CSI Correlator testbench
arc3_tb: arc3_csi_correlator.cpp arc3_csi_correlator_tb.cpp arc3_csi_correlator.h
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(HLS_INCLUDE) -o $(BUILD_DIR)/arc3_tb \
		arc3_csi_correlator.cpp arc3_csi_correlator_tb.cpp
	@echo "✅ Built ARC-3 testbench: $(BUILD_DIR)/arc3_tb"

# D-Gate+ FSM testbench
dgate_tb: dgate_fsm.cpp dgate_fsm_tb.cpp dgate_fsm.h
	@mkdir -p $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(HLS_INCLUDE) -o $(BUILD_DIR)/dgate_tb \
		dgate_fsm.cpp dgate_fsm_tb.cpp
	@echo "✅ Built D-Gate+ testbench: $(BUILD_DIR)/dgate_tb"

# Run C simulation
csim: arc3_tb dgate_tb
	@echo ""
	@echo "=========================================="
	@echo "Running ARC-3 CSI Correlator Tests"
	@echo "=========================================="
	@$(BUILD_DIR)/arc3_tb
	@echo ""
	@echo "=========================================="
	@echo "Running D-Gate+ FSM Tests"
	@echo "=========================================="
	@$(BUILD_DIR)/dgate_tb
	@echo ""
	@echo "=========================================="
	@echo "All C simulations complete!"
	@echo "=========================================="

################################################################################
# HLS Synthesis Targets (requires Vivado/Vitis HLS)
################################################################################

.PHONY: synth cosim export

# Synthesis - requires Vivado HLS license
synth:
	@echo "Synthesizing ARC-3 CSI Correlator..."
	@mkdir -p $(SYNTH_DIR)/arc3
	@cd $(SYNTH_DIR)/arc3 && vitis_hls -f $(CURDIR)/run_arc3_synth.tcl
	@echo ""
	@echo "Synthesizing D-Gate+ FSM..."
	@mkdir -p $(SYNTH_DIR)/dgate
	@cd $(SYNTH_DIR)/dgate && vitis_hls -f $(CURDIR)/run_dgate_synth.tcl
	@echo ""
	@echo "✅ Synthesis complete. Reports in $(SYNTH_DIR)/"

# C/RTL Co-simulation
cosim:
	@echo "Running C/RTL co-simulation (requires synthesis first)..."
	@cd $(SYNTH_DIR)/arc3 && vitis_hls -f $(CURDIR)/run_arc3_cosim.tcl
	@cd $(SYNTH_DIR)/dgate && vitis_hls -f $(CURDIR)/run_dgate_cosim.tcl
	@echo "✅ Co-simulation complete"

# Export as Vivado IP
export:
	@echo "Exporting RTL as IP cores..."
	@mkdir -p $(EXPORT_DIR)
	@cd $(SYNTH_DIR)/arc3 && vitis_hls -f $(CURDIR)/run_arc3_export.tcl
	@cd $(SYNTH_DIR)/dgate && vitis_hls -f $(CURDIR)/run_dgate_export.tcl
	@echo "✅ IP cores exported to $(EXPORT_DIR)/"

################################################################################
# TCL Script Generation (for Vivado HLS automation)
################################################################################

.PHONY: gen_tcl

gen_tcl: run_arc3_synth.tcl run_dgate_synth.tcl

run_arc3_synth.tcl:
	@echo "# ARC-3 Synthesis Script" > $@
	@echo "open_project arc3_project" >> $@
	@echo "set_top arc3_csi_correlator" >> $@
	@echo "add_files $(CURDIR)/arc3_csi_correlator.cpp" >> $@
	@echo "add_files -tb $(CURDIR)/arc3_csi_correlator_tb.cpp" >> $@
	@echo "open_solution solution1" >> $@
	@echo "set_part {$(FPGA_PART)}" >> $@
	@echo "create_clock -period $(CLOCK_PERIOD) -name default" >> $@
	@echo "csim_design" >> $@
	@echo "csynth_design" >> $@
	@echo "exit" >> $@
	@echo "Generated $@"

run_dgate_synth.tcl:
	@echo "# D-Gate+ Synthesis Script" > $@
	@echo "open_project dgate_project" >> $@
	@echo "set_top dgate_fsm_engine" >> $@
	@echo "add_files $(CURDIR)/dgate_fsm.cpp" >> $@
	@echo "add_files -tb $(CURDIR)/dgate_fsm_tb.cpp" >> $@
	@echo "open_solution solution1" >> $@
	@echo "set_part {$(FPGA_PART)}" >> $@
	@echo "create_clock -period $(CLOCK_PERIOD) -name default" >> $@
	@echo "csim_design" >> $@
	@echo "csynth_design" >> $@
	@echo "exit" >> $@
	@echo "Generated $@"

################################################################################
# Utility Targets
################################################################################

clean:
	rm -rf $(BUILD_DIR)
	rm -f run_*.tcl
	rm -f *.log *.jou
	rm -rf vitis_hls.log vivado*.log
	@echo "Cleaned build artifacts"

# Help
help:
	@echo "Portfolio B HLS Build System"
	@echo ""
	@echo "Targets:"
	@echo "  make all       - Build all testbenches"
	@echo "  make csim      - Run C simulation (no Vivado needed)"
	@echo "  make synth     - Synthesize to RTL (requires Vivado HLS)"
	@echo "  make cosim     - Run C/RTL co-simulation"
	@echo "  make export    - Export IP cores for Vivado integration"
	@echo "  make clean     - Remove build artifacts"
	@echo ""
	@echo "Environment Variables:"
	@echo "  XILINX_HLS     - Path to Vivado/Vitis HLS installation"
	@echo "  FPGA_PART      - Target FPGA part (default: $(FPGA_PART))"
	@echo "  CLOCK_PERIOD   - Target clock period in ns (default: $(CLOCK_PERIOD))"

################################################################################
# Report Generation
################################################################################

.PHONY: report

report:
	@echo "Generating synthesis report..."
	@if [ -f $(SYNTH_DIR)/arc3/solution1/syn/report/arc3_csi_correlator_csynth.rpt ]; then \
		echo "=== ARC-3 CSI Correlator Report ===" ; \
		cat $(SYNTH_DIR)/arc3/solution1/syn/report/arc3_csi_correlator_csynth.rpt | \
			grep -A20 "== Performance Estimates" ; \
	else \
		echo "Run 'make synth' first to generate reports" ; \
	fi
	@if [ -f $(SYNTH_DIR)/dgate/solution1/syn/report/dgate_fsm_engine_csynth.rpt ]; then \
		echo "=== D-Gate+ FSM Report ===" ; \
		cat $(SYNTH_DIR)/dgate/solution1/syn/report/dgate_fsm_engine_csynth.rpt | \
			grep -A20 "== Performance Estimates" ; \
	fi


