import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock

"""
Cocotb Testbench for AIPP-SH Sovereign Handshake Gate
Verifies nanosecond determinism and adversarial rejection.
"""

@cocotb.test()
async def test_deterministic_latency(dut):
    """Prove that the authorization signal fires in exactly 8ns."""
    
    # Start 1GHz clock (1ns period)
    clock = Clock(dut.clk, 1, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    dut.s_axis_tvalid.value = 0
    dut.s_axis_tdata.value = 0
    dut.phy_csi_match.value = 0
    await Timer(5, unit="ns")
    dut.rst_n.value = 1
    
    # Wait for a clean rising edge to start
    await RisingEdge(dut.clk)

    # Inject Legitimate Packet
    permit_tag = 0xA1BB50CCAA0055AA
    dut.s_axis_tdata.value = permit_tag
    dut.s_axis_tvalid.value = 1
    dut.phy_csi_match.value = 1
    
    # The data is sampled at the NEXT rising edge
    await RisingEdge(dut.clk)
    sample_time = cocotb.utils.get_sim_time(unit="ns")
    dut._log.info(f"Permit Sampled at {sample_time}ns")
    
    dut.s_axis_tvalid.value = 0 # Single pulse
    
    # Wait for auth_valid to go high
    while dut.auth_valid.value == 0:
        await RisingEdge(dut.clk)
        
    end_time = cocotb.utils.get_sim_time(unit="ns")
    latency = end_time - sample_time
    
    dut._log.info(f"Authorization Triggered at {end_time}ns")
    dut._log.info(f"Measured Latency (from sample): {latency}ns")
    
    # 8 stages means 8ns from the rising edge that samples the input
    # to the rising edge that updates the output observed by the testbench.
    
    assert latency == 8, f"Latency was {latency}ns, expected 8ns from sample (8 stages total)"
    dut._log.info("STATUS: ✅ DETERMINISTIC LATENCY PROVEN (8ns)")

@cocotb.test()
async def test_adversarial_rejection(dut):
    """Prove that an incorrect CSI or Permit results in a rejection signal."""
    
    # Start 1GHz clock
    clock = Clock(dut.clk, 1, unit="ns")
    cocotb.start_soon(clock.start())
    
    # Reset
    dut.rst_n.value = 0
    await Timer(5, unit="ns")
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # 1. Test Incorrect Permit Tag
    dut.s_axis_tdata.value = 0xBAD0DEBAD0DEBAD0
    dut.s_axis_tvalid.value = 1
    dut.phy_csi_match.value = 1
    await RisingEdge(dut.clk)
    dut.s_axis_tvalid.value = 0
    
    while dut.auth_reject.value == 0:
        await RisingEdge(dut.clk)
    
    assert dut.auth_reject.value == 1
    assert dut.auth_valid.value == 0
    dut._log.info("STATUS: ✅ INCORRECT PERMIT REJECTED")

    # 2. Test Incorrect CSI Match (Spoofer)
    dut.s_axis_tdata.value = 0xA1BB50CCAA0055AA
    dut.s_axis_tvalid.value = 1
    dut.phy_csi_match.value = 0 # No CSI Match
    await RisingEdge(dut.clk)
    dut.s_axis_tvalid.value = 0
    
    while dut.auth_reject.value == 0:
        await RisingEdge(dut.clk)
    
    assert dut.auth_reject.value == 1
    assert dut.auth_valid.value == 0
    dut._log.info("STATUS: ✅ CSI SPOOFER REJECTED")

