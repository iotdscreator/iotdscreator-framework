import os, sys, logging
import pathlib
fpath = pathlib.Path(__file__).parent.resolve()
root_directory = os.path.abspath("{}/..".format(fpath))
if root_directory not in sys.path:
    sys.path.insert(0, root_directory)
from features.packet.is_ack import IsAck
from features.packet.destination_mac_address import DestinationMacAddress
from features.packet.acknowledge_number import AcknowledgeNumber
from features.packet.is_rst import IsRst
from features.packet.is_cwr import IsCwr
from features.packet.is_fin import IsFin
from features.packet.total_ip_packet_length import TotalIpPacketLength
from features.packet.window_size import WindowSize
from features.packet.network_protocol import NetworkProtocol
from features.packet.is_psh import IsPsh
from features.packet.is_syn import IsSyn
from features.packet.is_urg import IsUrg
from features.packet.transport_protocol import TransportProtocol
from features.packet.ttl import Ttl
from features.packet.ip_identifier import IpIdentifier
from features.packet.sequence_number import SequenceNumber
from features.packet.is_ece import IsEce
from features.packet.source_mac_address import SourceMacAddress
from features.flow.flow_iat_std import FlowIatStd
from features.flow.forward_packet_length_max import ForwardPacketLengthMax
from features.flow.total_bhlen import TotalBhlen
from features.flow.flow_protocol import FlowProtocol
from features.flow.bpkts_per_second import BpktsPerSecond
from features.flow.flow_iat_total import FlowIatTotal
from features.flow.forward_iat_max import ForwardIatMax
from features.flow.flow_iat_mean import FlowIatMean
from features.flow.forward_packet_length_mean import ForwardPacketLengthMean
from features.flow.fpkts_per_second import FpktsPerSecond
from features.flow.flow_packets_per_second import FlowPacketsPerSecond
from features.flow.forward_iat_total import ForwardIatTotal
from features.flow.forward_packet_length_std import ForwardPacketLengthStd
from features.flow.total_fhlen import TotalFhlen
from features.flow.forward_iat_min import ForwardIatMin
from features.flow.backward_iat_std import BackwardIatStd
from features.flow.backward_packet_length_mean import BackwardPacketLengthMean
from features.flow.backward_iat_total import BackwardIatTotal
from features.flow.total_forward_packets import TotalForwardPackets
from features.flow.backward_packet_length_std import BackwardPacketLengthStd
from features.flow.backward_packet_length_min import BackwardPacketLengthMin
from features.flow.flow_ece import FlowEce
from features.flow.forward_packet_length_min import ForwardPacketLengthMin
from features.flow.flow_cwr import FlowCwr
from features.flow.flow_rst import FlowRst
from features.flow.backward_iat_mean import BackwardIatMean
from features.flow.flow_urg import FlowUrg
from features.flow.flow_psh import FlowPsh
from features.flow.forward_iat_std import ForwardIatStd
from features.flow.total_length_of_forward_packets import TotalLengthOfForwardPackets
from features.flow.backward_packet_length_max import BackwardPacketLengthMax
from features.flow.forward_iat_mean import ForwardIatMean
from features.flow.total_length_of_backward_packets import TotalLengthOfBackwardPackets
from features.flow.total_backward_packets import TotalBackwardPackets
from features.flow.flow_fin import FlowFin
from features.flow.flow_ack import FlowAck
from features.flow.flow_syn import FlowSyn
from features.flow.backward_iat_min import BackwardIatMin
from features.flow.flow_iat_min import FlowIatMin
from features.flow.backward_iat_max import BackwardIatMax
from features.flow.flow_iat_max import FlowIatMax
from features.host.cpu_running_time_on_user_mode import CpuRunningTimeOnUserMode
from features.host.total_swap_space_megabytes import TotalSwapSpaceMegabytes
from features.host.filesystem_metadata import FilesystemMetadata
from features.host.page_cache_megabytes import PageCacheMegabytes
from features.host.current_vm_space_megabytes import CurrentVmSpaceMegabytes
from features.host.number_of_received_icmp_datagrams import NumberOfReceivedIcmpDatagrams
from features.host.number_of_retransmission import NumberOfRetransmission
from features.host.disk_busy_time import DiskBusyTime
from features.host.number_of_active_tcp_open import NumberOfActiveTcpOpen
from features.host.cpu_utilization_on_interrupt_handling import CpuUtilizationOnInterruptHandling
from features.host.total_memory_megabytes import TotalMemoryMegabytes
from features.host.sleeping_uninterruptible import SleepingUninterruptible
from features.host.number_of_received_udp_datagrams import NumberOfReceivedUdpDatagrams
from features.host.number_of_context_switching import NumberOfContextSwitching
from features.host.number_of_passive_tcp_open import NumberOfPassiveTcpOpen
from features.host.cpu_load_average_per_15_minutes import CpuLoadAveragePer15Minutes
from features.host.number_of_transmitted_tcp_segments import NumberOfTransmittedTcpSegments
from features.host.cpu_waiting_time_percentage import CpuWaitingTimePercentage
from features.host.number_of_transmitted_icmp_datagrams import NumberOfTransmittedIcmpDatagrams
from features.host.number_of_open_processes import NumberOfOpenProcesses
from features.host.read_request_throughput import ReadRequestThroughput
from features.host.total_free_memory_megabytes import TotalFreeMemoryMegabytes
from features.host.cpu_load_average_per_minute import CpuLoadAveragePerMinute
from features.host.number_of_running_threads import NumberOfRunningThreads
from features.host.free_swap_space_megabytes import FreeSwapSpaceMegabytes
from features.host.clone_system_call import CloneSystemCall
from features.host.number_of_exit_processes import NumberOfExitProcesses
from features.host.maximum_vm_space_megabytes import MaximumVmSpaceMegabytes
from features.host.cpu_load_average_per_5_minutes import CpuLoadAveragePer5Minutes
from features.host.cpu_running_time_on_system_mode import CpuRunningTimeOnSystemMode
from features.host.cpu_idle_time_percentage import CpuIdleTimePercentage
from features.host.number_of_zombie_processes import NumberOfZombieProcesses
from features.host.number_of_transmitted_udp_datagrams import NumberOfTransmittedUdpDatagrams
from features.host.number_of_received_tcp_segments import NumberOfReceivedTcpSegments
from features.host.kernel_malloc import KernelMalloc
from features.host.cpu_stolen_time_percentage import CpuStolenTimePercentage
from features.host.cpu_utilization_on_kernel_mode import CpuUtilizationOnKernelMode
from features.host.write_request_throughput import WriteRequestThroughput
from features.host.cpu_utilization_on_user_mode import CpuUtilizationOnUserMode
from features.host.number_of_interrupt import NumberOfInterrupt
from features.transition.mean_number_of_received_udp_datagrams import MeanNumberOfReceivedUdpDatagrams
from features.transition.min_number_of_transmitted_tcp_segments import MinNumberOfTransmittedTcpSegments
from features.transition.max_number_of_transmitted_icmp_datagrams import MaxNumberOfTransmittedIcmpDatagrams
from features.transition.max_number_of_received_udp_datagrams import MaxNumberOfReceivedUdpDatagrams
from features.transition.min_kernel_malloc import MinKernelMalloc
from features.transition.max_total_swap_space_megabytes import MaxTotalSwapSpaceMegabytes
from features.transition.min_number_of_transmitted_icmp_datagrams import MinNumberOfTransmittedIcmpDatagrams
from features.transition.max_number_of_transmitted_udp_datagrams import MaxNumberOfTransmittedUdpDatagrams
from features.transition.min_number_of_transmitted_udp_datagrams import MinNumberOfTransmittedUdpDatagrams
from features.transition.mean_number_of_transmitted_icmp_datagrams import MeanNumberOfTransmittedIcmpDatagrams
from features.transition.max_number_of_received_tcp_segments import MaxNumberOfReceivedTcpSegments
from features.transition.mean_cpu_utilization_on_user_mode import MeanCpuUtilizationOnUserMode
from features.transition.mean_number_of_received_tcp_segments import MeanNumberOfReceivedTcpSegments
from features.transition.mean_sleeping_uninterruptible import MeanSleepingUninterruptible
from features.transition.min_total_free_memory_megabytes import MinTotalFreeMemoryMegabytes
from features.transition.min_cpu_idle_time_percentage import MinCpuIdleTimePercentage
from features.transition.max_total_free_memory_megabytes import MaxTotalFreeMemoryMegabytes
from features.transition.min_sleeping_uninterruptible import MinSleepingUninterruptible
from features.transition.min_number_of_zombie_processes import MinNumberOfZombieProcesses
from features.transition.mean_cpu_utilization_on_kernel_mode import MeanCpuUtilizationOnKernelMode
from features.transition.min_total_swap_space_megabytes import MinTotalSwapSpaceMegabytes
from features.transition.mean_number_of_transmitted_udp_datagrams import MeanNumberOfTransmittedUdpDatagrams
from features.transition.mean_cpu_idle_time_percentage import MeanCpuIdleTimePercentage
from features.transition.max_number_of_open_processes import MaxNumberOfOpenProcesses
from features.transition.min_write_request_throughput import MinWriteRequestThroughput
from features.transition.min_read_request_throughput import MinReadRequestThroughput
from features.transition.mean_cpu_running_time_on_user_mode import MeanCpuRunningTimeOnUserMode
from features.transition.min_cpu_running_time_on_user_mode import MinCpuRunningTimeOnUserMode
from features.transition.max_sleeping_uninterruptible import MaxSleepingUninterruptible
from features.transition.max_cpu_utilization_on_user_mode import MaxCpuUtilizationOnUserMode
from features.transition.max_number_of_exit_processes import MaxNumberOfExitProcesses
from features.transition.max_number_of_running_threads import MaxNumberOfRunningThreads
from features.transition.max_cpu_idle_time_percentage import MaxCpuIdleTimePercentage
from features.transition.max_write_request_throughput import MaxWriteRequestThroughput
from features.transition.min_cpu_utilization_on_kernel_mode import MinCpuUtilizationOnKernelMode
from features.transition.mean_number_of_received_icmp_datagrams import MeanNumberOfReceivedIcmpDatagrams
from features.transition.max_read_request_throughput import MaxReadRequestThroughput
from features.transition.mean_total_memory_megabytes import MeanTotalMemoryMegabytes
from features.transition.max_number_of_received_icmp_datagrams import MaxNumberOfReceivedIcmpDatagrams
from features.transition.mean_number_of_zombie_processes import MeanNumberOfZombieProcesses
from features.transition.min_number_of_running_threads import MinNumberOfRunningThreads
from features.transition.min_total_memory_megabytes import MinTotalMemoryMegabytes
from features.transition.mean_number_of_transmitted_tcp_segments import MeanNumberOfTransmittedTcpSegments
from features.transition.max_cpu_running_time_on_user_mode import MaxCpuRunningTimeOnUserMode
from features.transition.min_cpu_running_time_on_system_mode import MinCpuRunningTimeOnSystemMode
from features.transition.min_cpu_utilization_on_user_mode import MinCpuUtilizationOnUserMode
from features.transition.max_cpu_running_time_on_system_mode import MaxCpuRunningTimeOnSystemMode
from features.transition.max_cpu_utilization_on_kernel_mode import MaxCpuUtilizationOnKernelMode
from features.transition.mean_number_of_exit_processes import MeanNumberOfExitProcesses
from features.transition.mean_total_swap_space_megabytes import MeanTotalSwapSpaceMegabytes
from features.transition.mean_number_of_open_processes import MeanNumberOfOpenProcesses
from features.transition.min_number_of_received_udp_datagrams import MinNumberOfReceivedUdpDatagrams
from features.transition.mean_kernel_malloc import MeanKernelMalloc
from features.transition.mean_read_request_throughput import MeanReadRequestThroughput
from features.transition.max_number_of_transmitted_tcp_segments import MaxNumberOfTransmittedTcpSegments
from features.transition.max_number_of_zombie_processes import MaxNumberOfZombieProcesses
from features.transition.mean_cpu_running_time_on_system_mode import MeanCpuRunningTimeOnSystemMode
from features.transition.min_number_of_received_tcp_segments import MinNumberOfReceivedTcpSegments
from features.transition.min_number_of_received_icmp_datagrams import MinNumberOfReceivedIcmpDatagrams
from features.transition.min_number_of_exit_processes import MinNumberOfExitProcesses
from features.transition.max_kernel_malloc import MaxKernelMalloc
from features.transition.mean_total_free_memory_megabytes import MeanTotalFreeMemoryMegabytes
from features.transition.max_total_memory_megabytes import MaxTotalMemoryMegabytes
from features.transition.mean_write_request_throughput import MeanWriteRequestThroughput
from features.transition.mean_number_of_running_threads import MeanNumberOfRunningThreads
from features.transition.min_number_of_open_processes import MinNumberOfOpenProcesses

def init_packet_features(feature_extractor):
    feature_extractor.add_feature(IsAck("is_ack"))
    feature_extractor.add_feature(DestinationMacAddress("destination_mac_address"))
    feature_extractor.add_feature(AcknowledgeNumber("acknowledge_number"))
    feature_extractor.add_feature(IsRst("is_rst"))
    feature_extractor.add_feature(IsCwr("is_cwr"))
    feature_extractor.add_feature(IsFin("is_fin"))
    feature_extractor.add_feature(TotalIpPacketLength("total_ip_packet_length"))
    feature_extractor.add_feature(WindowSize("window_size"))
    feature_extractor.add_feature(NetworkProtocol("network_protocol"))
    feature_extractor.add_feature(IsPsh("is_psh"))
    feature_extractor.add_feature(IsSyn("is_syn"))
    feature_extractor.add_feature(IsUrg("is_urg"))
    feature_extractor.add_feature(TransportProtocol("transport_protocol"))
    feature_extractor.add_feature(Ttl("ttl"))
    feature_extractor.add_feature(IpIdentifier("ip_identifier"))
    feature_extractor.add_feature(SequenceNumber("sequence_number"))
    feature_extractor.add_feature(IsEce("is_ece"))
    feature_extractor.add_feature(SourceMacAddress("source_mac_address"))

def init_flow_features(feature_extractor):
    feature_extractor.add_feature(FlowIatStd("flow_iat_std"))
    feature_extractor.add_feature(ForwardPacketLengthMax("forward_packet_length_max"))
    feature_extractor.add_feature(TotalBhlen("total_bhlen"))
    feature_extractor.add_feature(FlowProtocol("flow_protocol"))
    feature_extractor.add_feature(BpktsPerSecond("bpkts_per_second"))
    feature_extractor.add_feature(FlowIatTotal("flow_iat_total"))
    feature_extractor.add_feature(ForwardIatMax("forward_iat_max"))
    feature_extractor.add_feature(FlowIatMean("flow_iat_mean"))
    feature_extractor.add_feature(ForwardPacketLengthMean("forward_packet_length_mean"))
    feature_extractor.add_feature(FpktsPerSecond("fpkts_per_second"))
    feature_extractor.add_feature(FlowPacketsPerSecond("flow_packets_per_second"))
    feature_extractor.add_feature(ForwardIatTotal("forward_iat_total"))
    feature_extractor.add_feature(ForwardPacketLengthStd("forward_packet_length_std"))
    feature_extractor.add_feature(TotalFhlen("total_fhlen"))
    feature_extractor.add_feature(ForwardIatMin("forward_iat_min"))
    feature_extractor.add_feature(BackwardIatStd("backward_iat_std"))
    feature_extractor.add_feature(BackwardPacketLengthMean("backward_packet_length_mean"))
    feature_extractor.add_feature(BackwardIatTotal("backward_iat_total"))
    feature_extractor.add_feature(TotalForwardPackets("total_forward_packets"))
    feature_extractor.add_feature(BackwardPacketLengthStd("backward_packet_length_std"))
    feature_extractor.add_feature(BackwardPacketLengthMin("backward_packet_length_min"))
    feature_extractor.add_feature(FlowEce("flow_ece"))
    feature_extractor.add_feature(ForwardPacketLengthMin("forward_packet_length_min"))
    feature_extractor.add_feature(FlowCwr("flow_cwr"))
    feature_extractor.add_feature(FlowRst("flow_rst"))
    feature_extractor.add_feature(BackwardIatMean("backward_iat_mean"))
    feature_extractor.add_feature(FlowUrg("flow_urg"))
    feature_extractor.add_feature(FlowPsh("flow_psh"))
    feature_extractor.add_feature(ForwardIatStd("forward_iat_std"))
    feature_extractor.add_feature(TotalLengthOfForwardPackets("total_length_of_forward_packets"))
    feature_extractor.add_feature(BackwardPacketLengthMax("backward_packet_length_max"))
    feature_extractor.add_feature(ForwardIatMean("forward_iat_mean"))
    feature_extractor.add_feature(TotalLengthOfBackwardPackets("total_length_of_backward_packets"))
    feature_extractor.add_feature(TotalBackwardPackets("total_backward_packets"))
    feature_extractor.add_feature(FlowFin("flow_fin"))
    feature_extractor.add_feature(FlowAck("flow_ack"))
    feature_extractor.add_feature(FlowSyn("flow_syn"))
    feature_extractor.add_feature(BackwardIatMin("backward_iat_min"))
    feature_extractor.add_feature(FlowIatMin("flow_iat_min"))
    feature_extractor.add_feature(BackwardIatMax("backward_iat_max"))
    feature_extractor.add_feature(FlowIatMax("flow_iat_max"))

def init_host_features(feature_extractor):
    feature_extractor.add_feature(CpuRunningTimeOnUserMode("cpu_running_time_on_user_mode"))
    feature_extractor.add_feature(TotalSwapSpaceMegabytes("total_swap_space_megabytes"))
    feature_extractor.add_feature(FilesystemMetadata("filesystem_metadata"))
    feature_extractor.add_feature(PageCacheMegabytes("page_cache_megabytes"))
    feature_extractor.add_feature(CurrentVmSpaceMegabytes("current_vm_space_megabytes"))
    feature_extractor.add_feature(NumberOfReceivedIcmpDatagrams("number_of_received_icmp_datagrams"))
    feature_extractor.add_feature(NumberOfRetransmission("number_of_retransmission"))
    feature_extractor.add_feature(DiskBusyTime("disk_busy_time"))
    feature_extractor.add_feature(NumberOfActiveTcpOpen("number_of_active_tcp_open"))
    feature_extractor.add_feature(CpuUtilizationOnInterruptHandling("cpu_utilization_on_interrupt_handling"))
    feature_extractor.add_feature(TotalMemoryMegabytes("total_memory_megabytes"))
    feature_extractor.add_feature(SleepingUninterruptible("sleeping_uninterruptible"))
    feature_extractor.add_feature(NumberOfReceivedUdpDatagrams("number_of_received_udp_datagrams"))
    feature_extractor.add_feature(NumberOfContextSwitching("number_of_context_switching"))
    feature_extractor.add_feature(NumberOfPassiveTcpOpen("number_of_passive_tcp_open"))
    feature_extractor.add_feature(CpuLoadAveragePer15Minutes("cpu_load_average_per_15_minutes"))
    feature_extractor.add_feature(NumberOfTransmittedTcpSegments("number_of_transmitted_tcp_segments"))
    feature_extractor.add_feature(CpuWaitingTimePercentage("cpu_waiting_time_percentage"))
    feature_extractor.add_feature(NumberOfTransmittedIcmpDatagrams("number_of_transmitted_icmp_datagrams"))
    feature_extractor.add_feature(NumberOfOpenProcesses("number_of_open_processes"))
    feature_extractor.add_feature(ReadRequestThroughput("read_request_throughput"))
    feature_extractor.add_feature(TotalFreeMemoryMegabytes("total_free_memory_megabytes"))
    feature_extractor.add_feature(CpuLoadAveragePerMinute("cpu_load_average_per_minute"))
    feature_extractor.add_feature(NumberOfRunningThreads("number_of_running_threads"))
    feature_extractor.add_feature(FreeSwapSpaceMegabytes("free_swap_space_megabytes"))
    feature_extractor.add_feature(CloneSystemCall("clone_system_call"))
    feature_extractor.add_feature(NumberOfExitProcesses("number_of_exit_processes"))
    feature_extractor.add_feature(MaximumVmSpaceMegabytes("maximum_vm_space_megabytes"))
    feature_extractor.add_feature(CpuLoadAveragePer5Minutes("cpu_load_average_per_5_minutes"))
    feature_extractor.add_feature(CpuRunningTimeOnSystemMode("cpu_running_time_on_system_mode"))
    feature_extractor.add_feature(CpuIdleTimePercentage("cpu_idle_time_percentage"))
    feature_extractor.add_feature(NumberOfZombieProcesses("number_of_zombie_processes"))
    feature_extractor.add_feature(NumberOfTransmittedUdpDatagrams("number_of_transmitted_udp_datagrams"))
    feature_extractor.add_feature(NumberOfReceivedTcpSegments("number_of_received_tcp_segments"))
    feature_extractor.add_feature(KernelMalloc("kernel_malloc"))
    feature_extractor.add_feature(CpuStolenTimePercentage("cpu_stolen_time_percentage"))
    feature_extractor.add_feature(CpuUtilizationOnKernelMode("cpu_utilization_on_kernel_mode"))
    feature_extractor.add_feature(WriteRequestThroughput("write_request_throughput"))
    feature_extractor.add_feature(CpuUtilizationOnUserMode("cpu_utilization_on_user_mode"))
    feature_extractor.add_feature(NumberOfInterrupt("number_of_interrupt"))

def init_transition_features(feature_extractor):
    feature_extractor.add_feature(MeanNumberOfReceivedUdpDatagrams("mean_number_of_received_udp_datagrams"))
    feature_extractor.add_feature(MinNumberOfTransmittedTcpSegments("min_number_of_transmitted_tcp_segments"))
    feature_extractor.add_feature(MaxNumberOfTransmittedIcmpDatagrams("max_number_of_transmitted_icmp_datagrams"))
    feature_extractor.add_feature(MaxNumberOfReceivedUdpDatagrams("max_number_of_received_udp_datagrams"))
    feature_extractor.add_feature(MinKernelMalloc("min_kernel_malloc"))
    feature_extractor.add_feature(MaxTotalSwapSpaceMegabytes("max_total_swap_space_megabytes"))
    feature_extractor.add_feature(MinNumberOfTransmittedIcmpDatagrams("min_number_of_transmitted_icmp_datagrams"))
    feature_extractor.add_feature(MaxNumberOfTransmittedUdpDatagrams("max_number_of_transmitted_udp_datagrams"))
    feature_extractor.add_feature(MinNumberOfTransmittedUdpDatagrams("min_number_of_transmitted_udp_datagrams"))
    feature_extractor.add_feature(MeanNumberOfTransmittedIcmpDatagrams("mean_number_of_transmitted_icmp_datagrams"))
    feature_extractor.add_feature(MaxNumberOfReceivedTcpSegments("max_number_of_received_tcp_segments"))
    feature_extractor.add_feature(MeanCpuUtilizationOnUserMode("mean_cpu_utilization_on_user_mode"))
    feature_extractor.add_feature(MeanNumberOfReceivedTcpSegments("mean_number_of_received_tcp_segments"))
    feature_extractor.add_feature(MeanSleepingUninterruptible("mean_sleeping_uninterruptible"))
    feature_extractor.add_feature(MinTotalFreeMemoryMegabytes("min_total_free_memory_megabytes"))
    feature_extractor.add_feature(MinCpuIdleTimePercentage("min_cpu_idle_time_percentage"))
    feature_extractor.add_feature(MaxTotalFreeMemoryMegabytes("max_total_free_memory_megabytes"))
    feature_extractor.add_feature(MinSleepingUninterruptible("min_sleeping_uninterruptible"))
    feature_extractor.add_feature(MinNumberOfZombieProcesses("min_number_of_zombie_processes"))
    feature_extractor.add_feature(MeanCpuUtilizationOnKernelMode("mean_cpu_utilization_on_kernel_mode"))
    feature_extractor.add_feature(MinTotalSwapSpaceMegabytes("min_total_swap_space_megabytes"))
    feature_extractor.add_feature(MeanNumberOfTransmittedUdpDatagrams("mean_number_of_transmitted_udp_datagrams"))
    feature_extractor.add_feature(MeanCpuIdleTimePercentage("mean_cpu_idle_time_percentage"))
    feature_extractor.add_feature(MaxNumberOfOpenProcesses("max_number_of_open_processes"))
    feature_extractor.add_feature(MinWriteRequestThroughput("min_write_request_throughput"))
    feature_extractor.add_feature(MinReadRequestThroughput("min_read_request_throughput"))
    feature_extractor.add_feature(MeanCpuRunningTimeOnUserMode("mean_cpu_running_time_on_user_mode"))
    feature_extractor.add_feature(MinCpuRunningTimeOnUserMode("min_cpu_running_time_on_user_mode"))
    feature_extractor.add_feature(MaxSleepingUninterruptible("max_sleeping_uninterruptible"))
    feature_extractor.add_feature(MaxCpuUtilizationOnUserMode("max_cpu_utilization_on_user_mode"))
    feature_extractor.add_feature(MaxNumberOfExitProcesses("max_number_of_exit_processes"))
    feature_extractor.add_feature(MaxNumberOfRunningThreads("max_number_of_running_threads"))
    feature_extractor.add_feature(MaxCpuIdleTimePercentage("max_cpu_idle_time_percentage"))
    feature_extractor.add_feature(MaxWriteRequestThroughput("max_write_request_throughput"))
    feature_extractor.add_feature(MinCpuUtilizationOnKernelMode("min_cpu_utilization_on_kernel_mode"))
    feature_extractor.add_feature(MeanNumberOfReceivedIcmpDatagrams("mean_number_of_received_icmp_datagrams"))
    feature_extractor.add_feature(MaxReadRequestThroughput("max_read_request_throughput"))
    feature_extractor.add_feature(MeanTotalMemoryMegabytes("mean_total_memory_megabytes"))
    feature_extractor.add_feature(MaxNumberOfReceivedIcmpDatagrams("max_number_of_received_icmp_datagrams"))
    feature_extractor.add_feature(MeanNumberOfZombieProcesses("mean_number_of_zombie_processes"))
    feature_extractor.add_feature(MinNumberOfRunningThreads("min_number_of_running_threads"))
    feature_extractor.add_feature(MinTotalMemoryMegabytes("min_total_memory_megabytes"))
    feature_extractor.add_feature(MeanNumberOfTransmittedTcpSegments("mean_number_of_transmitted_tcp_segments"))
    feature_extractor.add_feature(MaxCpuRunningTimeOnUserMode("max_cpu_running_time_on_user_mode"))
    feature_extractor.add_feature(MinCpuRunningTimeOnSystemMode("min_cpu_running_time_on_system_mode"))
    feature_extractor.add_feature(MinCpuUtilizationOnUserMode("min_cpu_utilization_on_user_mode"))
    feature_extractor.add_feature(MaxCpuRunningTimeOnSystemMode("max_cpu_running_time_on_system_mode"))
    feature_extractor.add_feature(MaxCpuUtilizationOnKernelMode("max_cpu_utilization_on_kernel_mode"))
    feature_extractor.add_feature(MeanNumberOfExitProcesses("mean_number_of_exit_processes"))
    feature_extractor.add_feature(MeanTotalSwapSpaceMegabytes("mean_total_swap_space_megabytes"))
    feature_extractor.add_feature(MeanNumberOfOpenProcesses("mean_number_of_open_processes"))
    feature_extractor.add_feature(MinNumberOfReceivedUdpDatagrams("min_number_of_received_udp_datagrams"))
    feature_extractor.add_feature(MeanKernelMalloc("mean_kernel_malloc"))
    feature_extractor.add_feature(MeanReadRequestThroughput("mean_read_request_throughput"))
    feature_extractor.add_feature(MaxNumberOfTransmittedTcpSegments("max_number_of_transmitted_tcp_segments"))
    feature_extractor.add_feature(MaxNumberOfZombieProcesses("max_number_of_zombie_processes"))
    feature_extractor.add_feature(MeanCpuRunningTimeOnSystemMode("mean_cpu_running_time_on_system_mode"))
    feature_extractor.add_feature(MinNumberOfReceivedTcpSegments("min_number_of_received_tcp_segments"))
    feature_extractor.add_feature(MinNumberOfReceivedIcmpDatagrams("min_number_of_received_icmp_datagrams"))
    feature_extractor.add_feature(MinNumberOfExitProcesses("min_number_of_exit_processes"))
    feature_extractor.add_feature(MaxKernelMalloc("max_kernel_malloc"))
    feature_extractor.add_feature(MeanTotalFreeMemoryMegabytes("mean_total_free_memory_megabytes"))
    feature_extractor.add_feature(MaxTotalMemoryMegabytes("max_total_memory_megabytes"))
    feature_extractor.add_feature(MeanWriteRequestThroughput("mean_write_request_throughput"))
    feature_extractor.add_feature(MeanNumberOfRunningThreads("mean_number_of_running_threads"))
    feature_extractor.add_feature(MinNumberOfOpenProcesses("min_number_of_open_processes"))
