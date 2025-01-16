# Host Features
IoTDSCreator extracts 40 host features, described below. The direction ("forward" and "backward") is determined by the initial packet. The "forward" is the direction from a source address of the first packet to a destination address of the first packet. The "backward" is the opposite direction.

<table>
  <tr>
    <td align="center"><b>Name</b></td><td align="center"><b>Description</b></td>
  </tr>
  <tr>
    <td>clone_system_call</td><td>The number of clone system calls ('clones').</td>
  </tr>
  <tr>
    <td>cpu_idle_time_percentage</td><td>The percentage of the CPU idle time.</td>
  </tr>
  <tr>
    <td>cpu_load_average_per_15_minutes</td><td>The average load of the CPU per 15 minutes.</td>
  </tr>
  <tr>
    <td>cpu_load_average_per_5_minutes</td><td>The average load of the CPU per 5 minutes.</td>
  </tr>
  <tr>
    <td>cpu_load_average_per_minute</td><td>The average load of the CPU per minute.</td>
  </tr>
  <tr>
    <td>cpu_running_time_on_system_mode</td><td>The CPU running time in the system mode.</td>
  </tr>
  <tr>
    <td>cpu_running_time_on_user_mode</td><td>The CPU running time in the user mode.</td>
  </tr>
  <tr>
    <td>cpu_stolen_time_percentage</td><td>The percentage of the CPU stolen time.</td>
  </tr>
  <tr>
    <td>cpu_utilization_on_interrupt_handling</td><td>The CPU utilization when handling an interrupt.</td>
  </tr>
  <tr>
    <td>cpu_utilization_on_kernel_mode</td><td>The CPU utilization in the kernel mode.</td>
  </tr>
  <tr>
    <td>cpu_utilization_on_user_mode</td><td>The CPU utilization in the user mode.</td>
  </tr>
  <tr>
    <td>cpu_waiting_time_percentage</td><td>The percentage of the CPU waiting time.</td>
  </tr>
  <tr>
    <td>current_vm_space_megabytes</td><td>The current space used by VM in megabytes.</td>
  </tr>
  <tr>
    <td>disk_busy_time</td><td>The busy time of disk.</td>
  </tr>
  <tr>
    <td>filesystem_metadata</td><td>The metadata of the filesystem.</td>
  </tr>
  <tr>
    <td>free_swap_space_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>kernel_malloc</td><td>.</td>
  </tr>
  <tr>
    <td>maximum_vm_space_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_active_tcp_open</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_context_switching</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_exit_processes</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_interrupt</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_open_processes</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_passive_tcp_open</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_received_icmp_datagrams</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_received_tcp_segments</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_received_udp_datagrams</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_retransmission</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_running_threads</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_transmitted_icmp_datagrams</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_transmitted_tcp_segments</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_transmitted_udp_datagrams</td><td>.</td>
  </tr>
  <tr>
    <td>number_of_zombie_processes</td><td>.</td>
  </tr>
  <tr>
    <td>page_cache_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>read_request_throughput</td><td>.</td>
  </tr>
  <tr>
    <td>sleeping_uninterruptible</td><td>.</td>
  </tr>
  <tr>
    <td>total_free_memory_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>total_memory_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>total_swap_space_megabytes</td><td>.</td>
  </tr>
  <tr>
    <td>write_request_throughtput</td><td>.</td>
  </tr>
</table>
